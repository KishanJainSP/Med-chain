"""
Fine-tuned AI Models Module for Medical Image and Text Analysis
Uses fine-tuned EfficientNet for medical images and simple text classifier
"""
import logging
import io
import os
import torch
import torch.nn as nn
from typing import Dict, Any, Optional
import numpy as np
import re
from collections import Counter

logger = logging.getLogger(__name__)

# Global model instances
efficientnet_model = None
text_classifier_model = None
text_vocab = None
text_label_map = None
models_loaded = False

# Medical condition labels (from training)
MEDICAL_IMAGE_LABELS = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration",
    "Mass", "Nodule", "Pneumonia", "Pneumothorax",
    "Consolidation", "Edema", "Emphysema", "Fibrosis",
    "Pleural_Thickening", "Hernia"
]

class MedicalEfficientNet(nn.Module):
    """EfficientNet modified for medical image classification"""
    def __init__(self, num_classes: int = 14, dropout_rate: float = 0.3):
        super().__init__()
        from torchvision import models
        
        # Load pretrained EfficientNet
        self.backbone = models.efficientnet_b0(weights='IMAGENET1K_V1')
        
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
        
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        logits = self.backbone(x)
        return logits

class SimpleMedicalTextClassifier(nn.Module):
    """Simple neural network for medical text classification"""
    
    def __init__(self, vocab_size, embedding_dim=64, hidden_dim=128, num_classes=5):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(hidden_dim * 2, num_classes)
        
    def forward(self, text):
        embedded = self.embedding(text)
        lstm_out, (hidden, _) = self.lstm(embedded)
        hidden = torch.cat([hidden[-2], hidden[-1]], dim=1)
        hidden = self.dropout(hidden)
        logits = self.classifier(hidden)
        return logits

def load_ai_models():
    """Load fine-tuned AI models"""
    global efficientnet_model, text_classifier_model, text_vocab, text_label_map, models_loaded
    
    if models_loaded:
        return
    
    logger.info("Loading fine-tuned AI models...")
    
    # Load fine-tuned EfficientNet
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'training', 'models', 'efficientnet_medical_demo.pth')
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location='cpu')
            efficientnet_model = MedicalEfficientNet(num_classes=14)
            efficientnet_model.load_state_dict(checkpoint['model_state_dict'])
            efficientnet_model.eval()
            logger.info("✓ Fine-tuned EfficientNet loaded successfully")
        else:
            logger.warning(f"Fine-tuned EfficientNet not found at {model_path}")
            efficientnet_model = None
    except Exception as e:
        logger.warning(f"Failed to load fine-tuned EfficientNet: {e}")
        efficientnet_model = None
    
    # Load simple text classifier
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'training', 'models', 'simple_text_classifier.pth')
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location='cpu')
            
            # Load model configuration
            config = checkpoint['model_config']
            text_classifier_model = SimpleMedicalTextClassifier(
                vocab_size=config['vocab_size'],
                embedding_dim=config['embedding_dim'],
                hidden_dim=config['hidden_dim'],
                num_classes=config['num_classes']
            )
            text_classifier_model.load_state_dict(checkpoint['model_state_dict'])
            text_classifier_model.eval()
            
            # Load vocabulary and label mapping
            text_vocab = checkpoint['vocab']
            text_label_map = checkpoint['label_map']
            
            logger.info("✓ Fine-tuned text classifier loaded successfully")
        else:
            logger.warning(f"Text classifier not found at {model_path}")
            text_classifier_model = None
    except Exception as e:
        logger.warning(f"Failed to load text classifier: {e}")
        text_classifier_model = None
    
    models_loaded = True

