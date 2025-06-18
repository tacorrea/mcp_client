#!/usr/bin/env python3
"""Simple test for German Language Learning integration."""

import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_imports():
    """Test basic imports."""
    try:
        from client.german_llm.config import get_config
        from client.german_llm.cli import handle_german_command
        print("✅ Imports working")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_dependencies():
    """Test dependencies."""
    deps = ["torch", "transformers", "language_tool_python"]
    missing = []
    
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} missing")
            missing.append(dep)
    
    return len(missing) == 0

if __name__ == "__main__":
    print("🚀 German Language Learning Test")
    print("=" * 30)
    
    imports_ok = test_imports()
    deps_ok = test_dependencies()
    
    if imports_ok and deps_ok:
        print("\n✅ All tests passed! Ready to use.")
    else:
        print("\n❌ Some tests failed. Run: pip install torch transformers language-tool-python")
