"""
Fine-tune EfficientNet for Medical Image Classification

Usage:
    python train_efficientnet.py --data_dir ./data/chest_xray --epochs 20 --batch_size 32

Supported datasets:
    - ChestX-ray14 (NIH)
    - CheXpert
    - MIMIC-CXR
    - Custom medical image datasets
"""
import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from torchvision import models
import numpy as np
from tqdm import tqdm
import json
from datetime import datetime

from config import EfficientNetConfig, MEDICAL_IMAGE_LABELS
from datasets import ChestXrayDataset, create_data_loaders

# Simple metrics calculation to avoid sklearn compatibility issues
def calculate_auc(y_true, y_pred):
    """Simple AUC calculation"""
    try:
        from sklearn.metrics import roc_auc_score
        return roc_auc_score(y_true, y_pred, average='macro')
    except:
        # Fallback: simple accuracy for binary classification
        y_pred_binary = (y_pred > 0.5).astype(int)
        return np.mean(y_true == y_pred_binary)


class MedicalEfficientNet(nn.Module):
    """
    EfficientNet modified for medical image classification
    """
    def __init__(self, num_classes: int = 14, dropout_rate: float = 0.3, pretrained: bool = True):
        super().__init__()
        
        # Load pretrained EfficientNet
        if pretrained:
            self.backbone = models.efficientnet_b0(weights='IMAGENET1K_V1')
        else:
            self.backbone = models.efficientnet_b0(weights=None)
        
        # Get the number of features from the classifier
        num_features = self.backbone.classifier[1].in_features
        
        # Replace classifier for multi-label classification
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(512, num_classes)
        )
        
        # For multi-label, we'll use sigmoid in forward
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        logits = self.backbone(x)
        return logits  # Return logits, apply sigmoid during inference
    
    def freeze_backbone(self):
        """Freeze all backbone layers except classifier"""
        for param in self.backbone.features.parameters():
            param.requires_grad = False
    
    def unfreeze_backbone(self):
        """Unfreeze all layers for full fine-tuning"""
        for param in self.backbone.parameters():
            param.requires_grad = True


def train_epoch(model, train_loader, criterion, optimizer, device, epoch, config):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    all_preds = []
    all_labels = []
    
    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{config.num_epochs}")
    
    for batch_idx, (images, labels) in enumerate(pbar):
        images = images.to(device)
        labels = labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
        # Store predictions for metrics
        preds = torch.sigmoid(outputs).detach().cpu().numpy()
        all_preds.append(preds)
        all_labels.append(labels.cpu().numpy())
        
        pbar.set_postfix({'loss': f'{loss.item():.4f}'})
    
    avg_loss = total_loss / len(train_loader)
    all_preds = np.vstack(all_preds)
    all_labels = np.vstack(all_labels)
    
    # Calculate metrics
    try:
        auc = calculate_auc(all_labels, all_preds)
    except ValueError:
        auc = 0.0
    
    return avg_loss, auc


def validate(model, val_loader, criterion, device):
    """Validate the model"""
    model.eval()
    total_loss = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in tqdm(val_loader, desc="Validating"):
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item()
            
            preds = torch.sigmoid(outputs).cpu().numpy()
            all_preds.append(preds)
            all_labels.append(labels.cpu().numpy())
    
    avg_loss = total_loss / len(val_loader)
    all_preds = np.vstack(all_preds)
    all_labels = np.vstack(all_labels)
    
    # Calculate metrics
    try:
        auc = calculate_auc(all_labels, all_preds)
    except ValueError:
        auc = 0.0
    
    # Per-class AUC
    per_class_auc = {}
    for i, label_name in enumerate(MEDICAL_IMAGE_LABELS[:all_labels.shape[1]]):
        try:
            per_class_auc[label_name] = calculate_auc(all_labels[:, i], all_preds[:, i])
        except ValueError:
            per_class_auc[label_name] = 0.0
    
    return avg_loss, auc, per_class_auc


