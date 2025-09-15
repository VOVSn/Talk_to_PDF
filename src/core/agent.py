import chainlit as cl
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import (
    RunnableWithMessageHistory,
    BaseChatMessageHistory,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama


store = {}


def get_history_by_session_id(session_id: str) -> BaseChatMessageHistory:
    """Gets or creates an in-memory chat history for a given session ID."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


def setup_agent(settings):
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