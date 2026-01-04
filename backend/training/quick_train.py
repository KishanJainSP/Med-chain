#!/usr/bin/env python3
"""
Quick Training Demo for Medical AI Models
Simplified version for fast demonstration
"""
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms
from torch.utils.data import DataLoader
import numpy as np
from tqdm import tqdm
import json
from datetime import datetime

from datasets import ChestXrayDataset, MedicalTextDataset
from config import EfficientNetConfig, ClinicalBERTConfig

def quick_train_efficientnet():
    """Quick EfficientNet training demo"""
    print("="*50)
    print("Quick EfficientNet Training Demo")
    print("="*50)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create a smaller model for demo
    model = models.efficientnet_b0(weights='IMAGENET1K_V1')
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(model.classifier[1].in_features, 14)
    )
    model = model.to(device)
    
    # Create small dataset
    dataset = ChestXrayDataset(
        './data/chest_xray',
        split='train',
        image_size=224,
        num_classes=14,
        augment=False
    )
    
    # Use only first 10 samples for quick demo
    subset_indices = list(range(min(10, len(dataset))))
    subset = torch.utils.data.Subset(dataset, subset_indices)
    
    dataloader = DataLoader(subset, batch_size=2, shuffle=True, num_workers=0)
    
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    print(f"Training on {len(subset)} samples...")
    
    # Quick training loop
    model.train()
    for epoch in range(2):
        total_loss = 0
        pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/2")
        
        for batch_idx, (images, labels) in enumerate(pbar):
            images = images.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1} - Average Loss: {avg_loss:.4f}")
    
    # Save model
    os.makedirs('./models', exist_ok=True)
    torch.save({
        'model_state_dict': model.state_dict(),
        'num_classes': 14,
        'model_type': 'efficientnet_b0'
    }, './models/efficientnet_medical_demo.pth')
    
    print("EfficientNet demo training complete!")
    print("Model saved to: ./models/efficientnet_medical_demo.pth")
    return model

def quick_train_clinicalbert():
    """Quick ClinicalBERT training demo"""
    print("\n" + "="*50)
    print("Quick ClinicalBERT Training Demo")
    print("="*50)
    
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        from transformers import AdamW
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {device}")
        
        # Load tokenizer and model
        model_name = "emilyalsentzer/Bio_ClinicalBERT"
        print(f"Loading {model_name}...")
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Create dataset
        dataset = MedicalTextDataset(
            './data/medical_text/train.csv',
            tokenizer,
            max_length=128
        )
        
        # Use only first 10 samples for quick demo
        subset_indices = list(range(min(10, len(dataset))))
        subset = torch.utils.data.Subset(dataset, subset_indices)
        
        dataloader = DataLoader(subset, batch_size=2, shuffle=True, num_workers=0)
        
        # Load model with correct number of labels
        num_labels = dataset.num_labels
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        )
        model = model.to(device)
        
        optimizer = AdamW(model.parameters(), lr=2e-5)
        
        print(f"Training on {len(subset)} samples with {num_labels} labels...")
        
        # Quick training loop
        model.train()
        for epoch in range(2):
            total_loss = 0
            pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/2")
            
            for batch in pbar:
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
                optimizer.step()
                
                total_loss += loss.item()
                pbar.set_postfix({'loss': f'{loss.item():.4f}'})
            
            avg_loss = total_loss / len(dataloader)
            print(f"Epoch {epoch+1} - Average Loss: {avg_loss:.4f}")
        
        # Save model
        os.makedirs('./models/clinicalbert_demo', exist_ok=True)
        model.save_pretrained('./models/clinicalbert_demo')
        tokenizer.save_pretrained('./models/clinicalbert_demo')
        
        # Save label mapping
        with open('./models/clinicalbert_demo/label_map.json', 'w') as f:
            json.dump(dataset.label_map, f)
        
        print("ClinicalBERT demo training complete!")
        print("Model saved to: ./models/clinicalbert_demo/")
        return model, tokenizer
        
    except ImportError as e:
        print(f"Transformers not available: {e}")
        return None, None

def main():
    """Run both training demos"""
    print("Starting Medical AI Model Fine-tuning Demo")
    print("This is a simplified version for quick demonstration")
    print("For full training, use the complete train_*.py scripts")
    
    # Train EfficientNet
    efficientnet_model = quick_train_efficientnet()
    
    # Train ClinicalBERT
    bert_model, tokenizer = quick_train_clinicalbert()
    
    # Summary
    print("\n" + "="*60)
    print("Training Demo Complete!")
    print("="*60)
    print("Models saved:")
    print("  - EfficientNet: ./models/efficientnet_medical_demo.pth")
    if bert_model:
        print("  - ClinicalBERT: ./models/clinicalbert_demo/")
    
    print("\nTo use these models in your application:")
    print("1. Load the saved models")
    print("2. Update ai_models.py to use the fine-tuned weights")
    print("3. Test with your medical data")
    
    return efficientnet_model, bert_model, tokenizer

if __name__ == "__main__":
    main()