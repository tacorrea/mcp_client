#!/usr/bin/env python3
"""
Quick test script for German Language Learning integration.
Run this to verify that everything is working correctly.
"""

import asyncio
import sys
import os
import logging

# Add the mcp-client directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp-client'))

from client.german_llm.config import get_named_config, validate_config


async def test_configuration():
    """Test configuration loading and validation."""
    print("🔧 Testing Configuration...")
    
    configs = ["default", "fast", "comprehensive", "beginner"]
    
    for config_name in configs:
        try:
            config = get_named_config(config_name)
            issues = validate_config(config)
            
            if issues:
                print(f"❌ {config_name}: {issues}")
            else:
                print(f"✅ {config_name}: Configuration valid")
        except Exception as e:
            print(f"❌ {config_name}: Error loading - {e}")
    
    print()


async def test_imports():
    """Test that all modules can be imported."""
    print("📦 Testing Imports...")
    
    modules = [
        ("LeoLMClient", "client.german_llm.leolm_client"),
        ("LanguageToolClient", "client.german_llm.languagetool_client"),
        ("GermanLanguageAnalyzer", "client.german_llm.german_analyzer"),
        ("Config", "client.german_llm.config"),
        ("CLI", "client.german_llm.cli")
    ]
    
    for name, module_path in modules:
        try:
            __import__(module_path)
            print(f"✅ {name}: Import successful")
        except ImportError as e:
            print(f"❌ {name}: Import failed - {e}")
        except Exception as e:
            print(f"⚠️  {name}: Import warning - {e}")
    
    print()


async def test_dependencies():
    """Test that required dependencies are available."""
    print("📚 Testing Dependencies...")
    
    dependencies = [
        ("PyTorch", "torch"),
        ("Transformers", "transformers"),
        ("LanguageTool", "language_tool_python"),
        ("Accelerate", "accelerate"),
        ("SentencePiece", "sentencepiece"),
        ("Requests", "requests"),
        ("AsyncIO HTTP", "aiohttp")
    ]
    
    for name, module in dependencies:
        try:
            imported = __import__(module)
            version = getattr(imported, '__version__', 'Unknown')
            print(f"✅ {name}: Available (version {version})")
        except ImportError:
            print(f"❌ {name}: Not installed")
    
    print()


async def test_basic_functionality():
    """Test basic functionality without model loading."""
    print("⚡ Testing Basic Functionality...")
    
    try:
        from client.german_llm.german_analyzer import GermanLanguageAnalyzer
        from client.german_llm.config import get_named_config
        
        # Test analyzer creation
        config = get_named_config("fast")
        analyzer = GermanLanguageAnalyzer(config)
        print("✅ Analyzer creation: Success")
        
        # Test configuration info
        info = analyzer.get_analyzer_info()
        print(f"✅ Config info: {info['config']['difficulty_level']} difficulty")
        
        # Test cleanup (without initialization)
        await analyzer.cleanup()
        print("✅ Cleanup: Success")
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
    
    print()


async def test_cli_integration():
    """Test CLI integration."""
    print("🖥️  Testing CLI Integration...")
    
    try:
        from client.german_llm.cli import handle_german_command
        
        # Test help command
        result = await handle_german_command([])
        if result.get("status") == "help_shown":
            print("✅ CLI help: Working")
        else:
            print("⚠️  CLI help: Unexpected result")
        
        # Test status command (should work without initialization)
        try:
            result = await handle_german_command(["status"])
            print("✅ CLI status: Working")
        except Exception as e:
            print(f"⚠️  CLI status: {e}")
        
    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
    
    print()


async def main():
    """Run all tests."""
    print("🚀 German Language Learning Integration Test")
    print("=" * 50)
    print()
    
    # Run tests
    await test_configuration()
    await test_imports()
    await test_dependencies()
    await test_basic_functionality()
    await test_cli_integration()
    
    print("🎯 Test Summary")
    print("=" * 20)
    print("If all tests show ✅, your integration is ready!")
    print()
    print("Next steps:")
    print("1. Run: python cli.py")
    print("2. Initialize: mcp> german init fast")
    print("3. Test: mcp> german check 'Ich bin ein Student.'")
    print()
    print("⚠️  Note: First initialization downloads models (~5-15 minutes)")


if __name__ == "__main__":
    asyncio.run(main())
