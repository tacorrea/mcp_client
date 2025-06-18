#!/bin/bash

# Simple setup for German Language Learning
echo "🚀 Installing German Language Learning dependencies..."

# Install dependencies
pip install torch transformers language-tool-python

echo "✅ Setup complete!"
echo ""
echo "Quick Start:"
echo "1. python mcp-client/cli.py"
echo "2. mcp> german init"
echo "3. mcp> german check 'Ich bin ein Student.'"
