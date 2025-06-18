# German Language Learning Integration

This integration adds comprehensive German language learning capabilities to your MCP client using:
- **LeoLM**: State-of-the-art German language model for generating explanations, examples, and exercises
- **LanguageTool**: Advanced grammar checking and rule-based feedback for German text

## Features

### Core Capabilities
- **Grammar Checking**: Advanced German grammar analysis with detailed feedback
- **Text Correction**: Automatic correction with explanations
- **Grammar Explanations**: AI-generated explanations for German grammar rules
- **Example Generation**: Context-appropriate example sentences
- **Exercise Creation**: Interactive grammar exercises
- **Learning Sessions**: Structured learning content for multiple topics

### Educational Focus
- **Rule-based Feedback**: Detailed explanations of grammar rules
- **Difficulty Levels**: Beginner, intermediate, and advanced content
- **Learning Recommendations**: Personalized suggestions based on error patterns
- **Comprehensive Analysis**: Multi-layered text analysis combining AI and rule-based systems

## Quick Start

### 1. Setup
```bash
# Run the setup script
./setup-german-llm.sh

# Or manual setup:
source venv/bin/activate
pip install -e .
```

### 2. Initialize and Test
```bash
# Start the CLI
python cli.py

# Initialize German analyzer
mcp> german init

# Test with a simple check
mcp> german check 'Ich bin ein Student und ich lerne deutsche.'
```

### 3. Basic Commands
```bash
# Quick grammar check
mcp> german check 'Der Lehrer geben uns viele Hausaufgaben.'

# Comprehensive analysis
mcp> german analyze 'Ich gehe zu der Schule jeden Tag.'

# Grammar explanation
mcp> german explain 'deutsche Kasuskongruenz'

# Text correction with explanations
mcp> german correct 'Die Kinder spielt im Garten.'
```

## Configuration Options

### Predefined Configurations

| Configuration | Use Case | Model Size | Features | Initialization Time |
|--------------|----------|------------|----------|-------------------|
| `default` | General use | Medium | Balanced | ~5 minutes |
| `fast` | Quick testing | Small | Basic | ~2 minutes |
| `comprehensive` | Best quality | Large | All features | ~10 minutes |
| `beginner` | Language learners | Medium | Learner-focused | ~5 minutes |

### Usage Examples
```bash
# Fast setup for testing
mcp> german init fast

# Full features for comprehensive analysis
mcp> german init comprehensive

# Optimized for beginners
mcp> german init beginner
```

### Custom Configuration
Create custom configurations by modifying `.env`:

```bash
# LeoLM Settings
LEOLM_MODEL_NAME=LeoLM/leo-hessianai-7b-chat
LEOLM_DEVICE=auto  # auto, cpu, cuda
LEOLM_MAX_LENGTH=2048
LEOLM_TEMPERATURE=0.7

# LanguageTool Settings
LANGUAGETOOL_LANGUAGE=de-DE  # de-DE, de-AT, de-CH
LANGUAGETOOL_MOTHER_TONGUE=en  # User's native language

# Analyzer Settings
GERMAN_ANALYZER_DIFFICULTY=intermediate  # beginner, intermediate, advanced
GERMAN_ANALYZER_PROVIDE_EXAMPLES=true
GERMAN_ANALYZER_GENERATE_EXERCISES=false
```

## Command Reference

### Initialization
```bash
german init [config]          # Initialize with configuration
german status                 # Check analyzer status
german cleanup                # Free up resources
```

### Text Analysis
```bash
german check 'text'           # Quick grammar check
german analyze 'text'         # Comprehensive analysis
german correct 'text'         # Correction with explanations
```

### Learning Tools
```bash
german explain 'topic'        # Explain grammar topic
german session topic1,topic2  # Create learning session
```

### Example Usage
```bash
# Grammar checking
mcp> german check 'Ich gehe zu der Universität.'
❌ Error found: 'der' should be 'die'

# Comprehensive analysis
mcp> german analyze 'Der Mann gehen zu seine Haus.'
📊 Found 3 issues:
   - Verb agreement error: 'gehen' → 'geht'
   - Article error: 'seine' → 'seinem'
   - Article error: 'der' → 'dem'

# Grammar explanation
mcp> german explain 'deutsche Artikel'
📚 Explanation: Die deutschen Artikel (der, die, das) ändern sich je nach Kasus...

# Learning session
mcp> german session 'deutsche Artikel,Kasuskongruenz'
🎓 Creating 30-minute learning session...
```

## Architecture

### Component Overview
```
German Language Analyzer
├── LeoLM Client          # AI-powered text generation
│   ├── Grammar explanations
│   ├── Example generation
│   └── Exercise creation
├── LanguageTool Client   # Rule-based grammar checking
│   ├── Error detection
│   ├── Rule explanations
│   └── Correction suggestions
└── Integration Layer     # Orchestrates both systems
    ├── Comprehensive analysis
    ├── Learning recommendations
    └── Educational content
```