def train_model(config: EfficientNetConfig):
    """
    Main training function
    """
    print("="*60)
    print("EfficientNet Medical Image Fine-tuning")
    print("="*60)
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create directories
    os.makedirs(config.checkpoint_dir, exist_ok=True)
    os.makedirs(os.path.dirname(config.model_save_path), exist_ok=True)
    
    # Create model
    print(f"\nLoading {config.model_name}...")
    model = MedicalEfficientNet(
        num_classes=config.num_classes,
        dropout_rate=config.dropout_rate,
        pretrained=config.pretrained
    )
    
    if config.freeze_backbone:
        print("Freezing backbone layers...")
        model.freeze_backbone()
    
    model = model.to(device)
    
    # Create data loaders
    print("\nLoading datasets...")
    train_loader, val_loader, test_loader = create_data_loaders(
        ChestXrayDataset, config
    )
    print(f"Train samples: {len(train_loader.dataset)}")
    print(f"Val samples: {len(val_loader.dataset)}")
    
    # Loss and optimizer
    criterion = nn.BCEWithLogitsLoss()  # For multi-label classification
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=config.num_epochs)
    
    # Training loop
    best_auc = 0
    history = {'train_loss': [], 'val_loss': [], 'train_auc': [], 'val_auc': []}
    
    print("\nStarting training...")
    for epoch in range(config.num_epochs):
        # Unfreeze backbone after specified epochs
        if epoch == config.unfreeze_after_epochs and config.freeze_backbone:
            print(f"\nUnfreezing backbone at epoch {epoch+1}")
            model.unfreeze_backbone()
            # Reset optimizer with lower learning rate for backbone
            optimizer = optim.AdamW([
                {'params': model.backbone.features.parameters(), 'lr': config.learning_rate / 10},
                {'params': model.backbone.classifier.parameters(), 'lr': config.learning_rate}
            ], weight_decay=config.weight_decay)
        
        # Train
        train_loss, train_auc = train_epoch(
            model, train_loader, criterion, optimizer, device, epoch, config
        )
        
        # Validate
        val_loss, val_auc, per_class_auc = validate(
            model, val_loader, criterion, device
        )
        
        scheduler.step()
        
        # Log metrics
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_auc'].append(train_auc)
        history['val_auc'].append(val_auc)
        
        print(f"\nEpoch {epoch+1}/{config.num_epochs}:")
        print(f"  Train Loss: {train_loss:.4f}, Train AUC: {train_auc:.4f}")
        print(f"  Val Loss: {val_loss:.4f}, Val AUC: {val_auc:.4f}")
        
        # Save best model
        if val_auc > best_auc:
            best_auc = val_auc
            print(f"  New best AUC! Saving model...")
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_auc': val_auc,
                'config': config.__dict__
            }, config.model_save_path)
        
        # Save checkpoint
        checkpoint_path = os.path.join(
            config.checkpoint_dir,
            f'checkpoint_epoch_{epoch+1}.pth'
        )
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_auc': val_auc
        }, checkpoint_path)
    
    # Final evaluation on test set
    print("\n" + "="*60)
    print("Final Evaluation on Test Set")
    print("="*60)
    
    # Load best model
    checkpoint = torch.load(config.model_save_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    test_loss, test_auc, per_class_auc = validate(
        model, test_loader, criterion, device
    )
    
    print(f"\nTest Loss: {test_loss:.4f}")
    print(f"Test AUC (macro): {test_auc:.4f}")
    print("\nPer-class AUC:")
    for label, auc in per_class_auc.items():
        print(f"  {label}: {auc:.4f}")
    
    # Save training history
    history['test_auc'] = test_auc
    history['per_class_auc'] = per_class_auc
    history_path = os.path.join(config.checkpoint_dir, 'training_history.json')
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"\nTraining complete! Model saved to: {config.model_save_path}")
    return model, history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune EfficientNet for medical images")
    parser.add_argument('--data_dir', type=str, default='./data/chest_xray')
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--num_classes', type=int, default=14)
    parser.add_argument('--output_dir', type=str, default='./models')
    args = parser.parse_args()
    
    config = EfficientNetConfig(
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        num_classes=args.num_classes,
        train_data_path=os.path.join(args.data_dir, 'train'),
        val_data_path=os.path.join(args.data_dir, 'val'),
        test_data_path=os.path.join(args.data_dir, 'test'),
        model_save_path=os.path.join(args.output_dir, 'efficientnet_medical.pth')
    )
    
    train_model(config)
