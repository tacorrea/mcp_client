"""
LeoLM Client - German Language Model Integration.

This module provides integration with LeoLM (Leo Language Model),
specifically optimized for German language tasks including:
- Generating explanations for German grammar rules
- Creating example sentences
- Generating language learning exercises
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    GenerationConfig,
    pipeline
)


@dataclass
class LeoLMConfig:
    """Configuration for LeoLM model."""
    model_name: str = "LeoLM/leo-hessianai-7b-chat"  # Default LeoLM model
    device: str = "auto"  # auto, cpu, cuda
    max_length: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    do_sample: bool = True
    cache_dir: Optional[str] = None


@dataclass 
class GermanPrompt:
    """Structured prompt for German language tasks."""
    task_type: str  # explanation, example, exercise, correction
    content: str
    context: Optional[str] = None
    difficulty_level: str = "intermediate"  # beginner, intermediate, advanced
    target_grammar: Optional[str] = None


class LeoLMClient:
    """Client for interacting with LeoLM German language model."""
    
    def __init__(self, config: Optional[LeoLMConfig] = None):
        self.config = config or LeoLMConfig()
        self.logger = logging.getLogger(__name__)
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the LeoLM model and tokenizer."""
        try:
            self.logger.info(f"Loading LeoLM model: {self.config.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name,
                cache_dir=self.config.cache_dir
            )
            
            # Load model with simpler configuration
            if self.config.device == "cpu":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_name,
                    torch_dtype=torch.float32,
                    device_map="cpu",
                    cache_dir=self.config.cache_dir,
                    low_cpu_mem_usage=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto",
                    cache_dir=self.config.cache_dir,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True
                )
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map=self.config.device
            )
            
            self._is_initialized = True
            self.logger.info("LeoLM model successfully initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LeoLM: {e}")
            return False
    
    def _ensure_initialized(self):
        """Ensure the model is initialized before use."""
        if not self._is_initialized:
            raise RuntimeError("LeoLM model not initialized. Call initialize() first.")
    
    def _format_prompt(self, prompt: GermanPrompt) -> str:
        """Format a structured prompt for LeoLM."""
        system_prompt = self._get_system_prompt(prompt.task_type)
        
        formatted_prompt = f"""<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
Aufgabe: {prompt.task_type}
Schwierigkeitsgrad: {prompt.difficulty_level}
"""
        
        if prompt.target_grammar:
            formatted_prompt += f"Grammatik-Fokus: {prompt.target_grammar}\n"
        
        if prompt.context:
            formatted_prompt += f"Kontext: {prompt.context}\n"
            
        formatted_prompt += f"Inhalt: {prompt.content}<|im_end|>\n<|im_start|>assistant\n"
        
        return formatted_prompt
    
    def _get_system_prompt(self, task_type: str) -> str:
        """Get system prompt based on task type."""
        system_prompts = {
            "explanation": """Du bist ein erfahrener Deutschlehrer. Erkläre deutsche Grammatikregeln klar und verständlich. 
Verwende einfache Sprache und gib konkrete Beispiele. Strukturiere deine Antworten logisch.""",
            
            "example": """Du bist ein Deutschlehrer, der hilfreiche Beispiele erstellt. 
Generiere klare, relevante Beispielsätze, die die gewünschte Grammatikregel demonstrieren. 
Variiere die Komplexität basierend auf dem Schwierigkeitsgrad.""",
            
            "exercise": """Du bist ein Deutschlehrer, der Übungen erstellt. 
Erstelle ansprechende und lehrreiche Übungen für deutsche Grammatik. 
Stelle Fragen, Lückentexte oder Umformungsaufgaben bereit.""",
            
            "correction": """Du bist ein Deutschlehrer, der Texte korrigiert. 
Analysiere den Text auf Grammatikfehler, erkläre die Fehler und gib Verbesserungsvorschläge."""
        }
        
        return system_prompts.get(task_type, system_prompts["explanation"])
    
    async def generate_explanation(self, grammar_topic: str, difficulty: str = "intermediate", 
                                 context: Optional[str] = None) -> Dict[str, Any]:
        """Generate a German grammar explanation."""
        self._ensure_initialized()
        
        prompt = GermanPrompt(
            task_type="explanation",
            content=f"Erkläre mir die deutsche Grammatikregel: {grammar_topic}",
            difficulty_level=difficulty,
            context=context,
            target_grammar=grammar_topic
        )
        
        return await self._generate_text(prompt)
    
    async def generate_examples(self, grammar_topic: str, count: int = 3, 
                              difficulty: str = "intermediate") -> Dict[str, Any]:
        """Generate example sentences for a grammar topic."""
        self._ensure_initialized()
        
        prompt = GermanPrompt(
            task_type="example",
            content=f"Erstelle {count} Beispielsätze für: {grammar_topic}",
            difficulty_level=difficulty,
            target_grammar=grammar_topic
        )
        
        return await self._generate_text(prompt)
    
    async def generate_exercise(self, grammar_topic: str, exercise_type: str = "fill_blank",
                              difficulty: str = "intermediate") -> Dict[str, Any]:
        """Generate a German grammar exercise."""
        self._ensure_initialized()
        
        exercise_instructions = {
            "fill_blank": "Erstelle eine Lückentext-Übung",
            "multiple_choice": "Erstelle eine Multiple-Choice-Aufgabe", 
            "transformation": "Erstelle eine Satz-Umformungsaufgabe",
            "correction": "Erstelle eine Fehlerkorrektur-Aufgabe"
        }
        
        instruction = exercise_instructions.get(exercise_type, exercise_instructions["fill_blank"])
        
        prompt = GermanPrompt(
            task_type="exercise",
            content=f"{instruction} für das Thema: {grammar_topic}",
            difficulty_level=difficulty,
            target_grammar=grammar_topic
        )
        
        return await self._generate_text(prompt)
    
    async def analyze_text(self, text: str, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze German text and provide grammatical insights."""
        self._ensure_initialized()
        
        focus_str = ", ".join(focus_areas) if focus_areas else "allgemeine Grammatik"
        
        prompt = GermanPrompt(
            task_type="correction",
            content=f"Analysiere diesen deutschen Text auf {focus_str}: {text}",
            context="Textanalyse"
        )
        
        return await self._generate_text(prompt)
    
    async def _generate_text(self, prompt: GermanPrompt) -> Dict[str, Any]:
        """Internal method to generate text using LeoLM."""
        try:
            formatted_prompt = self._format_prompt(prompt)
            
            # Configure generation parameters
            generation_config = GenerationConfig(
                max_length=self.config.max_length,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=self.config.do_sample,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
            
            # Generate text
            outputs = self.pipeline(
                formatted_prompt,
                generation_config=generation_config,
                return_full_text=False
            )
            
            generated_text = outputs[0]['generated_text'].strip()
            
            # Extract only the assistant's response
            if "<|im_start|>assistant" in formatted_prompt:
                # Remove the assistant token if it appears in output
                if generated_text.startswith("<|im_start|>assistant"):
                    generated_text = generated_text.replace("<|im_start|>assistant", "").strip()
                if generated_text.endswith("<|im_end|>"):
                    generated_text = generated_text.replace("<|im_end|>", "").strip()
            
            return {
                "success": True,
                "generated_text": generated_text,
                "prompt_type": prompt.task_type,
                "target_grammar": prompt.target_grammar,
                "difficulty": prompt.difficulty_level
            }
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt_type": prompt.task_type
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_name": self.config.model_name,
            "device": self.config.device,
            "initialized": self._is_initialized,
            "max_length": self.config.max_length,
            "temperature": self.config.temperature
        }
    
    async def cleanup(self):
        """Clean up model resources."""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        if self.pipeline:
            del self.pipeline
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        self._is_initialized = False
        self.logger.info("LeoLM resources cleaned up")
