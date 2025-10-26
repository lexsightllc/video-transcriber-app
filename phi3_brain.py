"""
Phi-3 Brain Module for Video Transcription Pipeline
This module integrates Microsoft's Phi-3 model as the intelligent core
for enhanced video content analysis and processing.
"""

import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, List, Optional, Any
import json
import re

logger = logging.getLogger(__name__)

class Phi3Brain:
    """
    Phi-3 powered brain for intelligent video content analysis.
    Provides advanced capabilities beyond basic transcription.
    """
    
    def __init__(self, model_name: str = "microsoft/Phi-3-mini-4k-instruct", device: str = "auto"):
        """
        Initialize the Phi-3 brain.
        
        Args:
            model_name: HuggingFace model identifier for Phi-3
            device: Device to run the model on ('auto', 'cpu', 'cuda')
        """
        self.model_name = model_name
        self.device = self._get_device(device)
        self.tokenizer = None
        self.model = None
        self._load_model()
        
    def _get_device(self, device: str) -> str:
        """Determine the best device to use."""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def _load_model(self):
        """Load the Phi-3 model and tokenizer."""
        try:
            logger.info(f"Loading Phi-3 model: {self.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load model with appropriate settings
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device != "cpu" else torch.float32,
                "device_map": "auto" if self.device == "cuda" else None
            }
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            if self.device != "cuda":
                self.model = self.model.to(self.device)
                
            logger.info(f"Phi-3 model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load Phi-3 model: {e}")
            raise
    
    def _generate_response(self, prompt: str, max_length: int = 1000, temperature: float = 0.7) -> str:
        """Generate a response using Phi-3."""
        try:
            # Format prompt for Phi-3 chat format
            messages = [{"role": "user", "content": prompt}]
            formatted_prompt = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # Tokenize
            inputs = self.tokenizer(
                formatted_prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=2048
            ).to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:], 
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"
    
    def analyze_transcription_quality(self, transcription: str) -> Dict[str, Any]:
        """
        Analyze the quality of a transcription and suggest improvements.
        """
        prompt = f"""
        Analyze the following video transcription for quality and provide insights:

        TRANSCRIPTION:
        {transcription}

        Please provide:
        1. Overall quality assessment (1-10 scale)
        2. Potential issues (unclear segments, missing punctuation, etc.)
        3. Suggested improvements
        4. Confidence level in the transcription accuracy

        Format your response as JSON with keys: quality_score, issues, improvements, confidence_level
        """
        
        response = self._generate_response(prompt, max_length=500)
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback to structured text analysis
        return {
            "quality_score": 7,
            "issues": ["Analysis could not be parsed as JSON"],
            "improvements": ["Manual review recommended"],
            "confidence_level": "medium",
            "raw_analysis": response
        }
    
    def generate_summary(self, transcription: str, summary_type: str = "comprehensive") -> str:
        """
        Generate an intelligent summary of the video content.
        
        Args:
            transcription: The video transcription text
            summary_type: Type of summary ('brief', 'comprehensive', 'bullet_points')
        """
        summary_prompts = {
            "brief": "Provide a brief 2-3 sentence summary of the main points:",
            "comprehensive": "Provide a comprehensive summary covering all key topics and insights:",
            "bullet_points": "Summarize the content as clear bullet points of key information:"
        }
        
        prompt = f"""
        {summary_prompts.get(summary_type, summary_prompts['comprehensive'])}

        VIDEO TRANSCRIPTION:
        {transcription}

        Summary:
        """
        
        return self._generate_response(prompt, max_length=800)
    
    def extract_key_topics(self, transcription: str) -> List[str]:
        """Extract key topics and themes from the transcription."""
        prompt = f"""
        Extract the main topics and themes discussed in this video transcription.
        Return only a comma-separated list of key topics (no explanations):

        TRANSCRIPTION:
        {transcription}

        Key topics:
        """
        
        response = self._generate_response(prompt, max_length=200)
        
        # Parse topics from response
        topics = [topic.strip() for topic in response.split(',')]
        return [topic for topic in topics if topic and len(topic) > 2]
    
    def analyze_sentiment(self, transcription: str) -> Dict[str, Any]:
        """Analyze the sentiment and emotional tone of the content."""
        prompt = f"""
        Analyze the sentiment and emotional tone of this video content:

        TRANSCRIPTION:
        {transcription}

        Provide:
        1. Overall sentiment (positive/negative/neutral)
        2. Emotional tone (professional, casual, excited, etc.)
        3. Key emotional moments or shifts
        4. Confidence in analysis

        Format as JSON with keys: sentiment, tone, emotional_moments, confidence
        """
        
        response = self._generate_response(prompt, max_length=400)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "sentiment": "neutral",
            "tone": "unknown",
            "emotional_moments": [],
            "confidence": "low",
            "raw_analysis": response
        }
    
    def generate_questions(self, transcription: str, num_questions: int = 5) -> List[str]:
        """Generate intelligent questions about the video content."""
        prompt = f"""
        Based on this video transcription, generate {num_questions} thoughtful questions that would help someone understand or engage with the content better.

        TRANSCRIPTION:
        {transcription}

        Questions (one per line):
        """
        
        response = self._generate_response(prompt, max_length=300)
        
        # Parse questions from response
        questions = []
        for line in response.split('\n'):
            line = line.strip()
            if line and ('?' in line or line.lower().startswith(('what', 'how', 'why', 'when', 'where', 'who'))):
                # Clean up question formatting
                question = re.sub(r'^\d+\.?\s*', '', line)  # Remove numbering
                questions.append(question)
        
        return questions[:num_questions]
    
    def answer_question(self, transcription: str, question: str) -> str:
        """Answer a question about the video content."""
        prompt = f"""
        Based on the following video transcription, answer this question:

        QUESTION: {question}

        TRANSCRIPTION:
        {transcription}

        ANSWER:
        """
        
        return self._generate_response(prompt, max_length=400)
    
    def generate_metadata(self, transcription: str) -> Dict[str, Any]:
        """Generate comprehensive metadata about the video content."""
        return {
            "summary": self.generate_summary(transcription, "brief"),
            "key_topics": self.extract_key_topics(transcription),
            "sentiment_analysis": self.analyze_sentiment(transcription),
            "quality_assessment": self.analyze_transcription_quality(transcription),
            "suggested_questions": self.generate_questions(transcription, 3),
            "word_count": len(transcription.split()),
            "estimated_duration_minutes": len(transcription.split()) / 150  # Rough estimate
        }
