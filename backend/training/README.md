# Medical AI Model Training

This module provides tools for fine-tuning AI models on medical datasets.

## Models

### EfficientNet (Medical Image Classification)
- Base: EfficientNet-B0 pretrained on ImageNet
- Target: Multi-label chest X-ray classification (14 pathologies)
- Datasets: ChestX-ray14, CheXpert, MIMIC-CXR

### ClinicalBERT (Medical Text Understanding)
- Base: Bio_ClinicalBERT (trained on MIMIC-III clinical notes)
- Target: Medical text classification, NER, Q&A
- Datasets: MIMIC-III, MTSamples, i2b2

## Quick Start

### 1. Create Sample Dataset (for testing)
```bash
cd /app/backend/training
python download_datasets.py --create-sample --output-dir ./data
```

### 2. Train EfficientNet
```bash
# With GPU
python train_efficientnet.py \
    --data_dir ./data/chest_xray \
    --epochs 20 \
    --batch_size 32 \
    --lr 1e-4

# Output: ./models/efficientnet_medical.pth
```

### 3. Train ClinicalBERT
```bash
python train_clinicalbert.py \
    --data_dir ./data/medical_text \
    --epochs 10 \
    --batch_size 16 \
    --lr 2e-5

# Output: ./models/clinicalbert_finetuned/
```

## Using Fine-tuned Models

After training, update the main application to use fine-tuned models:

```python
# In ai_models.py

# For EfficientNet:
checkpoint = torch.load('./models/efficientnet_medical.pth')
model.load_state_dict(checkpoint['model_state_dict'])

# For ClinicalBERT:
from transformers import AutoModelForSequenceClassification, AutoTokenizer
model = AutoModelForSequenceClassification.from_pretrained('./models/clinicalbert_finetuned')
tokenizer = AutoTokenizer.from_pretrained('./models/clinicalbert_finetuned')
```

## Dataset Requirements

### Chest X-ray Dataset Structure
```
data/chest_xray/
├── train/
│   ├── images/
│   │   ├── image_001.png
│   │   └── ...
│   └── labels.csv
├── val/
└── test/
```

labels.csv columns:
- `image_path`: filename of image
- `label_0` to `label_13`: binary labels for each pathology

### Medical Text Dataset Structure
```
data/medical_text/
├── train.csv
├── val.csv
└── test.csv
```

CSV columns:
- `text`: medical text content
- `label`: category (diagnosis, medication, symptom, etc.)

## Training on Cloud GPU

### Google Colab
```python
# Upload training files
!pip install torch torchvision transformers scikit-learn tqdm

# Clone or upload the training folder
# Run training script
!python train_efficientnet.py --epochs 20 --batch_size 64
```

### AWS SageMaker / Azure ML
1. Package training scripts
2. Upload dataset to S3/Blob storage
3. Configure training job with GPU instance
4. Download trained model weights

## Expected Performance

### EfficientNet on ChestX-ray14
- AUC (macro): ~0.82-0.85
- Training time: ~4 hours on V100 GPU

### ClinicalBERT on Medical Text
- F1 (macro): ~0.88-0.92
- Training time: ~2 hours on V100 GPU

## References

1. ChestX-ray14: https://nihcc.app.box.com/v/ChestXray-NIHCC
2. CheXpert: https://stanfordmlgroup.github.io/competitions/chexpert/
3. MIMIC-CXR: https://physionet.org/content/mimic-cxr/
4. Bio_ClinicalBERT: https://huggingface.co/emilyalsentzer/Bio_ClinicalBERT
