"""
Ollama AI Assistant Integration for MedChain
Provides intelligent summaries and recommendations based on medical AI model outputs
"""
import logging
import requests
import json
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Ollama API configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"  # Default model, can be changed

class OllamaAssistant:
    """Ollama-powered AI assistant for medical analysis"""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                if self.model in model_names or any(self.model in name for name in model_names):
                    logger.info(f"✓ Ollama available with model: {self.model}")
                    return True
                else:
                    logger.warning(f"Ollama running but model '{self.model}' not found. Available: {model_names}")
                    return False
            return False
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Generate response from Ollama"""
        if not self.available:
            raise Exception("Ollama is not available. Please ensure Ollama is running.")
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60  # Increased from 30 to 60 seconds
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                if not generated_text:
                    raise Exception("Ollama returned an empty response")
                return generated_text
            else:
                error_msg = f"Ollama API returned status code {response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out after 60 seconds. The model may be processing a complex query or system resources may be low."
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to Ollama. Please ensure Ollama is running."
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error generating Ollama response: {e}")
            raise
    
    def analyze_efficientnet_results(self, efficientnet_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive analysis and recommendations from EfficientNet results
        
        Args:
            efficientnet_output: Output from fine-tuned EfficientNet model
            
        Returns:
            Enhanced analysis with Ollama-generated summary and recommendations
        """
        if not self.available or not efficientnet_output.get("success"):
            return efficientnet_output
        
        # Extract key information
        findings = efficientnet_output.get("findings", [])
        all_predictions = efficientnet_output.get("all_predictions", {})
        confidence = efficientnet_output.get("confidence", 0)
        
        # Build prompt for Ollama
        system_prompt = """You are a medical AI assistant specializing in radiology and chest X-ray interpretation. 
Your role is to provide clear, professional summaries and recommendations based on AI model predictions.
Always emphasize that AI analysis should be confirmed by qualified radiologists."""
        
        prompt = f"""Analyze the following chest X-ray AI predictions and provide:
1. A concise clinical summary (2-3 sentences)
2. Key findings interpretation
3. Recommended next steps
4. Any relevant clinical considerations

AI Model Predictions:
{json.dumps(all_predictions, indent=2)}

Top Findings:
{chr(10).join(findings)}

Overall Confidence: {confidence:.1%}

Provide a professional medical summary suitable for healthcare providers."""
        
        ollama_response = self.generate_response(prompt, system_prompt)
        
        if ollama_response:
            efficientnet_output["ollama_summary"] = ollama_response
            efficientnet_output["ai_enhanced"] = True
            logger.info("✓ EfficientNet results enhanced with Ollama analysis")
        
        return efficientnet_output
    
    def analyze_text_classification(self, text_output: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """
        Generate insights from medical text classification results
        
        Args:
            text_output: Output from text classifier
            original_text: Original medical text
            
        Returns:
            Enhanced analysis with Ollama insights
        """
        if not self.available or not text_output.get("success"):
            return text_output
        
        predicted_category = text_output.get("predicted_category", "unknown")
        confidence = text_output.get("confidence", 0)
        all_predictions = text_output.get("all_predictions", {})
        
        system_prompt = """You are a medical AI assistant specializing in clinical documentation analysis.
Provide clear, actionable insights based on medical text classification results."""
        
        prompt = f"""Analyze this medical text classification result:

Original Text: "{original_text}"

Classification Results:
- Predicted Category: {predicted_category}
- Confidence: {confidence:.1%}
- All Predictions: {json.dumps(all_predictions, indent=2)}

Provide:
1. Interpretation of the classification
2. Key medical concepts identified
3. Suggested actions or follow-up
4. Any important considerations

Keep response concise and clinically relevant."""
        
        ollama_response = self.generate_response(prompt, system_prompt)
        
        if ollama_response:
            text_output["ollama_insights"] = ollama_response
            text_output["ai_enhanced"] = True
            logger.info("✓ Text classification enhanced with Ollama insights")
        
        return text_output
    
    def generate_comprehensive_summary(
        self, 
        image_analysis: Optional[Dict[str, Any]] = None,
        text_analysis: Optional[Dict[str, Any]] = None,
        patient_query: Optional[str] = None,
        medical_context: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive medical summary combining multiple AI outputs
        
        Args:
            image_analysis: EfficientNet image analysis results
            text_analysis: Text classifier results
            patient_query: Patient's question or concern
            medical_context: Additional medical context from records
            
        Returns:
            Comprehensive AI-generated summary
        """
        if not self.available:
            return "Ollama AI assistant not available. Using basic analysis."
        
        # Build comprehensive prompt
        system_prompt = """You are MedChain AI Assistant, a helpful medical AI that provides clear, 
compassionate, and accurate information to patients and healthcare providers. 
Always remind users that AI analysis should be confirmed by qualified healthcare professionals."""
        
        prompt_parts = ["Please provide a comprehensive medical summary based on the following information:\n"]
        
        if patient_query:
            prompt_parts.append(f"\n**Patient Query:** {patient_query}")
        
        if image_analysis and image_analysis.get("success"):
            prompt_parts.append(f"\n**Medical Image Analysis (EfficientNet):**")
            prompt_parts.append(f"- Model: {image_analysis.get('model', 'EfficientNet')}")
            prompt_parts.append(f"- Confidence: {image_analysis.get('confidence', 0):.1%}")
            prompt_parts.append(f"- Findings: {', '.join(image_analysis.get('findings', []))}")
            if image_analysis.get("ollama_summary"):
                prompt_parts.append(f"- AI Summary: {image_analysis['ollama_summary']}")
        
        if text_analysis and text_analysis.get("success"):
            prompt_parts.append(f"\n**Medical Text Analysis:**")
            prompt_parts.append(f"- Category: {text_analysis.get('predicted_category', 'unknown')}")
            prompt_parts.append(f"- Confidence: {text_analysis.get('confidence', 0):.1%}")
            if text_analysis.get("ollama_insights"):
                prompt_parts.append(f"- AI Insights: {text_analysis['ollama_insights']}")
        
        if medical_context:
            prompt_parts.append(f"\n**Medical Records Context:**\n{medical_context[:500]}")
        
        prompt_parts.append("""

Please provide:
1. **Summary**: Clear overview of the medical situation
2. **Key Findings**: Important points from the AI analysis
3. **Recommendations**: Suggested next steps and actions
4. **Important Notes**: Any warnings or considerations

Format the response in a clear, patient-friendly manner while maintaining medical accuracy.""")
        
        prompt = "\n".join(prompt_parts)
        
        response = self.generate_response(prompt, system_prompt)
        
        if response:
            logger.info("✓ Generated comprehensive Ollama summary")
            return response
        else:
            return "Unable to generate AI summary. Please review individual analysis results."
    
    def get_medical_recommendations(self, findings: List[str], context: str = "") -> List[str]:
        """
        Generate specific medical recommendations based on findings
        
        Args:
            findings: List of medical findings
            context: Additional context
            
        Returns:
            List of actionable recommendations
        """
        if not self.available or not findings:
            return ["Consult with healthcare provider for personalized recommendations"]
        
        system_prompt = """You are a medical AI providing evidence-based recommendations.
Generate specific, actionable recommendations based on medical findings."""
        
        prompt = f"""Based on these medical findings, provide 3-5 specific, actionable recommendations:

Findings:
{chr(10).join(f"- {f}" for f in findings)}

{f"Context: {context}" if context else ""}

Provide recommendations as a numbered list. Be specific and practical."""
        
        response = self.generate_response(prompt, system_prompt)
        
        if response:
            # Parse recommendations from response
            recommendations = []
            for line in response.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                    # Remove numbering/bullets
                    clean_line = line.lstrip("0123456789.-•) ").strip()
                    if clean_line:
                        recommendations.append(clean_line)
            
            return recommendations if recommendations else [response]
        
        return ["Consult with healthcare provider for personalized recommendations"]
    
    def answer_medical_question(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        Answer patient medical questions with context from AI analysis
        Optimized for conversational chat interface
        
        Args:
            question: Patient's question
            context: Medical context including AI analysis results
            
        Returns:
            AI-generated conversational answer
        """
        if not self.available:
            return "AI assistant not available. Please consult with your healthcare provider."
        
        # Determine user role for appropriate tone
        user_role = context.get("user_role", "patient") if context else "patient"
        
        # Special handling for medical record analysis
        if user_role == "medical_analysis":
            return self._generate_medical_record_analysis(question, context)
        
        # Build context-aware system prompt
        if user_role == "doctor":
            system_prompt = """You are a medical AI assistant helping healthcare professionals.
Provide clear, evidence-based information using appropriate medical terminology.
Be concise but thorough. Include relevant clinical considerations."""
        else:
            system_prompt = """You are a compassionate medical AI assistant helping patients understand their health.
Provide clear, accurate information in patient-friendly language.
Be empathetic and supportive while emphasizing the importance of professional medical consultation.
Never provide definitive diagnoses - always recommend consulting healthcare providers.
Keep responses conversational and easy to understand."""
        
        # Build comprehensive prompt
        prompt_parts = []
        
        # Add the question
        prompt_parts.append(f"Question: {question}")
        
        # Add context if available
        if context:
            # Image analysis context
            if context.get("image_analysis") and context["image_analysis"].get("success"):
                img = context["image_analysis"]
                prompt_parts.append("\n**Medical Image Analysis Available:**")
                if img.get("findings"):
                    prompt_parts.append(f"Findings: {', '.join(img['findings'][:3])}")
                if img.get("ollama_summary"):
                    prompt_parts.append(f"AI Summary: {img['ollama_summary'][:200]}...")
            
            # Text analysis context
            if context.get("text_analysis") and context["text_analysis"].get("success"):
                txt = context["text_analysis"]
                prompt_parts.append(f"\n**Text Classification:** {txt.get('predicted_category', 'unknown')}")
                if txt.get("ollama_insights"):
                    prompt_parts.append(f"Insights: {txt['ollama_insights'][:200]}...")
            
            # Medical records context
            if context.get("medical_records"):
                records = context["medical_records"][:400]
                prompt_parts.append(f"\n**Medical Records Context:**\n{records}")
        
        # Add instructions
        if user_role == "doctor":
            prompt_parts.append("\nProvide a professional medical response with relevant clinical information.")
        else:
            prompt_parts.append("\nProvide a helpful, compassionate response that:")
            prompt_parts.append("1. Addresses the question directly")
            prompt_parts.append("2. Uses simple, clear language")
            prompt_parts.append("3. Provides actionable information")
            prompt_parts.append("4. Emphasizes consulting healthcare professionals")
            prompt_parts.append("5. Is supportive and empathetic")
        
        prompt = "\n".join(prompt_parts)
        
        # Generate response - raise exception if fails
        response = self.generate_response(prompt, system_prompt)
        
        if not response:
            # Raise exception instead of returning generic message
            raise Exception("Ollama did not return a response. This may be due to timeout or model error.")
        
        # Clean up response
        response = response.strip()
        
        # Add disclaimer if not already present and user is patient
        if user_role == "patient" and "consult" not in response.lower()[-200:]:
            response += "\n\nRemember to consult with your healthcare provider for personalized medical advice."
        
        return response
    
    def _generate_medical_record_analysis(self, analysis_prompt: str, context: Dict[str, Any]) -> str:
        """
        Generate specialized medical record analysis using Ollama
        
        Args:
            analysis_prompt: Detailed medical analysis prompt
            context: Medical context including document info
            
        Returns:
            Professional medical analysis
        """
        system_prompt = """You are a medical AI specialist with expertise in clinical documentation, radiology, pathology, and laboratory medicine. 
Your role is to provide comprehensive, professional medical analysis of healthcare documents.

Guidelines:
- Use appropriate medical terminology while remaining clear
- Provide structured, detailed analysis following the exact format requested
- Focus on clinical significance and patient care implications
- Identify key findings, abnormalities, and patterns with specific details
- Suggest appropriate follow-up care and monitoring with timelines
- Always emphasize the need for professional medical interpretation
- Be thorough and specific in your analysis
- Prioritize findings by clinical importance and urgency
- Include relevant medical context and differential considerations"""
        
        try:
            # Use longer timeout for complex medical analysis
            payload = {
                "model": self.model,
                "prompt": analysis_prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent medical analysis
                    "top_p": 0.9,
                    "num_predict": 2000  # Allow longer responses for detailed analysis
                }
            }
            
            logger.info("Generating detailed medical analysis with Ollama")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=90  # Extended timeout for complex medical analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                if not generated_text:
                    raise Exception("Ollama returned an empty response for medical analysis")
                
                logger.info(f"Medical analysis completed successfully, length: {len(generated_text)}")
                return generated_text
            else:
                error_msg = f"Ollama API returned status code {response.status_code} for medical analysis"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "Medical analysis timed out after 90 seconds. Complex medical documents may require additional processing time."
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to Ollama for medical analysis. Please ensure Ollama is running."
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error generating medical analysis: {e}")
            raise Exception(f"Medical analysis failed: {str(e)}")


# Global instance
_ollama_assistant = None

def get_ollama_assistant() -> OllamaAssistant:
    """Get or create global Ollama assistant instance"""
    global _ollama_assistant
    if _ollama_assistant is None:
        _ollama_assistant = OllamaAssistant()
    return _ollama_assistant

def is_ollama_available() -> bool:
    """Check if Ollama is available"""
    assistant = get_ollama_assistant()
    return assistant.available
