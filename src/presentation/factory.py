import chainlit as cl
from chainlit.input_widget import Select, Slider, TextInput

from src.core.agent import setup_agent
from src.core.rag import setup_rag_chain


@cl.on_chat_start
async def start():
    """
    Initializes the chat by greeting the user, configuring settings and
    optionally setting up a RAG chain for a PDF.
    """
    ask_name = cl.AskUserMessage(content="What is your name?", timeout=30)
    result = await ask_name.send()
    name = result["output"] if result else "stranger"
    cl.user_session.set("name", name)

    await cl.Message(
        content=f"Hello, {name}! Please configure the settings for our chat"
    ).send()

    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="Model",
                values=["gpt-oss:20b", "phi4"],
                initial_index=0,
            ),
            TextInput(
                id="domain",
                label="Domain",
                initial="IT",
                placeholder="Type the domain area",
                multiline=False,
            ),
            Slider(
                id="temperature",
                label="Temperature",
                initial=0,
                min=0,
                max=1,
                step=0.1,
            ),
        ]
    ).send()
    setup_agent(settings)
    await cl.Message(content="Settings updated! You can now chat").send()

    files = await cl.AskFileMessage(
        content="Optional: Please upload a PDF file to talk to, if you want.",
        accept=["application/pdf"],
        max_size_mb=20,
        timeout=180,
    ).send()
    if files:
        await setup_rag_chain(files[0])


@cl.on_settings_update
async def on_settings_update(settings):
    """Handles updating the agent when settings are changed."""
    setup_agent(settings)
    await cl.Message(content="Settings updated! You can now chat").send()


@cl.set_chat_profiles
async def chat_profile():
    """Defines the chat profiles for the application."""
    return [
        cl.ChatProfile(
            name="Parrot is crazy",
            icon="/public/robot_parrot.svg",
            markdown_description="We use chainlit with langchain crazy parrot",
            starters=[
                cl.Starter(
                    label="What is LangChain?",
                    message="What is langchain?",
                    icon="/public/chain.svg",
                ),
                cl.Starter(
                    label="Why parrot is the mascot of the LangChain?",
                    message="Why parrot is the mascot of the LangChain?",
                    icon="/public/blue_parrot.svg",
                ),
            ],
        )
    ]