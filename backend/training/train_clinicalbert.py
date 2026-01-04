"""
Fine-tune ClinicalBERT for Medical Text Classification/NER

Usage:
    python train_clinicalbert.py --data_dir ./data/medical_text --epochs 10 --task classification

Supported tasks:
    - classification: Medical text classification (diagnosis, symptoms, etc.)
    - ner: Named Entity Recognition for medical entities
    - qa: Question Answering for medical queries
"""
import os
import argparse
import torch
import torch.nn as nn
from torch.optim import AdamW
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    get_linear_schedule_with_warmup
)
# Simple metrics to avoid sklearn compatibility issues
def simple_accuracy(y_true, y_pred):
    return np.mean(y_true == y_pred)

def simple_f1(y_true, y_pred, average='macro'):
    # Simple F1 calculation
    unique_labels = np.unique(np.concatenate([y_true, y_pred]))
    f1_scores = []
    for label in unique_labels:
        tp = np.sum((y_true == label) & (y_pred == label))
        fp = np.sum((y_true != label) & (y_pred == label))
        fn = np.sum((y_true == label) & (y_pred != label))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        f1_scores.append(f1)
    
    return np.mean(f1_scores) if average == 'macro' else f1_scores

def simple_classification_report(y_true, y_pred, target_names=None):
    unique_labels = np.unique(np.concatenate([y_true, y_pred]))
    report = {}
    
    for i, label in enumerate(unique_labels):
        tp = np.sum((y_true == label) & (y_pred == label))
        fp = np.sum((y_true != label) & (y_pred == label))
        fn = np.sum((y_true == label) & (y_pred != label))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        label_name = target_names[i] if target_names and i < len(target_names) else str(label)
        report[label_name] = {
            'precision': precision,
            'recall': recall,
            'f1-score': f1
        }
    
    return report
from tqdm import tqdm
import numpy as np
import json
from datetime import datetime

from config import ClinicalBERTConfig, MEDICAL_TEXT_LABELS
from datasets import MedicalTextDataset


def train_epoch(model, train_loader, optimizer, scheduler, device, epoch, config):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    all_preds = []
    all_labels = []
    
    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{config.num_epochs}")
    
    for batch_idx, batch in enumerate(pbar):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        optimizer.zero_grad()
        
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        
        loss = outputs.loss
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        
        optimizer.step()
        scheduler.step()
        
        total_loss += loss.item()
        
        # Store predictions
        preds = torch.argmax(outputs.logits, dim=-1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().numpy())
        
        pbar.set_postfix({'loss': f'{loss.item():.4f}'})
    
    avg_loss = total_loss / len(train_loader)
    accuracy = simple_accuracy(all_labels, all_preds)
    f1 = simple_f1(all_labels, all_preds, average='macro')
    
    return avg_loss, accuracy, f1


