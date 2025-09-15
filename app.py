import chainlit as cl
from chainlit.input_widget import Select, Slider, TextInput
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import (
    RunnableWithMessageHistory,
    BaseChatMessageHistory,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel
from langchain_core.vectorstores import VectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


store = {}


def get_history_by_session_id(session_id: str) -> BaseChatMessageHistory:
    """Gets or creates an in-memory chat history for a given session ID."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


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
    await setup_agent(settings)

    files = await cl.AskFileMessage(
        content="Optional: Please upload a PDF file to talk to, if you want.",
        accept=["application/pdf"],
        max_size_mb=20,
        timeout=180,
    ).send()
    if files:
        await setup_rag_chain(files[0])


async def setup_rag_chain(file: cl.File):
    """Sets up the RAG chain for conversing with the uploaded PDF."""
    msg = cl.Message(content=f"Processing file: {file.name}...")
    await msg.send()

    loader = PyPDFLoader(file.path)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100)
    documents = loader.load_and_split(text_splitter)

    embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-base")
    vectorstore = FAISS.from_documents(documents, embeddings)
    cl.user_session.set("vectorstore", vectorstore)

    await cl.Message(
        content=f"You can now ask questions about{file.name}.").send()


@cl.on_settings_update
async def setup_agent(settings):
    """Sets up the general conversational agent based on user settings."""
    cl.user_session.set("model", settings["model"])
    cl.user_session.set("domain", settings["domain"])
    cl.user_session.set("temperature", settings["temperature"])

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
            You are an expert in {domain}.
            Your task is to answer the question as short as possible
            """,
            ),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )

    llm = ChatOllama(
        model=settings["model"],
        temperature=float(settings["temperature"]),
    )

    final_chain = RunnableWithMessageHistory(
        prompt | llm | StrOutputParser(),
        get_history_by_session_id,
        input_messages_key="question",
        history_messages_key="history",
    )

    cl.user_session.set("final_chain", final_chain)
    await cl.Message(content="Settings updated! You can now chat").send()


@cl.on_message
async def handle_message(message: cl.Message):
    """Handles incoming messages, with RAG or without(general chat)."""
    vectorstore: VectorStore = cl.user_session.get("vectorstore")
    user_session_id = cl.user_session.get("id")

    if vectorstore:
        retriever = vectorstore.as_retriever()
        model = cl.user_session.get("model", "gpt-oss:20b")
        temperature = cl.user_session.get("temperature", 0.1)

        rag_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
             You are a helpful assistant. Use the following context to answer
             the question. \nContext: {context}
             """,
                ),
                ("human", "{question}"),
            ]
        )
        llm = ChatOllama(
            model=model,
            temperature=float(temperature),
        )
        rag_chain = RunnableParallel(
            {
                "context": (lambda x: x["question"]) | retriever,
                "question": (lambda x: x["question"]),
            }
        ).assign(answer=rag_prompt | llm | StrOutputParser())

        msg = cl.Message(content="")
        async for chunk in rag_chain.astream(
            {"question": message.content},
            config=RunnableConfig(
                configurable={"session_id": user_session_id}),
        ):
            if "answer" in chunk:
                await msg.stream_token(chunk["answer"])
        await msg.send()

    else:
        final_chain = cl.user_session.get("final_chain")
        if not final_chain:
            await cl.Message(
                content="Please configure the settings for our chat"
            ).send()
            return

        domain = cl.user_session.get("domain")

        thanks_action = cl.Action(
            label="❤",
            name="thanks",
            payload={"user_session_id": user_session_id},
            tooltip="Send thanks for the helpful reply",
        )

        msg = cl.Message(content="", actions=[thanks_action])
        async for chunk in final_chain.astream(
            {"domain": domain, "question": message.content},
            config=RunnableConfig(
                configurable={"session_id": user_session_id}),
        ):
            await msg.stream_token(chunk)
        await msg.send()


@cl.set_chat_profiles
async def chat_profile():
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


@cl.action_callback("thanks")
async def on_action(action: cl.Action):
    print("message_id", action.forId, "action_payload:", action.payload)
    await action.remove()
    await cl.Message(content="Thank you too!").send()