def analyze_medical_image(image_bytes: bytes, use_ollama: bool = True) -> Dict[str, Any]:
    """Analyze medical image using fine-tuned EfficientNet with optional Ollama enhancement"""
    if efficientnet_model is None:
        return {
            "success": False,
            "analysis": "Fine-tuned image analysis model not available",
            "confidence": 0
        }
    
    try:
        from torchvision import transforms
        from PIL import Image
        
        # Preprocess image
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        input_tensor = preprocess(image).unsqueeze(0)
        
        with torch.no_grad():
            logits = efficientnet_model(input_tensor)
            probabilities = torch.sigmoid(logits).squeeze().numpy()
        
        # Get top predictions
        top_indices = np.argsort(probabilities)[::-1][:5]
        
        findings = []
        recommendations = []
        
        for i, idx in enumerate(top_indices):
            if probabilities[idx] > 0.3:  # Threshold for significant findings
                condition = MEDICAL_IMAGE_LABELS[idx]
                confidence = probabilities[idx]
                findings.append(f"{condition}: {confidence:.1%} confidence")
                
                # Add condition-specific recommendations
                if condition in ["Pneumonia", "Infiltration"]:
                    recommendations.append("Consider antibiotic treatment if bacterial infection suspected")
                elif condition in ["Cardiomegaly", "Edema"]:
                    recommendations.append("Cardiac evaluation recommended")
                elif condition in ["Mass", "Nodule"]:
                    recommendations.append("Further imaging and specialist consultation advised")
        
        if not findings:
            findings = ["No significant abnormalities detected with high confidence"]
            recommendations = ["Routine follow-up as clinically indicated"]
        
        analysis_result = {
            "success": True,
            "type": "fine_tuned_medical_image_analysis",
            "model": "Fine-tuned EfficientNet for Medical Images",
            "confidence": float(np.max(probabilities)),
            "analysis": f"Medical chest X-ray analyzed using fine-tuned EfficientNet model trained on medical imaging data.",
            "findings": findings,
            "recommendations": recommendations,
            "all_predictions": {
                MEDICAL_IMAGE_LABELS[i]: float(probabilities[i]) 
                for i in range(len(MEDICAL_IMAGE_LABELS))
            },
            "disclaimer": "AI analysis is for reference only. Please consult a radiologist for definitive diagnosis."
        }
        
        # Enhance with Ollama if available and requested
        if use_ollama:
            try:
                from ollama_assistant import get_ollama_assistant
                ollama = get_ollama_assistant()
                if ollama.available:
                    analysis_result = ollama.analyze_efficientnet_results(analysis_result)
                    # Get additional recommendations from Ollama
                    ollama_recs = ollama.get_medical_recommendations(findings, "Chest X-ray analysis")
                    if ollama_recs:
                        analysis_result["ollama_recommendations"] = ollama_recs
            except Exception as e:
                logger.warning(f"Ollama enhancement failed: {e}")
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Fine-tuned image analysis error: {e}")
        return {
            "success": False,
            "analysis": f"Error analyzing image: {str(e)}",
            "confidence": 0
        }

def text_to_indices(text: str, vocab: dict, max_length: int = 100) -> list:
    """Convert text to indices using vocabulary"""
    words = re.findall(r'\\b\\w+\\b', text.lower())
    indices = [vocab.get(word, vocab.get('<UNK>', 1)) for word in words]
    
    # Pad or truncate
    if len(indices) < max_length:
        indices.extend([vocab.get('<PAD>', 0)] * (max_length - len(indices)))
    else:
        indices = indices[:max_length]
    
    return indices

