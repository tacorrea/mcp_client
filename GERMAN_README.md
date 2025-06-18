# German Language Learning Integration

Simple integration of LeoLM and LanguageTool for German language analysis.

## Setup

```bash
# Install dependencies
pip install torch transformers language-tool-python

# Or use the setup script
./setup-german-llm.sh
```

## Usage

```bash
# Start CLI
python mcp-client/cli.py

# Initialize (grammar checking only - fast!)
mcp> german init grammar-only

# Check text
mcp> german check 'Ich bin ein Student.'

# For explanations, use full version
mcp> german init default
mcp> german explain 'deutsche Artikel'
```

## Commands

- `german init [grammar-only|fast|default]` - Initialize analyzer
- `german check 'text'` - Quick grammar check  
- `german explain 'topic'` - Explain grammar topic (needs fast/default)
- `german status` - Show status

## Configurations

- **grammar-only** - Just LanguageTool (fast, no model download)
- **fast** - Small LLM + LanguageTool (medium speed)
- **default** - Full LLM + LanguageTool (slow, best quality)

## Features

- **LeoLM**: German language model for explanations and examples
- **LanguageTool**: Grammar checking and corrections
- **Simple CLI**: Integrated with your MCP client

## Test

```bash
python mcp-client/client/test/test-german-integration.py
```
