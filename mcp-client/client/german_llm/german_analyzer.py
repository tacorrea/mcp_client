"""
German Language Analyzer - Comprehensive German Language Learning Assistant.

This module combines LeoLM and LanguageTool to provide:
- Grammar explanations and examples
- Text analysis and correction
- Learning exercises generation
- Comprehensive feedback for German language learners
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .leolm_client import LeoLMClient, LeoLMConfig, GermanPrompt
from .languagetool_client import LanguageToolClient, LanguageToolConfig, GrammarAnalysis


@dataclass
class GermanAnalyzerConfig:
    """Configuration for the German Language Analyzer."""
    leolm_config: Optional[LeoLMConfig] = None
    languagetool_config: Optional[LanguageToolConfig] = None
    auto_correct: bool = False
    provide_examples: bool = True
    generate_exercises: bool = False
    difficulty_level: str = "intermediate"


@dataclass
class ComprehensiveAnalysis:
    """Complete analysis combining LLM and grammar checking."""
    original_text: str
    grammar_analysis: GrammarAnalysis
    llm_analysis: Optional[Dict[str, Any]] = None
    explanations: List[Dict[str, Any]] = None
    examples: List[str] = None
    exercises: List[Dict[str, Any]] = None
    learning_recommendations: List[str] = None


class GermanLanguageAnalyzer:
    """Main class that orchestrates LeoLM and LanguageTool for German language learning."""
    
    def __init__(self, config: Optional[GermanAnalyzerConfig] = None):
        self.config = config or GermanAnalyzerConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize clients
        if self.config.leolm_config:
            self.leolm_client = LeoLMClient(self.config.leolm_config)
        else:
            self.leolm_client = None
        self.languagetool_client = LanguageToolClient(self.config.languagetool_config)
        
        self._is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize both LeoLM and LanguageTool."""
        try:
            self.logger.info("Initializing German Language Analyzer...")
            
            # Initialize LanguageTool first (faster)
            lt_success = await self.languagetool_client.initialize()
            if not lt_success:
                self.logger.error("Failed to initialize LanguageTool")
                return False
            
            # Initialize LeoLM if configured
            if self.config.leolm_config:
                leolm_success = await self.leolm_client.initialize()
                if not leolm_success:
                    self.logger.error("Failed to initialize LeoLM")
                    return False
            else:
                self.logger.info("LeoLM not configured, using LanguageTool only")
            
            self._is_initialized = True
            self.logger.info("German Language Analyzer successfully initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize German Language Analyzer: {e}")
            return False
    
    def _ensure_initialized(self):
        """Ensure the analyzer is initialized."""
        if not self._is_initialized:
            raise RuntimeError("German Language Analyzer not initialized. Call initialize() first.")
    
    async def analyze_text_comprehensive(self, text: str, 
                                       generate_explanations: bool = True,
                                       generate_examples: bool = None,
                                       generate_exercises: bool = None) -> ComprehensiveAnalysis:
        """Perform comprehensive analysis of German text."""
        self._ensure_initialized()
        
        generate_examples = generate_examples if generate_examples is not None else self.config.provide_examples
        generate_exercises = generate_exercises if generate_exercises is not None else self.config.generate_exercises
        
        try:
            # Step 1: Grammar analysis with LanguageTool
            self.logger.info("Running grammar analysis...")
            grammar_analysis = await self.languagetool_client.analyze_learning_text(
                text, self.config.difficulty_level
            )
            
            # Step 2: LLM analysis if there are errors
            llm_analysis = None
            explanations = []
            examples = []
            exercises = []
            
            if grammar_analysis["analysis"]["total_issues"] > 0:
                self.logger.info("Running LLM analysis for errors...")
                
                # Analyze text with LeoLM
                llm_analysis = await self.leolm_client.analyze_text(
                    text, 
                    focus_areas=list(grammar_analysis["categories_summary"].keys())
                )
                
                # Generate explanations for critical errors
                if generate_explanations:
                    explanations = await self._generate_error_explanations(grammar_analysis)
                
                # Generate examples for grammar rules
                if generate_examples:
                    examples = await self._generate_grammar_examples(grammar_analysis)
                
                # Generate exercises if requested
                if generate_exercises:
                    exercises = await self._generate_practice_exercises(grammar_analysis)
            
            # Step 3: Learning recommendations
            learning_recommendations = await self._generate_learning_recommendations(grammar_analysis, llm_analysis)
            
            return ComprehensiveAnalysis(
                original_text=text,
                grammar_analysis=grammar_analysis,
                llm_analysis=llm_analysis,
                explanations=explanations,
                examples=examples,
                exercises=exercises,
                learning_recommendations=learning_recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {e}")
            raise
    
    async def quick_check(self, text: str) -> Dict[str, Any]:
        """Quick grammar check and basic feedback."""
        self._ensure_initialized()
        
        grammar_analysis = await self.languagetool_client.check_text(text)
        
        return {
            "original_text": text,
            "has_errors": grammar_analysis.total_errors > 0,
            "error_count": grammar_analysis.total_errors,
            "corrected_text": grammar_analysis.corrected_text,
            "main_issues": list(grammar_analysis.categories_found.keys())[:3],
            "quick_suggestions": [
                match.suggestions[0] if match.suggestions else "Keine Vorschläge"
                for match in grammar_analysis.matches[:3]
            ]
        }
    
    async def explain_grammar_topic(self, topic: str, difficulty: str = None) -> Dict[str, Any]:
        """Generate comprehensive explanation for a grammar topic."""
        self._ensure_initialized()
        
        if not self.config.leolm_config:
            return {
                "topic": topic,
                "error": "LLM not available in this configuration. Use 'fast' or 'default' config for explanations."
            }
        
        difficulty = difficulty or self.config.difficulty_level
        
        # Generate explanation with LeoLM
        explanation = await self.leolm_client.generate_explanation(topic, difficulty)
        
        # Generate examples
        examples = await self.leolm_client.generate_examples(topic, count=3, difficulty=difficulty)
        
        # Generate an exercise
        exercise = await self.leolm_client.generate_exercise(topic, difficulty=difficulty)
        
        return {
            "topic": topic,
            "difficulty": difficulty,
            "explanation": explanation,
            "examples": examples,
            "exercise": exercise,
            "status": "success" if all([explanation.get("success"), examples.get("success"), exercise.get("success")]) else "partial"
        }
    
    async def correct_text_with_explanation(self, text: str) -> Dict[str, Any]:
        """Correct text and provide detailed explanations."""
        self._ensure_initialized()
        
        # Get grammar analysis
        grammar_analysis = await self.languagetool_client.analyze_learning_text(text)
        
        corrections = []
        
        for error in grammar_analysis["critical_errors"] + grammar_analysis["learning_opportunities"]:
            # Get LLM explanation for the error
            if error["suggestions"]:
                explanation_prompt = f"Erkläre den Grammatikfehler: '{error['error_text']}' sollte '{error['suggestions'][0]}' sein. Warum?"
                llm_explanation = await self.leolm_client.analyze_text(explanation_prompt)
                
                corrections.append({
                    "original": error["error_text"],
                    "corrected": error["suggestions"][0],
                    "rule": error["category_german"],
                    "explanation": error["explanation"],
                    "llm_explanation": llm_explanation.get("generated_text", ""),
                    "position": error["position"]
                })
        
        return {
            "original_text": text,
            "corrected_text": grammar_analysis["corrected_text"],
            "corrections": corrections,
            "summary": {
                "total_corrections": len(corrections),
                "main_categories": list(grammar_analysis["categories_summary"].keys()),
                "overall_quality": self._assess_text_quality(grammar_analysis)
            }
        }
    
    async def generate_learning_session(self, topics: List[str], difficulty: str = None) -> Dict[str, Any]:
        """Generate a complete learning session with explanations, examples, and exercises."""
        self._ensure_initialized()
        
        difficulty = difficulty or self.config.difficulty_level
        session_content = []
        
        for topic in topics:
            topic_content = await self.explain_grammar_topic(topic, difficulty)
            session_content.append(topic_content)
        
        # Generate a comprehensive exercise combining all topics
        combined_exercise = await self.leolm_client.generate_exercise(
            f"Kombinierte Übung zu: {', '.join(topics)}",
            exercise_type="mixed",
            difficulty=difficulty
        )
        
        return {
            "topics": topics,
            "difficulty": difficulty,
            "content": session_content,
            "final_exercise": combined_exercise,
            "session_summary": {
                "total_topics": len(topics),
                "estimated_duration": len(topics) * 15,  # 15 minutes per topic
                "difficulty_level": difficulty
            }
        }
    
    async def _generate_error_explanations(self, grammar_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate LLM explanations for grammar errors."""
        explanations = []
        
        # Focus on critical errors first
        for error in grammar_analysis["critical_errors"][:3]:  # Limit to top 3
            if error["rule_id"]:
                explanation = await self.leolm_client.generate_explanation(
                    error["category_german"],
                    difficulty=self.config.difficulty_level,
                    context=f"Fehler: {error['error_text']}"
                )
                
                explanations.append({
                    "error": error,
                    "explanation": explanation
                })
        
        return explanations
    
    async def _generate_grammar_examples(self, grammar_analysis: Dict[str, Any]) -> List[str]:
        """Generate examples for the grammar issues found."""
        examples = []
        
        # Get unique categories
        categories = list(grammar_analysis["categories_summary"].keys())[:2]  # Limit to 2 categories
        
        for category in categories:
            if category in ["GRAMMAR", "CASE_AGREEMENT"]:
                example_result = await self.leolm_client.generate_examples(
                    category, count=2, difficulty=self.config.difficulty_level
                )
                if example_result.get("success"):
                    examples.extend(example_result["generated_text"].split("\n"))
        
        return examples
    
    async def _generate_practice_exercises(self, grammar_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate practice exercises based on found errors."""
        exercises = []
        
        categories = list(grammar_analysis["categories_summary"].keys())[:2]
        
        for category in categories:
            exercise = await self.leolm_client.generate_exercise(
                category,
                exercise_type="fill_blank",
                difficulty=self.config.difficulty_level
            )
            
            if exercise.get("success"):
                exercises.append({
                    "category": category,
                    "exercise": exercise
                })
        
        return exercises
    
    async def _generate_learning_recommendations(self, grammar_analysis: Dict[str, Any], 
                                               llm_analysis: Optional[Dict[str, Any]]) -> List[str]:
        """Generate personalized learning recommendations."""
        recommendations = []
        
        # Based on error patterns
        error_count = grammar_analysis["analysis"]["total_issues"]
        
        if error_count == 0:
            recommendations.append("Ausgezeichnet! Ihr Text ist grammatikalisch korrekt.")
            recommendations.append("Versuchen Sie komplexere Satzstrukturen zu verwenden.")
        elif error_count <= 2:
            recommendations.append("Gute Arbeit! Nur wenige kleine Fehler.")
            recommendations.append("Achten Sie auf die Details bei der Kasuskongruenz.")
        else:
            recommendations.append("Konzentrieren Sie sich auf die Grundgrammatik.")
            recommendations.append("Üben Sie regelmäßig mit einfacheren Texten.")
        
        # Based on error categories
        if "TYPOS" in grammar_analysis["categories_summary"]:
            recommendations.append("Verwenden Sie eine Rechtschreibprüfung.")
        
        if "GRAMMAR" in grammar_analysis["categories_summary"]:
            recommendations.append("Wiederholen Sie die deutschen Kasusregeln.")
        
        return recommendations
    
    def _assess_text_quality(self, grammar_analysis: Dict[str, Any]) -> str:
        """Assess overall text quality."""
        error_count = grammar_analysis["analysis"]["total_issues"]
        
        if error_count == 0:
            return "Exzellent"
        elif error_count <= 2:
            return "Gut"
        elif error_count <= 5:
            return "Befriedigend"
        else:
            return "Verbesserungsbedürftig"
    
    def get_analyzer_info(self) -> Dict[str, Any]:
        """Get information about the analyzer."""
        return {
            "initialized": self._is_initialized,
            "leolm_info": self.leolm_client.get_model_info() if self._is_initialized else None,
            "languagetool_info": self.languagetool_client.get_tool_info() if self._is_initialized else None,
            "config": {
                "auto_correct": self.config.auto_correct,
                "provide_examples": self.config.provide_examples,
                "generate_exercises": self.config.generate_exercises,
                "difficulty_level": self.config.difficulty_level
            }
        }
    
    async def cleanup(self):
        """Clean up all resources."""
        if self._is_initialized:
            if self.leolm_client:
                await self.leolm_client.cleanup()
            await self.languagetool_client.cleanup()
            self._is_initialized = False
            self.logger.info("German Language Analyzer cleaned up")
