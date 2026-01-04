"""
Training Configuration for Medical AI Models
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class EfficientNetConfig:
    """Configuration for EfficientNet medical image classifier"""
    model_name: str = "efficientnet_b0"
    num_classes: int = 14  # ChestX-ray14 has 14 pathology classes
    learning_rate: float = 1e-4
    batch_size: int = 32
    num_epochs: int = 20
    image_size: int = 224
    pretrained: bool = True
    freeze_backbone: bool = True  # Freeze early layers initially
    unfreeze_after_epochs: int = 5  # Unfreeze after N epochs
    dropout_rate: float = 0.3
    weight_decay: float = 1e-5
    
    # Data paths
    train_data_path: str = "./data/chest_xray/train"
    val_data_path: str = "./data/chest_xray/val"
    test_data_path: str = "./data/chest_xray/test"
    
    # Output
    checkpoint_dir: str = "./checkpoints/efficientnet"
    model_save_path: str = "./models/efficientnet_medical.pth"

@dataclass
class ClinicalBERTConfig:
    """Configuration for ClinicalBERT fine-tuning"""
    model_name: str = "emilyalsentzer/Bio_ClinicalBERT"
    num_labels: int = 5  # Medical text classification labels
    learning_rate: float = 2e-5
    batch_size: int = 16
    num_epochs: int = 10
    max_seq_length: int = 512
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    gradient_accumulation_steps: int = 2
    
    # Task type: 'classification', 'ner', 'qa'
    task_type: str = "classification"
    
    # Data paths
    train_data_path: str = "./data/medical_text/train.csv"
    val_data_path: str = "./data/medical_text/val.csv"
    test_data_path: str = "./data/medical_text/test.csv"
    
    # Output
    checkpoint_dir: str = "./checkpoints/clinicalbert"
    model_save_path: str = "./models/clinicalbert_finetuned"

# Medical condition labels for classification
MEDICAL_IMAGE_LABELS = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
    "Mass", "Nodule", "Pneumonia", "Pneumothorax",
    "Consolidation", "Edema", "Emphysema", "Fibrosis",
    "Pleural_Thickening", "Hernia"
]

MEDICAL_TEXT_LABELS = [
    "diagnosis",      # Diagnostic statement
    "treatment",      # Treatment recommendation
    "medication",     # Medication prescription
    "symptom",        # Symptom description
    "test_result"     # Lab/test results
]
