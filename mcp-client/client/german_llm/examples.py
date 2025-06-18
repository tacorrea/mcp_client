"""
Example usage of the German Language Learning system.

This script demonstrates how to use LeoLM and LanguageTool
for comprehensive German language analysis and learning.
"""

import asyncio
import sys
import os
import logging

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.german_llm.german_analyzer import GermanLanguageAnalyzer
from client.german_llm.config import (
    get_config, 
    get_named_config, 
    create_custom_config,
    validate_config
)


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def basic_example():
    """Basic example of text analysis."""
    print("=== Basic German Text Analysis Example ===\n")
    
    # Create analyzer with default configuration
    analyzer = GermanLanguageAnalyzer()
    
    try:
        # Initialize the analyzer (this may take a few minutes for first-time model download)
        print("Initializing German Language Analyzer (this may take a few minutes)...")
        success = await analyzer.initialize()
        
        if not success:
            print("Failed to initialize analyzer")
            return
        
        print("✅ Analyzer initialized successfully!\n")
        
        # Example German text with some errors
        test_text = """
        Ich bin ein Student und ich lerne deutsche Sprache. 
        Der Lehrer geben uns viele Hausaufgaben jeden Tag.
        Manchmal ist es schwer, aber ich mag die deutsche Kultur sehr.
        """
        
        print(f"📝 Analyzing text: {test_text.strip()}\n")
        
        # Quick check
        print("--- Quick Check ---")
        quick_result = await analyzer.quick_check(test_text)
        print(f"Has errors: {quick_result['has_errors']}")
        print(f"Error count: {quick_result['error_count']}")
        print(f"Corrected text: {quick_result['corrected_text']}")
        print(f"Main issues: {quick_result['main_issues']}")
        print()
        
        # Comprehensive analysis
        print("--- Comprehensive Analysis ---")
        comprehensive = await analyzer.analyze_text_comprehensive(
            test_text,
            generate_explanations=True,
            generate_examples=True
        )
        
        print(f"Total issues found: {comprehensive.grammar_analysis['analysis']['total_issues']}")
        print(f"Critical errors: {comprehensive.grammar_analysis['analysis']['critical_errors']}")
        print(f"Learning opportunities: {comprehensive.grammar_analysis['analysis']['learning_opportunities']}")
        print()
        
        if comprehensive.explanations:
            print("--- Error Explanations ---")
            for i, explanation in enumerate(comprehensive.explanations[:2], 1):
                error = explanation['error']
                print(f"{i}. Error: '{error['error_text']}'")
                print(f"   Category: {error['category_german']}")
                print(f"   Suggestion: {error['suggestions'][0] if error['suggestions'] else 'No suggestion'}")
                print(f"   Explanation: {error['explanation']}")
                print()
        
        if comprehensive.learning_recommendations:
            print("--- Learning Recommendations ---")
            for i, rec in enumerate(comprehensive.learning_recommendations, 1):
                print(f"{i}. {rec}")
            print()
        
    finally:
        await analyzer.cleanup()


async def grammar_explanation_example():
    """Example of grammar topic explanation."""
    print("=== Grammar Explanation Example ===\n")
    
    # Use fast configuration for quicker initialization
    config = get_named_config("fast")
    analyzer = GermanLanguageAnalyzer(config)
    
    try:
        print("Initializing analyzer with fast configuration...")
        success = await analyzer.initialize()
        
        if not success:
            print("Failed to initialize analyzer")
            return
        
        print("✅ Analyzer initialized!\n")
        
        # Explain a grammar topic
        topic = "deutsche Kasuskongruenz"
        print(f"📚 Explaining grammar topic: {topic}\n")
        
        explanation = await analyzer.explain_grammar_topic(topic, difficulty="intermediate")
        
        if explanation["status"] == "success":
            print("--- Explanation ---")
            if explanation["explanation"].get("success"):
                print(explanation["explanation"]["generated_text"])
            print()
            
            print("--- Examples ---")
            if explanation["examples"].get("success"):
                print(explanation["examples"]["generated_text"])
            print()
            
            print("--- Practice Exercise ---")
            if explanation["exercise"].get("success"):
                print(explanation["exercise"]["generated_text"])
            print()
        else:
            print("❌ Failed to generate complete explanation")
        
    finally:
        await analyzer.cleanup()


