"""Simple German Language Learning CLI."""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from client.german_llm.german_analyzer import GermanLanguageAnalyzer
from client.german_llm.config import get_config


class GermanLLMCommand:
    """Simple CLI commands for German language learning."""
    
    def __init__(self):
        self.analyzer: Optional[GermanLanguageAnalyzer] = None
        self.logger = logging.getLogger(__name__)
    
    async def init_analyzer(self, config_name: str = "default") -> bool:
        """Initialize the German analyzer."""
        try:
            config = get_config(config_name)
            self.analyzer = GermanLanguageAnalyzer(config)
            
            print("🔄 Initializing German Language Analyzer...")
            success = await self.analyzer.initialize()
            
            if success:
                print("✅ Ready!")
            else:
                print("❌ Failed to initialize")
                
            return success
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def quick_check(self, text: str) -> Dict[str, Any]:
        """Quick grammar check."""
        if not self.analyzer:
            print("❌ Not initialized. Run 'german init' first.")
            return {"error": "Not initialized"}
        
        try:
            result = await self.analyzer.quick_check(text)
            
            print(f"� Text: {text}")
            print(f"Errors: {result['error_count']}")
            if result['has_errors']:
                print(f"Corrected: {result['corrected_text']}")
            else:
                print("✅ No errors found!")
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"error": str(e)}
    
    async def explain_grammar(self, topic: str) -> Dict[str, Any]:
        """Explain a German grammar topic."""
        if not self.analyzer:
            print("❌ Not initialized. Run 'german init' first.")
            return {"error": "Not initialized"}
        
        try:
            result = await self.analyzer.explain_grammar_topic(topic)
            
            if result["status"] == "success" and result["explanation"].get("success"):
                print(f"📚 {topic}:")
                print(result["explanation"]["generated_text"])
            else:
                print("❌ Failed to generate explanation")
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"error": str(e)}


# Global instance
german_llm = GermanLLMCommand()


async def handle_german_command(args: List[str]) -> Dict[str, Any]:
    """Handle German language learning commands."""
    if not args:
        print("German Commands:")
        print("  german init [grammar-only|fast|default] - Initialize analyzer")
        print("  german check 'text'                    - Quick grammar check")
        print("  german explain 'topic'                 - Explain grammar topic")
        print("  german status                          - Show status")
        print("")
        print("Configs:")
        print("  grammar-only - Just LanguageTool (fast, no LLM)")
        print("  fast         - Small LLM + LanguageTool")  
        print("  default      - Full LLM + LanguageTool")
        return {"status": "help"}
    
    command = args[0].lower()
    
    if command == "init":
        config_name = args[1] if len(args) > 1 else "default"
        success = await german_llm.init_analyzer(config_name)
        return {"command": "init", "success": success}
    
    elif command == "check":
        if len(args) < 2:
            print("Usage: german check 'your text here'")
            return {"error": "No text"}
        text = " ".join(args[1:]).strip("'\"")
        return await german_llm.quick_check(text)
    
    elif command == "explain":
        if len(args) < 2:
            print("Usage: german explain 'grammar topic'")
            return {"error": "No topic"}
        topic = " ".join(args[1:]).strip("'\"")
        return await german_llm.explain_grammar(topic)
    
    elif command == "status":
        if german_llm.analyzer:
            print("✅ German analyzer initialized")
        else:
            print("❌ German analyzer not initialized")
        return {"initialized": german_llm.analyzer is not None}
    
    else:
        print(f"Unknown command: {command}")
        return {"error": f"Unknown command: {command}"}