def analyze_medical_text(text: str, use_ollama: bool = True) -> Dict[str, Any]:
    """Analyze medical text using fine-tuned text classifier with optional Ollama enhancement"""
    if text_classifier_model is None or text_vocab is None:
        return {
            "success": False,
            "analysis": "Fine-tuned text analysis model not available"
        }
    
    try:
        # Convert text to indices
        text_indices = text_to_indices(text, text_vocab)
        input_tensor = torch.tensor([text_indices], dtype=torch.long)
        
        with torch.no_grad():
            logits = text_classifier_model(input_tensor)
            probabilities = torch.softmax(logits, dim=1).squeeze().numpy()
        
        # Get prediction
        predicted_idx = np.argmax(probabilities)
        confidence = probabilities[predicted_idx]
        
        # Reverse label mapping
        idx_to_label = {v: k for k, v in text_label_map.items()}
        predicted_category = idx_to_label.get(predicted_idx, "unknown")
        
        # All predictions
        all_predictions = {
            idx_to_label.get(i, f"class_{i}"): float(probabilities[i])
            for i in range(len(probabilities))
        }
        
        result = {
            "success": True,
            "model": "Fine-tuned Medical Text Classifier",
            "predicted_category": predicted_category,
            "confidence": float(confidence),
            "all_predictions": all_predictions,
            "analysis": f"Text classified as '{predicted_category}' with {confidence:.1%} confidence"
        }
        
        # Enhance with Ollama if available and requested
        if use_ollama:
            try:
                from ollama_assistant import get_ollama_assistant
                ollama = get_ollama_assistant()
                if ollama.available:
                    result = ollama.analyze_text_classification(result, text)
            except Exception as e:
                logger.warning(f"Ollama enhancement failed: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Fine-tuned text analysis error: {e}")
        return {
            "success": False,
            "analysis": f"Error: {str(e)}"
        }

def get_medical_keywords(text: str) -> list:
    """Extract medical keywords from text"""
    medical_terms = [
        "diabetes", "hypertension", "blood pressure", "cholesterol",
        "heart", "cardiac", "pulmonary", "respiratory", "asthma",
        "headache", "migraine", "fever", "infection", "inflammation",
        "pain", "chronic", "acute", "symptom", "diagnosis",
        "prescription", "medication", "treatment", "therapy",
        "xray", "x-ray", "mri", "ct scan", "ultrasound",
        "blood test", "report", "scan", "imaging"
    ]
    
    text_lower = text.lower()
    found = [term for term in medical_terms if term in text_lower]
    return found

def generate_ai_response(query: str, context: str = "", image_analysis: Dict = None, use_ollama: bool = True) -> str:
    """Generate comprehensive AI response using fine-tuned models and Ollama"""
    
    keywords = get_medical_keywords(query)
    text_analysis = analyze_medical_text(query, use_ollama=use_ollama) if text_classifier_model else None
    
    # Try to use Ollama for comprehensive summary
    if use_ollama:
        try:
            from ollama_assistant import get_ollama_assistant
            ollama = get_ollama_assistant()
            if ollama.available:
                ollama_summary = ollama.generate_comprehensive_summary(
                    image_analysis=image_analysis,
                    text_analysis=text_analysis,
                    patient_query=query,
                    medical_context=context
                )
                if ollama_summary:
                    return ollama_summary
        except Exception as e:
            logger.warning(f"Ollama comprehensive summary failed: {e}")
    
    # Fallback to original response generation
    response_parts = []
    
    # Add context from records if available
    if context:
        response_parts.append(f"**Analysis of your medical records:**\\n{context}")
    
    # Add image analysis if available
    if image_analysis and image_analysis.get("success"):
        response_parts.append(f"\\n**Medical Image Analysis (Fine-tuned EfficientNet):**")
        response_parts.append(f"- {image_analysis['analysis']}")
        response_parts.append(f"- Model: {image_analysis.get('model', 'Fine-tuned EfficientNet')}")
        for finding in image_analysis.get("findings", []):
            response_parts.append(f"- {finding}")
        
        # Add Ollama summary if available
        if image_analysis.get("ollama_summary"):
            response_parts.append(f"\\n**AI Analysis Summary:**\\n{image_analysis['ollama_summary']}")
        
        if image_analysis.get("recommendations"):
            response_parts.append("\\n**Recommendations:**")
            for rec in image_analysis["recommendations"]:
                response_parts.append(f"- {rec}")
        
        # Add Ollama recommendations if available
        if image_analysis.get("ollama_recommendations"):
            response_parts.append("\\n**Additional AI Recommendations:**")
            for rec in image_analysis["ollama_recommendations"]:
                response_parts.append(f"- {rec}")
    
    # Add text classification if available
    if text_analysis and text_analysis.get("success"):
        response_parts.append(f"\\n**Text Analysis (Fine-tuned Classifier):**")
        response_parts.append(f"- Category: {text_analysis['predicted_category']}")
        response_parts.append(f"- Confidence: {text_analysis['confidence']:.1%}")
        response_parts.append(f"- Model: {text_analysis.get('model', 'Fine-tuned Text Classifier')}")
        
        # Add Ollama insights if available
        if text_analysis.get("ollama_insights"):
            response_parts.append(f"\\n**AI Insights:**\\n{text_analysis['ollama_insights']}")
    
    # Generate medical information based on keywords
    if keywords:
        response_parts.append(f"\\n**Relevant Medical Information:**")
        response_parts.append(get_condition_info(keywords))
    else:
        response_parts.append(get_general_help())
    
    # Add disclaimer
    response_parts.append("\\n\\n*Disclaimer: This AI analysis uses fine-tuned medical models but is for educational purposes only. Always consult a healthcare professional for medical advice.*")
    
    return "\\n".join(response_parts)