async def text_correction_example():
    """Example of text correction with explanations."""
    print("=== Text Correction with Explanations Example ===\n")
    
    analyzer = GermanLanguageAnalyzer()
    
    try:
        print("Initializing analyzer...")
        success = await analyzer.initialize()
        
        if not success:
            print("Failed to initialize analyzer")
            return
        
        print("✅ Analyzer initialized!\n")
        
        # Text with various errors
        error_text = "Der Mann gehen zu der Haus von seine Freund."
        
        print(f"📝 Original text: {error_text}\n")
        
        correction_result = await analyzer.correct_text_with_explanation(error_text)
        
        print("--- Corrections ---")
        print(f"Corrected text: {correction_result['corrected_text']}\n")
        
        for i, correction in enumerate(correction_result['corrections'], 1):
            print(f"{i}. '{correction['original']}' → '{correction['corrected']}'")
            print(f"   Rule: {correction['rule']}")
            print(f"   Explanation: {correction['explanation']}")
            if correction['llm_explanation']:
                print(f"   LLM Explanation: {correction['llm_explanation'][:200]}...")
            print()
        
        print("--- Summary ---")
        summary = correction_result['summary']
        print(f"Total corrections: {summary['total_corrections']}")
        print(f"Main categories: {summary['main_categories']}")
        print(f"Overall quality: {summary['overall_quality']}")
        print()
        
    finally:
        await analyzer.cleanup()


async def learning_session_example():
    """Example of a complete learning session."""
    print("=== Learning Session Example ===\n")
    
    # Use beginner configuration
    config = get_named_config("beginner")
    analyzer = GermanLanguageAnalyzer(config)
    
    try:
        print("Initializing analyzer for beginner level...")
        success = await analyzer.initialize()
        
        if not success:
            print("Failed to initialize analyzer")
            return
        
        print("✅ Analyzer initialized!\n")
        
        # Create a learning session with multiple topics
        topics = ["deutsche Artikel", "Nominativ und Akkusativ"]
        
        print(f"🎓 Creating learning session for topics: {topics}\n")
        
        session = await analyzer.generate_learning_session(topics, difficulty="beginner")
        
        print("--- Learning Session ---")
        print(f"Topics: {session['topics']}")
        print(f"Difficulty: {session['difficulty']}")
        print(f"Estimated duration: {session['session_summary']['estimated_duration']} minutes\n")
        
        for i, topic_content in enumerate(session['content'], 1):
            print(f"=== Topic {i}: {topic_content['topic']} ===")
            
            if topic_content['explanation'].get('success'):
                print("Explanation:")
                print(topic_content['explanation']['generated_text'][:300] + "...\n")
            
            if topic_content['examples'].get('success'):
                print("Examples:")
                print(topic_content['examples']['generated_text'][:200] + "...\n")
        
        if session['final_exercise'].get('success'):
            print("=== Final Combined Exercise ===")
            print(session['final_exercise']['generated_text'][:300] + "...")
            print()
        
    finally:
        await analyzer.cleanup()


async def configuration_example():
    """Example of different configurations."""
    print("=== Configuration Examples ===\n")
    
    # Show different configurations
    configs = {
        "Default": get_config("default"),
        "Fast": get_config("fast"),
        "Comprehensive": get_config("comprehensive"),
        "Beginner": get_config("beginner")
    }
    
    for name, config in configs.items():
        print(f"--- {name} Configuration ---")
        print(f"Model: {config.leolm_config.model_name}")
        print(f"Device: {config.leolm_config.device}")
        print(f"Max length: {config.leolm_config.max_length}")
        print(f"Temperature: {config.leolm_config.temperature}")
        print(f"Language: {config.languagetool_config.language}")
        print(f"Difficulty: {config.difficulty_level}")
        print(f"Auto correct: {config.auto_correct}")
        print(f"Provide examples: {config.provide_examples}")
        print(f"Generate exercises: {config.generate_exercises}")
        
        # Validate configuration
        issues = validate_config(config)
        if issues:
            print(f"⚠️  Issues: {issues}")
        else:
            print("✅ Configuration valid")
        print()
    
    # Custom configuration example
    print("--- Custom Configuration ---")
    custom_config = create_custom_config(
        leolm_temperature=0.8,
        difficulty_level="advanced",
        provide_examples=True,
        generate_exercises=True
    )
    
    print(f"Custom temperature: {custom_config.leolm_config.temperature}")
    print(f"Custom difficulty: {custom_config.difficulty_level}")
    print()


async def main():
    """Main function to run examples."""
    if len(sys.argv) > 1:
        example = sys.argv[1].lower()
        
        examples = {
            "basic": basic_example,
            "grammar": grammar_explanation_example,
            "correction": text_correction_example,
            "session": learning_session_example,
            "config": configuration_example
        }
        
        if example in examples:
            await examples[example]()
        else:
            print(f"Unknown example: {example}")
            print(f"Available examples: {list(examples.keys())}")
    else:
        print("German Language Learning System Examples")
        print("=====================================\n")
        print("Available examples:")
        print("  python examples.py basic      - Basic text analysis")
        print("  python examples.py grammar    - Grammar explanation")
        print("  python examples.py correction - Text correction")
        print("  python examples.py session    - Learning session")
        print("  python examples.py config     - Configuration examples")
        print("\nNote: First run may take several minutes to download models.")


if __name__ == "__main__":
    asyncio.run(main())
