"""
Download Medical Datasets for Training

This script helps download publicly available medical datasets.
Note: Some datasets require registration/access approval.
"""
import os
import requests
import tarfile
import zipfile
from tqdm import tqdm
import pandas as pd
import json


DATASET_INFO = {
    'chest_xray_sample': {
        'description': 'Sample chest X-ray dataset (Kaggle)',
        'url': 'https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia',
        'registration_required': True,
        'instructions': '''
            1. Go to https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia
            2. Download the dataset
            3. Extract to ./data/chest_xray/
        '''
    },
    'chestx_ray14': {
        'description': 'NIH ChestX-ray14 Dataset (112,120 X-ray images)',
        'url': 'https://nihcc.app.box.com/v/ChestXray-NIHCC',
        'registration_required': True,
        'instructions': '''
            1. Go to https://nihcc.app.box.com/v/ChestXray-NIHCC
            2. Download images and labels
            3. Extract to ./data/chestx_ray14/
        '''
    },
    'mimic_cxr': {
        'description': 'MIMIC-CXR Database (377,110 images)',
        'url': 'https://physionet.org/content/mimic-cxr/2.0.0/',
        'registration_required': True,
        'instructions': '''
            1. Complete CITI training
            2. Sign DUA at PhysioNet
            3. Download from https://physionet.org/content/mimic-cxr/2.0.0/
        '''
    },
    'mimic_iii': {
        'description': 'MIMIC-III Clinical Database (text data)',
        'url': 'https://physionet.org/content/mimiciii/1.4/',
        'registration_required': True,
        'instructions': '''
            1. Complete CITI training
            2. Sign DUA at PhysioNet
            3. Download from https://physionet.org/content/mimiciii/1.4/
        '''
    },
    'mtsamples': {
        'description': 'MTSamples - Medical Transcription Samples',
        'url': 'https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions',
        'registration_required': False,
        'instructions': '''
            1. Download from Kaggle
            2. Place mtsamples.csv in ./data/medical_text/
        '''
    }
}


def create_sample_dataset(output_dir: str):
    """
    Create a sample dataset for testing the training pipeline
    """
    print("Creating sample medical dataset for testing...")
    
    # Create directories
    os.makedirs(os.path.join(output_dir, 'chest_xray', 'train', 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'chest_xray', 'val', 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'chest_xray', 'test', 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'medical_text'), exist_ok=True)
    
    # Create sample image labels
    import numpy as np
    from PIL import Image
    
    for split in ['train', 'val', 'test']:
        n_samples = 100 if split == 'train' else 20
        labels_data = []
        
        for i in range(n_samples):
            # Create dummy grayscale image
            img = Image.fromarray(
                np.random.randint(0, 255, (224, 224), dtype=np.uint8),
                mode='L'
            ).convert('RGB')
            img_path = f'image_{i}.png'
            img.save(os.path.join(output_dir, 'chest_xray', split, 'images', img_path))
            
            # Random labels
            labels_data.append({
                'image_path': img_path,
                **{f'label_{j}': np.random.randint(0, 2) for j in range(14)}
            })
        
        df = pd.DataFrame(labels_data)
        df.to_csv(os.path.join(output_dir, 'chest_xray', split, 'labels.csv'), index=False)
    
    # Create sample text data
    medical_texts = [
        ("Patient presents with chest pain radiating to left arm, shortness of breath, and diaphoresis. ECG shows ST elevation.", "diagnosis"),
        ("Prescribed Aspirin 81mg daily, Lisinopril 10mg daily, Metoprolol 25mg twice daily.", "medication"),
        ("Blood pressure: 145/92 mmHg. Heart rate: 88 bpm. Temperature: 98.6°F. SpO2: 96% on room air.", "test_result"),
        ("Patient reports persistent cough for 2 weeks, productive with yellow sputum. Denies fever or chills.", "symptom"),
        ("Recommend cardiac catheterization to assess coronary artery disease. Continue current medications.", "treatment"),
        ("Hemoglobin A1c: 7.2%. Fasting glucose: 132 mg/dL. Lipid panel within normal limits.", "test_result"),
        ("Diagnosis: Type 2 Diabetes Mellitus with peripheral neuropathy. ICD-10: E11.42", "diagnosis"),
        ("Start Metformin 500mg twice daily with meals. Increase gradually to 1000mg twice daily.", "medication"),
        ("Patient complains of numbness and tingling in both feet, worse at night.", "symptom"),
        ("Physical therapy referral for gait training and balance exercises.", "treatment"),
    ]
    
    # Expand dataset
    expanded_texts = medical_texts * 10
    np.random.shuffle(expanded_texts)
    
    # Split into train/val/test
    n = len(expanded_texts)
    train_texts = expanded_texts[:int(n*0.7)]
    val_texts = expanded_texts[int(n*0.7):int(n*0.85)]
    test_texts = expanded_texts[int(n*0.85):]
    
    for split, data in [('train', train_texts), ('val', val_texts), ('test', test_texts)]:
        df = pd.DataFrame(data, columns=['text', 'label'])
        df.to_csv(os.path.join(output_dir, 'medical_text', f'{split}.csv'), index=False)
    
    print(f"Sample dataset created in {output_dir}")
    print(f"  - Chest X-ray: train=100, val=20, test=20 images")
    print(f"  - Medical text: train={len(train_texts)}, val={len(val_texts)}, test={len(test_texts)} samples")


def list_datasets():
    """List available datasets and their download instructions"""
    print("\n" + "="*60)
    print("Available Medical Datasets")
    print("="*60)
    
    for name, info in DATASET_INFO.items():
        print(f"\n{name}")
        print("-" * len(name))
        print(f"Description: {info['description']}")
        print(f"URL: {info['url']}")
        print(f"Registration Required: {info['registration_required']}")
        print(f"Instructions:{info['instructions']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download medical datasets")
    parser.add_argument('--list', action='store_true', help='List available datasets')
    parser.add_argument('--create-sample', action='store_true', help='Create sample dataset for testing')
    parser.add_argument('--output-dir', type=str, default='./data', help='Output directory')
    args = parser.parse_args()
    
    if args.list:
        list_datasets()
    elif args.create_sample:
        create_sample_dataset(args.output_dir)
    else:
        print("Use --list to see available datasets or --create-sample to create a test dataset")
