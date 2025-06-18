"""
LanguageTool Client - German Grammar and Style Checking.

This module provides integration with LanguageTool for:
- Grammar checking German text
- Style analysis and suggestions
- Detailed rule-based feedback
- Language learning focused corrections
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import language_tool_python
from language_tool_python import LanguageTool


@dataclass
class LanguageToolConfig:
    """Configuration for LanguageTool."""
    language: str = "de-DE"  # German (Germany)
    motherTongue: Optional[str] = None  # User's native language for better suggestions
    enabled_rules: Optional[List[str]] = None
    disabled_rules: Optional[List[str]] = None
    enabled_categories: Optional[List[str]] = None
    disabled_categories: Optional[List[str]] = None


@dataclass
class GrammarMatch:
    """Represents a grammar error or suggestion."""
    offset: int
    length: int
    rule_id: str
    category: str
    message: str
    short_message: str
    suggestions: List[str]
    context: str
    error_text: str
    rule_description: Optional[str] = None
    urls: Optional[List[str]] = None


@dataclass
class GrammarAnalysis:
    """Complete analysis of a text's grammar."""
    text: str
    matches: List[GrammarMatch]
    total_errors: int
    categories_found: Dict[str, int]
    suggestions_count: int
    corrected_text: str


class LanguageToolClient:
    """Client for LanguageTool German grammar checking."""
    
    def __init__(self, config: Optional[LanguageToolConfig] = None):
        self.config = config or LanguageToolConfig()
        self.logger = logging.getLogger(__name__)
        self.tool: Optional[LanguageTool] = None
        self._is_initialized = False
        
        # German grammar categories for educational purposes
        self.grammar_categories = {
            "TYPOS": "Rechtschreibfehler",
            "GRAMMAR": "Grammatikfehler",
            "PUNCTUATION": "Zeichensetzung",
            "STYLE": "Stil und Ausdruck",
            "CONFUSED_WORDS": "Verwechselte Wörter",
            "REDUNDANCY": "Redundanz",
            "GENDER_NEUTRALITY": "Geschlechtergerechte Sprache",
            "COLLOQUIALISMS": "Umgangssprache",
            "REGIONALISMS": "Regionalismen"
        }
    
    async def initialize(self) -> bool:
        """Initialize LanguageTool."""
        try:
            self.logger.info(f"Initializing LanguageTool for language: {self.config.language}")
            
            # Initialize LanguageTool with configuration
            kwargs = {"language": self.config.language}
            if self.config.motherTongue:
                kwargs["motherTongue"] = self.config.motherTongue
                
            self.tool = LanguageTool(**kwargs)
            
            # Configure enabled/disabled rules if specified
            if self.config.enabled_rules:
                self.tool.enabled_rules = set(self.config.enabled_rules)
            
            if self.config.disabled_rules:
                self.tool.disabled_rules = set(self.config.disabled_rules)
            
            if self.config.enabled_categories:
                self.tool.enabled_categories = set(self.config.enabled_categories)
                
            if self.config.disabled_categories:
                self.tool.disabled_categories = set(self.config.disabled_categories)
            
            self._is_initialized = True
            self.logger.info("LanguageTool successfully initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LanguageTool: {e}")
            return False
    
    def _ensure_initialized(self):
        """Ensure LanguageTool is initialized."""
        if not self._is_initialized or not self.tool:
            raise RuntimeError("LanguageTool not initialized. Call initialize() first.")
    
    async def check_text(self, text: str, focus_categories: Optional[List[str]] = None) -> GrammarAnalysis:
        """Check German text for grammar, style, and spelling errors."""
        self._ensure_initialized()
        
        try:
            # Get matches from LanguageTool
            matches = self.tool.check(text)
            
            # Convert to our format
            grammar_matches = []
            categories_found = {}
            
            for match in matches:
                # Filter by focus categories if specified
                if focus_categories and match.category not in focus_categories:
                    continue
                
                # Create our grammar match object
                grammar_match = GrammarMatch(
                    offset=match.offset,
                    length=match.errorLength,
                    rule_id=match.ruleId,
                    category=match.category,
                    message=match.message,
                    short_message=match.message,
                    suggestions=match.replacements[:5],  # Limit suggestions
                    context=match.context,
                    error_text=text[match.offset:match.offset + match.errorLength],
                    rule_description=self._get_rule_description(match.ruleId),
                    urls=getattr(match, 'urls', None)
                )
                
                grammar_matches.append(grammar_match)
                
                # Count categories
                category = match.category
                categories_found[category] = categories_found.get(category, 0) + 1
            
            # Generate corrected text
            corrected_text = self._apply_corrections(text, grammar_matches)
            
            return GrammarAnalysis(
                text=text,
                matches=grammar_matches,
                total_errors=len(grammar_matches),
                categories_found=categories_found,
                suggestions_count=sum(len(m.suggestions) for m in grammar_matches),
                corrected_text=corrected_text
            )
            
        except Exception as e:
            self.logger.error(f"Text checking failed: {e}")
            raise
    
    async def check_sentence(self, sentence: str) -> Dict[str, Any]:
        """Check a single sentence and provide detailed feedback."""
        analysis = await self.check_text(sentence)
        
        return {
            "sentence": sentence,
            "has_errors": analysis.total_errors > 0,
            "error_count": analysis.total_errors,
            "errors": [
                {
                    "type": match.category,
                    "rule": match.rule_id,
                    "message": match.message,
                    "error_text": match.error_text,
                    "suggestions": match.suggestions,
                    "position": {"start": match.offset, "end": match.offset + match.length}
                }
                for match in analysis.matches
            ],
            "corrected": analysis.corrected_text,
            "categories": analysis.categories_found
        }
    
    async def get_grammar_explanation(self, rule_id: str) -> Dict[str, Any]:
        """Get detailed explanation for a specific grammar rule."""
        self._ensure_initialized()
        
        try:
            # Get rule description
            description = self._get_rule_description(rule_id)
            category = self._get_rule_category(rule_id)
            
            return {
                "rule_id": rule_id,
                "category": category,
                "category_german": self.grammar_categories.get(category, category),
                "description": description,
                "explanation": self._get_educational_explanation(rule_id),
                "examples": self._get_rule_examples(rule_id)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get grammar explanation: {e}")
            return {
                "rule_id": rule_id,
                "error": str(e)
            }
    
    async def analyze_learning_text(self, text: str, difficulty_level: str = "intermediate") -> Dict[str, Any]:
        """Analyze text specifically for language learning purposes."""
        analysis = await self.check_text(text)
        
        # Categorize errors by learning importance
        critical_errors = []
        learning_opportunities = []
        style_suggestions = []
        
        for match in analysis.matches:
            if match.category in ["TYPOS", "GRAMMAR"]:
                critical_errors.append(match)
            elif match.category in ["STYLE", "REDUNDANCY"]:
                style_suggestions.append(match)
            else:
                learning_opportunities.append(match)
        
        return {
            "text": text,
            "difficulty_level": difficulty_level,
            "analysis": {
                "total_issues": analysis.total_errors,
                "critical_errors": len(critical_errors),
                "learning_opportunities": len(learning_opportunities),
                "style_suggestions": len(style_suggestions)
            },
            "critical_errors": [self._format_error_for_learning(error) for error in critical_errors],
            "learning_opportunities": [self._format_error_for_learning(error) for error in learning_opportunities],
            "style_suggestions": [self._format_error_for_learning(error) for error in style_suggestions],
            "corrected_text": analysis.corrected_text,
            "improvement_suggestions": self._generate_improvement_suggestions(analysis),
            "categories_summary": analysis.categories_found
        }
    
    def _apply_corrections(self, text: str, matches: List[GrammarMatch]) -> str:
        """Apply the first suggestion for each match to create corrected text."""
        if not matches:
            return text
        
        # Sort matches by offset in reverse order to avoid position shifts
        sorted_matches = sorted(matches, key=lambda m: m.offset, reverse=True)
        corrected = text
        
        for match in sorted_matches:
            if match.suggestions:
                # Apply the first suggestion
                start = match.offset
                end = match.offset + match.length
                corrected = corrected[:start] + match.suggestions[0] + corrected[end:]
        
        return corrected
    
    def _format_error_for_learning(self, match: GrammarMatch) -> Dict[str, Any]:
        """Format error information for language learning context."""
        return {
            "error_text": match.error_text,
            "position": {"start": match.offset, "end": match.offset + match.length},
            "category": match.category,
            "category_german": self.grammar_categories.get(match.category, match.category),
            "rule_id": match.rule_id,
            "message": match.message,
            "suggestions": match.suggestions,
            "context": match.context,
            "explanation": self._get_educational_explanation(match.rule_id),
            "severity": self._get_error_severity(match.category)
        }
    
    def _get_rule_description(self, rule_id: str) -> str:
        """Get description for a grammar rule."""
        # This could be expanded with a comprehensive rule database
        rule_descriptions = {
            "GERMAN_SPELLCHECK": "Rechtschreibprüfung",
            "AGREEMENT_ERRORS": "Kongruenzfehler (Subjekt-Prädikat-Übereinstimmung)",
            "CASE_AGREEMENT": "Kasuskongruenz",
            "ARTICLE_MISSING": "Fehlender Artikel",
            "COMMA_COMPOUND_SENTENCE": "Komma in zusammengesetzten Sätzen",
            "WORD_ORDER": "Wortstellung"
        }
        return rule_descriptions.get(rule_id, f"Regel: {rule_id}")
    
    def _get_rule_category(self, rule_id: str) -> str:
        """Get category for a grammar rule."""
        # Simplified category mapping
        if "SPELL" in rule_id:
            return "TYPOS"
        elif "AGREEMENT" in rule_id or "CASE" in rule_id:
            return "GRAMMAR"
        elif "COMMA" in rule_id:
            return "PUNCTUATION"
        else:
            return "GRAMMAR"
    
    def _get_educational_explanation(self, rule_id: str) -> str:
        """Get educational explanation for a rule."""
        explanations = {
            "AGREEMENT_ERRORS": "Das Subjekt und das Prädikat müssen in Person und Numerus übereinstimmen.",
            "CASE_AGREEMENT": "Artikel, Adjektive und Substantive müssen im gleichen Kasus stehen.",
            "ARTICLE_MISSING": "Deutsche Substantive benötigen meist einen Artikel (der, die, das, ein, eine).",
            "COMMA_COMPOUND_SENTENCE": "Hauptsätze werden durch Kommas getrennt."
        }
        return explanations.get(rule_id, "Überprüfen Sie die Grammatikregel.")
    
    def _get_rule_examples(self, rule_id: str) -> List[str]:
        """Get example sentences for a rule."""
        examples = {
            "AGREEMENT_ERRORS": [
                "Falsch: Die Kinder spielt im Garten.",
                "Richtig: Die Kinder spielen im Garten."
            ],
            "CASE_AGREEMENT": [
                "Falsch: Ich gebe der Mann das Buch.",
                "Richtig: Ich gebe dem Mann das Buch."
            ]
        }
        return examples.get(rule_id, [])
    
    def _get_error_severity(self, category: str) -> str:
        """Get severity level for error category."""
        severity_map = {
            "TYPOS": "high",
            "GRAMMAR": "high", 
            "PUNCTUATION": "medium",
            "STYLE": "low",
            "REDUNDANCY": "low"
        }
        return severity_map.get(category, "medium")
    
    def _generate_improvement_suggestions(self, analysis: GrammarAnalysis) -> List[str]:
        """Generate overall improvement suggestions based on analysis."""
        suggestions = []
        
        if analysis.categories_found.get("TYPOS", 0) > 2:
            suggestions.append("Überprüfen Sie die Rechtschreibung sorgfältiger.")
        
        if analysis.categories_found.get("GRAMMAR", 0) > 1:
            suggestions.append("Achten Sie auf Grammatikregeln, besonders Kasuskongruenz.")
        
        if analysis.categories_found.get("PUNCTUATION", 0) > 1:
            suggestions.append("Überprüfen Sie die Kommasetzung in zusammengesetzten Sätzen.")
        
        if len(suggestions) == 0:
            suggestions.append("Gute Arbeit! Der Text ist grammatikalisch korrekt.")
        
        return suggestions
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return ["de-DE", "de-AT", "de-CH"]  # German variants
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about LanguageTool configuration."""
        return {
            "language": self.config.language,
            "motherTongue": self.config.motherTongue,
            "initialized": self._is_initialized,
            "supported_categories": list(self.grammar_categories.keys()),
            "version": language_tool_python.__version__ if hasattr(language_tool_python, '__version__') else "unknown"
        }
    
    async def cleanup(self):
        """Clean up LanguageTool resources."""
        if self.tool:
            self.tool.close()
            self.tool = None
        self._is_initialized = False
        self.logger.info("LanguageTool resources cleaned up")
