# LLM Assistant

A versatile chatbot implementation powered by Large Language Models with multiple deployment options.

## Features

- 💬 Interactive chat interface using Streamlit
- 🤖 Amazon Bedrock integration (Meta's Llama 4)
- 🔄 Persistent conversation memory
- 📊 LangSmith monitoring and tracing
- 🌐 Language control support
- 🔍 Error handling and graceful fallbacks

## Quick Start

### Prerequisites
- Python 3.9+
- AWS account with Bedrock access
- LangSmith account (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/llm_assistant.git
cd llm_assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Required Packages

```pip-requirements
streamlit>=1.31.0    # Web interface framework
langchain>=0.1.0     # LLM integration framework
langgraph>=0.0.21    # Conversation flow control
langchain-community>=0.0.10  # Community extensions
langsmith>=0.0.77    # Monitoring and tracing
boto3>=1.34.0        # AWS SDK for Python
python-dotenv>=1.0.0 # Environment variable management
typing-extensions>=4.8.0  # Type hints support
botocore>=1.34.0     # AWS SDK core
```

### Configuration

1. Set up your secrets in `.streamlit/secrets.toml`:
```toml
aws_region = "<YOUR_AWS_REGION>"
bedrock_model_id = "<YOUR_BEDROCK_MODEL_ID>"
LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"
```

2. Run the application:
```bash
streamlit run app.py
```

## Architecture

- Built with LangChain and LangGraph
- Streamlit for web interface
- Amazon Bedrock for LLM access
- LangSmith for monitoring

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

This is an open source project.