def validate(model, val_loader, device, label_names=None):
    """Validate the model"""
    model.eval()
    total_loss = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in tqdm(val_loader, desc="Validating"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            total_loss += outputs.loss.item()
            
            preds = torch.argmax(outputs.logits, dim=-1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())
    
    avg_loss = total_loss / len(val_loader)
    accuracy = simple_accuracy(all_labels, all_preds)
    f1 = simple_f1(all_labels, all_preds, average='macro')
    
    # Classification report
    report = simple_classification_report(
        all_labels, all_preds,
        target_names=label_names
    )
    
    return avg_loss, accuracy, f1, report


def train_model(config: ClinicalBERTConfig):
    """
    Main training function for ClinicalBERT
    """
    print("="*60)
    print("ClinicalBERT Medical Text Fine-tuning")
    print("="*60)
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create directories
    os.makedirs(config.checkpoint_dir, exist_ok=True)
    os.makedirs(config.model_save_path, exist_ok=True)
    
    # Load tokenizer
    print(f"\nLoading tokenizer: {config.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    
    # Create datasets
    print("\nLoading datasets...")
    train_dataset = MedicalTextDataset(
        config.train_data_path,
        tokenizer,
        config.max_seq_length
    )
    val_dataset = MedicalTextDataset(
        config.val_data_path,
        tokenizer,
        config.max_seq_length,
        label_map=train_dataset.label_map
    )
    test_dataset = MedicalTextDataset(
        config.test_data_path,
        tokenizer,
        config.max_seq_length,
        label_map=train_dataset.label_map
    )
    
    # Get label names
    label_names = list(train_dataset.label_map.keys())
    num_labels = len(label_names)
    print(f"Number of labels: {num_labels}")
    print(f"Labels: {label_names}")
    
    # Create data loaders
    from torch.utils.data import DataLoader
    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=False)
    
    print(f"Train samples: {len(train_dataset)}")
    print(f"Val samples: {len(val_dataset)}")
    
    # Load model
    print(f"\nLoading model: {config.model_name}")
    model = AutoModelForSequenceClassification.from_pretrained(
        config.model_name,
        num_labels=num_labels
    )
    model = model.to(device)
    
    # Optimizer and scheduler
    optimizer = AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )
    
    total_steps = len(train_loader) * config.num_epochs
    warmup_steps = int(total_steps * config.warmup_ratio)
    
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps
    )
    
    # Training loop
    best_f1 = 0
    history = {
        'train_loss': [], 'val_loss': [],
        'train_acc': [], 'val_acc': [],
        'train_f1': [], 'val_f1': []
    }
    
    print("\nStarting training...")
    for epoch in range(config.num_epochs):
        # Train
        train_loss, train_acc, train_f1 = train_epoch(
            model, train_loader, optimizer, scheduler, device, epoch, config
        )
        
        # Validate
        val_loss, val_acc, val_f1, val_report = validate(
            model, val_loader, device, label_names
        )
        
        # Log metrics
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)
        history['train_f1'].append(train_f1)
        history['val_f1'].append(val_f1)
        
        print(f"\nEpoch {epoch+1}/{config.num_epochs}:")
        print(f"  Train - Loss: {train_loss:.4f}, Acc: {train_acc:.4f}, F1: {train_f1:.4f}")
        print(f"  Val   - Loss: {val_loss:.4f}, Acc: {val_acc:.4f}, F1: {val_f1:.4f}")
        
        # Save best model
        if val_f1 > best_f1:
            best_f1 = val_f1
            print(f"  New best F1! Saving model...")
            model.save_pretrained(config.model_save_path)
            tokenizer.save_pretrained(config.model_save_path)
            
            # Save label map
            with open(os.path.join(config.model_save_path, 'label_map.json'), 'w') as f:
                json.dump(train_dataset.label_map, f)
        
        # Save checkpoint
        checkpoint_path = os.path.join(
            config.checkpoint_dir,
            f'checkpoint_epoch_{epoch+1}'
        )
        model.save_pretrained(checkpoint_path)
    
    # Final evaluation on test set
    print("\n" + "="*60)
    print("Final Evaluation on Test Set")
    print("="*60)
    
    # Load best model
    model = AutoModelForSequenceClassification.from_pretrained(config.model_save_path)
    model = model.to(device)
    
    test_loss, test_acc, test_f1, test_report = validate(
        model, test_loader, device, label_names
    )
    
    print(f"\nTest Loss: {test_loss:.4f}")
    print(f"Test Accuracy: {test_acc:.4f}")
    print(f"Test F1 (macro): {test_f1:.4f}")
    print("\nClassification Report:")
    for label in label_names:
        metrics = test_report[label]
        print(f"  {label}: P={metrics['precision']:.3f}, R={metrics['recall']:.3f}, F1={metrics['f1-score']:.3f}")
    
    # Save training history
    history['test_acc'] = test_acc
    history['test_f1'] = test_f1
    history['test_report'] = test_report
    history_path = os.path.join(config.checkpoint_dir, 'training_history.json')
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"\nTraining complete! Model saved to: {config.model_save_path}")
    return model, tokenizer, history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune ClinicalBERT for medical text")
    parser.add_argument('--data_dir', type=str, default='./data/medical_text')
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=2e-5)
    parser.add_argument('--max_length', type=int, default=512)
    parser.add_argument('--task', type=str, default='classification', choices=['classification', 'ner'])
    parser.add_argument('--output_dir', type=str, default='./models/clinicalbert_finetuned')
    args = parser.parse_args()
    
    config = ClinicalBERTConfig(
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        max_seq_length=args.max_length,
        task_type=args.task,
        train_data_path=os.path.join(args.data_dir, 'train.csv'),
        val_data_path=os.path.join(args.data_dir, 'val.csv'),
        test_data_path=os.path.join(args.data_dir, 'test.csv'),
        model_save_path=args.output_dir
    )
    
    train_model(config)
