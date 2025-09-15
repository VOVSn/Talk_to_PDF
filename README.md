# Chainlit RAG Proof of Concept

This project is a Proof of Concept (PoC) for a Retrieval-Augmented Generation (RAG) application using [Chainlit](https://docs.chainlit.io/get-started/overview).

## Features

- **General Chat**: Engage in conversations using configurable LLMs
- **Document Q&A**: Upload PDF files and ask questions about their content
- **Configurable Settings**: Adjust model, domain expertise, and temperature
- **Clean Architecture**: Separated concerns with core logic and presentation layers

## Project Structure

```
.
├── .gitignore
├── pyproject.toml
├── README.md
└── src/
    ├── main.py              # Entry point - registers Chainlit decorators
    ├── core/
    │   ├── agent.py         # Conversational agent logic
    │   └── rag.py          # RAG chain implementation
    └── presentation/
        ├── callbacks.py     # Message handling (@cl.on_message)
        └── factory.py       # UI setup (@cl.on_chat_start)
```

## Requirements

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Ollama running locally with models (gpt-oss:20b, phi4, etc.)

## Installation with uv (Recommended)

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and navigate to the project**:
   ```bash
   cd chainlit-rag-poc
   ```

3. **Install dependencies and create virtual environment**:
   ```bash
   uv sync
   ```

4. **Ensure Ollama is running** with required models:
   ```bash
   ollama pull gpt-oss:20b
   ollama pull phi4
   ```

## Usage with uv

1. **Run the application**:
   ```bash
   uv run chainlit run src/main.py -w
   ```

2. **Alternative: Activate virtual environment first**:
   ```bash
   # Activate the virtual environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Then run normally
   chainlit run src/main.py -w
   ```

## Installation with pip (Alternative)

1. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Run the application**:
   ```bash
   chainlit run src/main.py -w
   ```

## Usage

1. **Open your browser**:
   Navigate to `http://localhost:8000`

2. **Configure settings**:
   - Choose your preferred model
   - Set domain expertise
   - Adjust temperature for creativity

3. **Start chatting**:
   - Ask general questions for normal conversation
   - Upload a PDF to enable document-specific Q&A

## Development with uv

- **Add new dependencies**:
  ```bash
  uv add package-name
  ```

- **Add development dependencies**:
  ```bash
  uv add --group dev package-name
  ```

- **Run linting**:
  ```bash
  uv run ruff check src/
  uv run ruff format src/
  ```

## Troubleshooting

- **Import errors**: Ensure you're running from the project root
- **Model errors**: Verify Ollama is running and models are available
- **PDF processing**: Check file size (<20MB) and format (PDF only)
- **uv issues**: Make sure you have the latest version of uv installed