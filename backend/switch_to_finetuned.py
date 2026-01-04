#!/usr/bin/env python3
"""
Switch to Fine-tuned Models
This script backs up the original ai_models.py and replaces it with the fine-tuned version
"""
import os
import shutil
from datetime import datetime

def switch_to_finetuned():
    """Switch to fine-tuned AI models"""
    
    # Paths
    original_file = "ai_models.py"
    finetuned_file = "ai_models_finetuned.py"
    backup_file = f"ai_models_original_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    print("Switching to Fine-tuned AI Models")
    print("=" * 40)
    
    # Check if files exist
    if not os.path.exists(original_file):
        print(f"❌ Original file {original_file} not found")
        return False
    
    if not os.path.exists(finetuned_file):
        print(f"❌ Fine-tuned file {finetuned_file} not found")
        return False
    
    try:
        # Backup original
        print(f"📁 Backing up original to {backup_file}")
        shutil.copy2(original_file, backup_file)
        
        # Replace with fine-tuned version
        print(f"🔄 Replacing {original_file} with fine-tuned version")
        shutil.copy2(finetuned_file, original_file)
        
        print("✅ Successfully switched to fine-tuned models!")
        print()
        print("Fine-tuned models now active:")
        print("  - EfficientNet: Fine-tuned for medical chest X-ray analysis")
        print("  - Text Classifier: Fine-tuned for medical text classification")
        print()
        print("To revert back:")
        print(f"  cp {backup_file} {original_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error switching models: {e}")
        return False

def check_model_files():
    """Check if fine-tuned model files exist"""
    print("Checking Fine-tuned Model Files")
    print("=" * 35)
    
    model_files = [
        "training/models/efficientnet_medical_demo.pth",
        "training/models/simple_text_classifier.pth"
    ]
    
    all_exist = True
    for model_file in model_files:
        if os.path.exists(model_file):
            size = os.path.getsize(model_file) / (1024 * 1024)  # MB
            print(f"✅ {model_file} ({size:.1f} MB)")
        else:
            print(f"❌ {model_file} - NOT FOUND")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("MedChain Fine-tuned Model Switcher")
    print("=" * 40)
    
    # Check model files first
    if not check_model_files():
        print()
        print("❌ Some fine-tuned model files are missing!")
        print("Please run the training scripts first:")
        print("  cd training")
        print("  python quick_train.py")
        print("  python simple_text_model.py")
    else:
        print()
        switch_to_finetuned()