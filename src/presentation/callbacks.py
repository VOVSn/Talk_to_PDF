import chainlit as cl
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.vectorstores import VectorStore

from src.core.rag import get_rag_chain


@cl.on_message
async def handle_message(message: cl.Message):
    """Handles incoming messages, with RAG or without(general chat)."""
    vectorstore: VectorStore = cl.user_session.get("vectorstore")
    user_session_id = cl.user_session.get("id")

    if vectorstore:
        rag_chain = get_rag_chain()
        msg = cl.Message(content="")
        async for chunk in rag_chain.astream(
            {"question": message.content},
            config=RunnableConfig(configurable={"session_id": user_session_id}),
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
            config=RunnableConfig(configurable={"session_id": user_session_id}),
        ):
            await msg.stream_token(chunk)
        await msg.send()


@cl.action_callback("thanks")
async def on_action(action: cl.Action):
    """Callback for the 'thanks' action."""
    print("message_id", action.forId, "action_payload:", action.payload)
    await action.remove()
    await cl.Message(content="Thank you too!").send()