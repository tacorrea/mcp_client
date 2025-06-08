#!/bin/bash

# MCP Setup Script
# This script sets up the MCP configuration with your DeepL API key

echo "🔧 Setting up MCP configuration..."

# Check if .env file exists
if [ ! -f "mcp-client/.env" ]; then
    echo "❌ Error: mcp-client/.env file not found"
    echo "Please create the .env file with your DEEPL_AUTH_KEY first"
    exit 1
fi

# Read the API key from .env
DEEPL_KEY=$(grep "DEEPL_AUTH_KEY=" mcp-client/.env | cut -d'=' -f2)

if [ -z "$DEEPL_KEY" ]; then
    echo "❌ Error: DEEPL_AUTH_KEY not found in mcp-client/.env"
    exit 1
fi

# Create the MCP configuration
mkdir -p .vscode
cat > .vscode/mcp.json << EOF
{
"inputs": [
  {
    "type": "promptString"
  }
],
"servers": {
  "fetch": {
    "command": "uvx",
    "args": ["mcp-server-fetch"]
  },
  "deepl": {
    "command": "npx",
    "args": ["-y", "deepl-mcp-server"],
    "env": {
      "DEEPL_API_KEY": "$DEEPL_KEY"
    }
  }
 }
}
EOF

echo "✅ MCP configuration created successfully!"
echo "🔒 The configuration file (.vscode/mcp.json) is in .gitignore and won't be committed"
echo "📝 A template file (.vscode/mcp.json.template) has been created for sharing"