### LeoLM Integration
- **Model**: LeoLM (Leo Language Model) - German-optimized
- **Tasks**: Explanations, examples, exercises
- **Strengths**: Natural language generation, contextual understanding
- **Configuration**: Model size, temperature, max length

### LanguageTool Integration
- **Engine**: Rule-based German grammar checker
- **Tasks**: Error detection, rule identification, corrections
- **Strengths**: Precise grammar rules, detailed feedback
- **Configuration**: Language variant, enabled/disabled rules

## Programming Interface

### Python API Usage
```python
from client.german_llm import GermanLanguageAnalyzer
from client.german_llm.config import get_named_config

# Initialize with configuration
config = get_named_config("comprehensive")
analyzer = GermanLanguageAnalyzer(config)

# Initialize (downloads models on first run)
await analyzer.initialize()

# Quick check
result = await analyzer.quick_check("Ich bin ein Student.")

# Comprehensive analysis
analysis = await analyzer.analyze_text_comprehensive(
    "Der Lehrer geben uns Hausaufgaben.",
    generate_explanations=True,
    generate_examples=True
)

# Grammar explanation
explanation = await analyzer.explain_grammar_topic(
    "deutsche Kasuskongruenz", 
    difficulty="intermediate"
)

# Cleanup
await analyzer.cleanup()
```

### Custom Configuration
```python
from client.german_llm.config import create_custom_config

# Create custom configuration
config = create_custom_config(
    leolm_temperature=0.8,
    difficulty_level="advanced",
    provide_examples=True,
    generate_exercises=True
)

analyzer = GermanLanguageAnalyzer(config)
```

## Examples and Use Cases

### Language Learning
```bash
# Check homework
mcp> german check 'Ich habe meine Hausaufgaben gemacht.'

# Learn about cases
mcp> german explain 'deutsche Kasus'

# Practice with exercises
mcp> german session 'Nominativ,Akkusativ,Dativ'
```

### Professional Writing
```bash
# Check business email
mcp> german analyze 'Sehr geehrte Damen und Herren, ich schreibe Ihnen bezüglich...'

# Professional configuration
mcp> german init comprehensive
```

### Teaching Support
```bash
# Generate teaching material
mcp> german explain 'Perfekt vs Präteritum'

# Create exercises for students
mcp> german session 'schwache Verben,starke Verben'
```

## Performance and Requirements

### System Requirements
- **Memory**: 8GB RAM recommended (4GB minimum)
- **Storage**: 5GB for model cache
- **Python**: 3.8+ (3.10+ recommended)
- **Network**: Required for initial model download

### Performance Characteristics
| Operation | Time (first run) | Time (cached) | Memory Usage |
|-----------|------------------|---------------|--------------|
| Initialization | 5-15 minutes | 30-60 seconds | 2-4GB |
| Quick check | 1-3 seconds | <1 second | +100MB |
| Comprehensive analysis | 10-30 seconds | 5-15 seconds | +200MB |
| Grammar explanation | 15-45 seconds | 5-20 seconds | +200MB |

### Optimization Tips
1. **Use `fast` configuration** for development/testing
2. **Keep analyzer initialized** for multiple operations
3. **Use CPU for consistency**, GPU for speed
4. **Limit text length** for faster processing

## Troubleshooting

### Common Issues

#### Model Download Fails
```bash
# Check internet connection and storage space
df -h  # Check disk space
# Retry initialization
mcp> german cleanup
mcp> german init
```

#### Out of Memory Errors
```bash
# Use smaller model configuration
mcp> german init fast

# Or limit max length in .env
LEOLM_MAX_LENGTH=1024
```

#### LanguageTool Not Working
```bash
# Install Java (required for LanguageTool)
# macOS:
brew install openjdk

# Check installation
mcp> german status
```

### Debug Mode
```bash
# Enable debug logging
export PYTHONPATH=$PWD
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# Run your commands here
"
```

## Contributing

### Adding New Features
1. **Grammar Rules**: Extend LanguageTool configuration
2. **LLM Prompts**: Modify prompt templates in `leolm_client.py`
3. **Configurations**: Add new configs in `config.py`
4. **Commands**: Extend CLI in `cli.py`

### Testing
```bash
# Run examples
python client/german_llm/examples.py basic
python client/german_llm/examples.py grammar

# Test configurations
python client/german_llm/examples.py config
```

## License and Attribution

- **LeoLM**: Used under Apache 2.0 license
- **LanguageTool**: LGPL license
- **Integration Code**: MIT license

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review example usage in `examples.py`
3. Check system requirements and performance tips
