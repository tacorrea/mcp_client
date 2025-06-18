"""Simple configuration for German Language Learning."""

from client.german_llm.leolm_client import LeoLMConfig
from client.german_llm.languagetool_client import LanguageToolConfig
from client.german_llm.german_analyzer import GermanAnalyzerConfig


# Simple predefined configurations
CONFIGS = {
    "grammar-only": GermanAnalyzerConfig(
        leolm_config=None,  # No LLM, just grammar checking
        languagetool_config=LanguageToolConfig(language="de-DE"),
        provide_examples=False,
        generate_exercises=False
    ),
    
    "fast": GermanAnalyzerConfig(
        leolm_config=LeoLMConfig(
            model_name="microsoft/DialoGPT-medium",  # Smaller, more stable model
            device="cpu",
            max_length=512,
            temperature=0.7
        ),
        languagetool_config=LanguageToolConfig(language="de-DE"),
        provide_examples=False,
        generate_exercises=False
    ),
    
    "default": GermanAnalyzerConfig(
        leolm_config=LeoLMConfig(
            model_name="LeoLM/leo-hessianai-7b-chat",
            device="cpu",  # Use CPU for stability
            max_length=1024,
            temperature=0.7
        ),
        languagetool_config=LanguageToolConfig(language="de-DE"),
        provide_examples=True,
        generate_exercises=False
    )
}


def get_config(name: str = "default") -> GermanAnalyzerConfig:
    """Get configuration by name."""
    if name not in CONFIGS:
        return CONFIGS["default"]
    return CONFIGS[name]
