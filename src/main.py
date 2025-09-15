# src/main.py
"""
Main entry point for the Chainlit RAG application.
This module imports and registers all Chainlit decorators.
"""
import sys
from pathlib import Path

# Add the src directory to the Python path so we can import our modules
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import all the Chainlit decorated functions to register them
from presentation.factory import start, on_settings_update, chat_profile
from presentation.callbacks import handle_message, on_action

# Optional: You can add any application-level initialization here
def initialize_app():
    """Initialize application-level configurations if needed."""
    pass

# Call initialization if needed
initialize_app()