# src/presentation/factory.py
import chainlit as cl
from chainlit.input_widget import Select, Slider, TextInput

from core.agent import setup_agent
from core.rag import setup_rag_chain


@cl.on_chat_start
async def start():
    """
    Initializes the chat by greeting the user, configuring settings and
    optionally setting up a RAG chain for a PDF.
    """
    try:
        # Ask for user's name
        ask_name = cl.AskUserMessage(
            content="👋 Welcome! What's your name?", 
            timeout=30
        )
        result = await ask_name.send()
        name = result["output"] if result else "Friend"
        cl.user_session.set("name", name)

        await cl.Message(
            content=f"Hello, {name}! 🎉\n\nPlease configure the settings below to get started."
        ).send()

        # Configure settings
        settings = await cl.ChatSettings([
            Select(
                id="model",
                label="🤖 Model",
                values=["gpt-oss:20b", "phi4", "llama2", "mistral"],
                initial_index=0,
            ),
            TextInput(
                id="domain",
                label="🎯 Domain of Expertise",
                initial="General Knowledge",
                placeholder="e.g., IT, Medicine, Finance, etc.",
                multiline=False,
            ),
            Slider(
                id="temperature",
                label="🌡️ Temperature (Creativity)",
                initial=0.3,
                min=0,
                max=1,
                step=0.1,
            ),
        ]).send()

        # Setup the agent
        success = setup_agent(settings)
        if not success:
            await cl.Message(
                content="⚠️ Warning: There was an issue setting up the agent. Please try again."
            ).send()
            return

        await cl.Message(
            content="✅ Settings configured! You can now:\n- Chat normally for general questions\n- Upload a PDF to ask questions about specific documents"
        ).send()

        # Optional PDF upload
        files = await cl.AskFileMessage(
            content="📄 **Optional**: Upload a PDF file to enable document-specific Q&A",
            accept=["application/pdf"],
            max_size_mb=20,
            timeout=180,
        ).send()
        
        if files:
            await setup_rag_chain(files[0])

    except Exception as e:
        await cl.Message(
            content=f"❌ Error during initialization: {str(e)}"
        ).send()
        print(f"Error in start: {e}")


@cl.on_settings_update
async def on_settings_update(settings):
    """Handles updating the agent when settings are changed."""
    try:
        success = setup_agent(settings)
        if success:
            await cl.Message(
                content="✅ Settings updated successfully!"
            ).send()
        else:
            await cl.Message(
                content="⚠️ There was an issue updating the settings. Please try again."
            ).send()
    except Exception as e:
        await cl.Message(
            content=f"❌ Error updating settings: {str(e)}"
        ).send()
        print(f"Error in on_settings_update: {e}")


@cl.set_chat_profiles
async def chat_profile():
    """Defines the chat profiles for the application."""
    return [
        cl.ChatProfile(
            name="RAG Assistant",
            icon="🤖",
            markdown_description="**AI Assistant with RAG capabilities**\n\nI can help you with general questions and analyze PDF documents you upload.",
            starters=[
                cl.Starter(
                    label="What is RAG?",
                    message="What is Retrieval-Augmented Generation (RAG) and how does it work?",
                    icon="🔍",
                ),
                cl.Starter(
                    label="How do I upload a document?",
                    message="How can I upload a PDF document to ask questions about it?",
                    icon="📄",
                ),
                cl.Starter(
                    label="General Chat",
                    message="Hello! I'd like to have a general conversation.",
                    icon="💬",
                ),
            ],
        )
    ]