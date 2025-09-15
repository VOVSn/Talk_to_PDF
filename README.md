# Chainlit RAG Proof of Concept

This project is a simple Proof of Concept (PoC) for a Retrieval-Augmented Generation (RAG) application using [Chainlit](https://docs.chainlit.io/get-started/overview).

It demonstrates how to build a chat application that can:
- Engage in a general conversation using a Large Language Model (LLM).
- Augment its knowledge with information from an uploaded PDF file.
- Allow users to configure settings like the model and temperature.

## Project Structure

The project has been refactored to promote a clear separation of concerns, making it more maintainable and scalable.

```
.
├── .gitignore
├── pyproject.toml
├── README.md
└── src
    ├── core
    │   ├── agent.py      # Core logic for the conversational agent and chat history
    │   └── rag.py        # Core logic for the RAG chain
    ├── main.py           # Main entry point for the Chainlit application
    └── presentation
        ├── callbacks.py  # Handles user messages and actions (@cl.on_message)
        └── factory.py      # Creates UI components and handles setup (@cl.on_chat_start)
```

- **`src/`**: The main source code directory.
  - **`main.py`**: The entry point that Chainlit uses to run the application. It imports the necessary modules to register the Chainlit decorators.
  - **`core/`**: Contains the core business logic of the application.
    - `agent.py`: Manages the setup of the main conversational agent and chat history.
    - `rag.py`: Manages the setup of the RAG chain for interacting with documents.
  - **`presentation/`**: Contains the code related to the user interface and user interaction (the "view" layer).
    - `factory.py`: Responsible for creating and setting up the initial chat interface, settings, and chat profiles.
    - `callbacks.py`: Contains the callbacks that respond to user actions, such as sending a message or clicking a button.

## How to Run

1.  **Install Dependencies**:
    Make sure you have Python 3.9+ installed. It's recommended to use a virtual environment.

    ```bash
    pip install -e .
    ```

2.  **Run the application**:
    Use the Chainlit CLI to run the application.

    ```bash
    chainlit run src/main.py -w
    ```
    The `-w` flag enables auto-reloading, which is useful for development.

3.  **Open your browser**:
    Navigate to `http://localhost:8000` to start interacting with the chat application.