#!/usr/bin/env python3
"""
Simple Medical Text Classifier
Uses basic PyTorch without transformers to avoid dependency issues
"""
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from tqdm import tqdm
import json
import re
from collections import Counter

class SimpleTextDataset(Dataset):
    """Simple text dataset with basic tokenization"""
    
    def __init__(self, csv_path, vocab=None, max_length=100):
        self.data = pd.read_csv(csv_path) if os.path.exists(csv_path) else self._create_dummy_data()
        self.max_length = max_length
        
        # Create vocabulary
        if vocab is None:
            self.vocab = self._build_vocab()
        else:
            self.vocab = vocab
        
        # Create label mapping
        unique_labels = self.data['label'].unique()
        self.label_map = {label: i for i, label in enumerate(unique_labels)}
        self.num_labels = len(self.label_map)
        
    def _create_dummy_data(self):
        """Create dummy medical text data"""
        texts = [
            "Patient presents with chest pain and shortness of breath",
            "Prescribed metformin 500mg twice daily for diabetes",
            "Blood glucose level: 126 mg/dL, HbA1c: 6.2%",
            "Diagnosis: Type 2 Diabetes Mellitus",
            "Patient reports headache and dizziness for past 3 days",
        ] * 20
        labels = ["symptom", "medication", "test_result", "diagnosis", "symptom"] * 20
        return pd.DataFrame({'text': texts, 'label': labels})
    
    def _build_vocab(self):
        """Build vocabulary from text data"""
        all_text = ' '.join(self.data['text'].astype(str))
        # Simple tokenization
        words = re.findall(r'\b\w+\b', all_text.lower())
        word_counts = Counter(words)
        
        # Keep most common words
        vocab = {'<PAD>': 0, '<UNK>': 1}
        for word, count in word_counts.most_common(1000):
            if count > 1:  # Only include words that appear more than once
                vocab[word] = len(vocab)
        
        return vocab
    
    def _text_to_indices(self, text):
        """Convert text to indices"""
        words = re.findall(r'\b\w+\b', text.lower())
        indices = [self.vocab.get(word, self.vocab['<UNK>']) for word in words]
        
        # Pad or truncate
        if len(indices) < self.max_length:
            indices.extend([self.vocab['<PAD>']] * (self.max_length - len(indices)))
        else:
            indices = indices[:self.max_length]
        
        return indices
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        
        # Convert text to indices
        text_indices = self._text_to_indices(row['text'])
        
        # Get label
        label = self.label_map[row['label']]
        
        return {
            'text': torch.tensor(text_indices, dtype=torch.long),
            'label': torch.tensor(label, dtype=torch.long)
        }

class SimpleMedicalTextClassifier(nn.Module):
    """Simple neural network for medical text classification"""
    
    def __init__(self, vocab_size, embedding_dim=64, hidden_dim=128, num_classes=5):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(hidden_dim * 2, num_classes)
        
    def forward(self, text):
        # Embedding
        embedded = self.embedding(text)  # (batch, seq_len, embedding_dim)
        
        # LSTM
        lstm_out, (hidden, _) = self.lstm(embedded)
        
        # Use last hidden state (bidirectional, so concat both directions)
        hidden = torch.cat([hidden[-2], hidden[-1]], dim=1)  # (batch, hidden_dim * 2)
        
        # Dropout and classification
        hidden = self.dropout(hidden)
        logits = self.classifier(hidden)
        
        return logits

def train_simple_text_model():
    """Train simple medical text classifier"""
    print("="*50)
    print("Simple Medical Text Classifier Training")
    print("="*50)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create dataset
    train_dataset = SimpleTextDataset('./data/medical_text/train.csv')
    val_dataset = SimpleTextDataset('./data/medical_text/val.csv', vocab=train_dataset.vocab)
    
    print(f"Vocabulary size: {len(train_dataset.vocab)}")
    print(f"Number of classes: {train_dataset.num_labels}")
    print(f"Train samples: {len(train_dataset)}")
    print(f"Val samples: {len(val_dataset)}")
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False, num_workers=0)
    
    # Create model
    model = SimpleMedicalTextClassifier(
        vocab_size=len(train_dataset.vocab),
        embedding_dim=64,
        hidden_dim=128,
        num_classes=train_dataset.num_labels
    )
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    # Training loop
    print("\nStarting training...")
    for epoch in range(3):
        # Train
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/3")
        for batch in pbar:
            text = batch['text'].to(device)
            labels = batch['label'].to(device)
            
            optimizer.zero_grad()
            outputs = model(text)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100.*correct/total:.1f}%'
            })
        
        train_acc = 100. * correct / total
        avg_loss = total_loss / len(train_loader)
        
        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        val_loss = 0
        
        with torch.no_grad():
            for batch in val_loader:
                text = batch['text'].to(device)
                labels = batch['label'].to(device)
                
                outputs = model(text)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_acc = 100. * val_correct / val_total
        val_avg_loss = val_loss / len(val_loader)
        
        print(f"Epoch {epoch+1}/3:")
        print(f"  Train - Loss: {avg_loss:.4f}, Acc: {train_acc:.1f}%")
        print(f"  Val   - Loss: {val_avg_loss:.4f}, Acc: {val_acc:.1f}%")
    
    # Save model
    os.makedirs('./models', exist_ok=True)
    torch.save({
        'model_state_dict': model.state_dict(),
        'vocab': train_dataset.vocab,
        'label_map': train_dataset.label_map,
        'model_config': {
            'vocab_size': len(train_dataset.vocab),
            'embedding_dim': 64,
            'hidden_dim': 128,
            'num_classes': train_dataset.num_labels
        }
    }, './models/simple_text_classifier.pth')
    
    print("\nSimple text classifier training complete!")
    print("Model saved to: ./models/simple_text_classifier.pth")
    
    return model, train_dataset.vocab, train_dataset.label_map

if __name__ == "__main__":
    train_simple_text_model()