def get_condition_info(keywords: list) -> str:
    """Get information about detected medical conditions"""
    info_map = {
        "diabetes": "**Diabetes:** Monitor blood sugar, maintain balanced diet, regular exercise, medication adherence, regular check-ups.",
        "hypertension": "**Hypertension:** Regular BP monitoring, low sodium diet, exercise, stress management, medication as prescribed.",
        "blood pressure": "**Blood Pressure:** Keep track of readings, healthy lifestyle, limit salt and alcohol, maintain healthy weight.",
        "heart": "**Heart Health:** Cardiovascular exercise, heart-healthy diet, avoid smoking, regular screenings.",
        "cardiac": "**Cardiac Care:** Follow cardiologist recommendations, monitor symptoms, emergency protocols.",
        "asthma": "**Asthma:** Identify triggers, use inhalers correctly, have action plan, keep rescue medication accessible.",
        "headache": "**Headache:** Stay hydrated, adequate rest, identify triggers, seek care for severe/persistent cases.",
        "migraine": "**Migraine:** Track triggers, dark quiet room during episodes, preventive medications if frequent.",
        "fever": "**Fever:** Rest, hydration, monitor temperature, seek care if >103°F or persists.",
        "pain": "**Pain Management:** Identify source, rest, ice/heat as appropriate, consult for persistent pain.",
        "xray": "**X-Ray Results:** Requires radiologist interpretation. Discuss findings with your doctor.",
        "mri": "**MRI Results:** Complex imaging requires specialist review for accurate interpretation.",
        "blood test": "**Blood Test:** Results should be reviewed with your healthcare provider for context.",
        "prescription": "**Prescription:** Follow dosage instructions, note side effects, don't skip doses.",
        "report": "**Medical Report:** Review with your healthcare provider for personalized interpretation.",
    }
    
    responses = []
    for kw in keywords[:3]:  # Limit to 3 conditions
        for key, info in info_map.items():
            if key in kw or kw in key:
                responses.append(info)
                break
    
    return "\\n".join(responses) if responses else "Please provide more details about your health concern."

def get_general_help() -> str:
    """Return message directing to Ollama chat"""
    return "Please use the chat interface for medical questions. All responses are powered by Ollama AI for natural, conversational assistance."

def get_model_status() -> Dict[str, bool]:
    """Return status of loaded fine-tuned models"""
    return {
        "efficientnet_finetuned": efficientnet_model is not None,
        "text_classifier_finetuned": text_classifier_model is not None,
        "models_loaded": models_loaded,
        "model_paths": {
            "efficientnet": os.path.join(os.path.dirname(__file__), 'training', 'models', 'efficientnet_medical_demo.pth'),
            "text_classifier": os.path.join(os.path.dirname(__file__), 'training', 'models', 'simple_text_classifier.pth')
        }
    }