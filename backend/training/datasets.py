"""
Medical Dataset Loaders for Training
"""
import os
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import pandas as pd
from typing import Tuple, List, Optional
import numpy as np


class ChestXrayDataset(Dataset):
    """
    Dataset for Chest X-ray images (compatible with ChestX-ray14, CheXpert, etc.)
    
    Expected directory structure:
    data/
      chest_xray/
        train/
          images/
          labels.csv  (columns: image_path, label1, label2, ...)
        val/
        test/
    """
    
    def __init__(
        self,
        data_dir: str,
        split: str = "train",
        image_size: int = 224,
        num_classes: int = 14,
        augment: bool = True
    ):
        self.data_dir = os.path.join(data_dir, split)
        self.image_dir = os.path.join(self.data_dir, "images")
        self.num_classes = num_classes
        self.augment = augment and split == "train"
        
        # Load labels
        labels_path = os.path.join(self.data_dir, "labels.csv")
        if os.path.exists(labels_path):
            self.labels_df = pd.read_csv(labels_path)
        else:
            # Create dummy data for demonstration
            self.labels_df = self._create_dummy_data()
        
        # Transforms
        if self.augment:
            self.transform = transforms.Compose([
                transforms.Resize((image_size + 32, image_size + 32)),
                transforms.RandomCrop(image_size),
                transforms.RandomHorizontalFlip(),
                transforms.RandomRotation(10),
                transforms.ColorJitter(brightness=0.1, contrast=0.1),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
    
    def _create_dummy_data(self):
        """Create dummy data for testing the pipeline"""
        return pd.DataFrame({
            'image_path': [f'dummy_{i}.png' for i in range(100)],
            **{f'label_{i}': np.random.randint(0, 2, 100) for i in range(self.num_classes)}
        })
    
    def __len__(self):
        return len(self.labels_df)
    
    def __getitem__(self, idx) -> Tuple[torch.Tensor, torch.Tensor]:
        row = self.labels_df.iloc[idx]
        
        # Load image
        image_path = os.path.join(self.image_dir, row['image_path'])
        if os.path.exists(image_path):
            image = Image.open(image_path).convert('RGB')
        else:
            # Create dummy image for testing
            image = Image.new('RGB', (224, 224), color='gray')
        
        image = self.transform(image)
        
        # Get labels (multi-label classification)
        labels = torch.zeros(self.num_classes)
        for i in range(self.num_classes):
            col_name = f'label_{i}'
            if col_name in row:
                labels[i] = float(row[col_name])
        
        return image, labels


class MedicalTextDataset(Dataset):
    """
    Dataset for Medical Text Classification
    
    Expected CSV format:
    text,label
    "Patient presents with...",diagnosis
    "Prescribed medication...",medication
    """
    
    def __init__(
        self,
        data_path: str,
        tokenizer,
        max_length: int = 512,
        label_map: Optional[dict] = None
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Load data
        if os.path.exists(data_path):
            self.data = pd.read_csv(data_path)
        else:
            # Create dummy data
            self.data = self._create_dummy_data()
        
        # Label mapping
        if label_map:
            self.label_map = label_map
        else:
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
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx) -> dict:
        row = self.data.iloc[idx]
        
        # Tokenize text
        encoding = self.tokenizer(
            row['text'],
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Get label
        label = self.label_map.get(row['label'], 0)
        
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


def create_data_loaders(
    dataset_class,
    config,
    tokenizer=None
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Create train, validation, and test data loaders
    """
    if dataset_class == ChestXrayDataset:
        train_dataset = ChestXrayDataset(
            config.train_data_path.replace('/train', ''),
            split='train',
            image_size=config.image_size,
            num_classes=config.num_classes,
            augment=True
        )
        val_dataset = ChestXrayDataset(
            config.val_data_path.replace('/val', ''),
            split='val',
            image_size=config.image_size,
            num_classes=config.num_classes,
            augment=False
        )
        test_dataset = ChestXrayDataset(
            config.test_data_path.replace('/test', ''),
            split='test',
            image_size=config.image_size,
            num_classes=config.num_classes,
            augment=False
        )
    else:
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
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    return train_loader, val_loader, test_loader
