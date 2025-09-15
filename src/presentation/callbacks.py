# src/presentation/callbacks.py
import chainlit as cl
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.vectorstores import VectorStore

from core.rag import get_rag_chain


@cl.on_message
async def handle_message(message: cl.Message):
    """Handles incoming messages, with RAG or without (general chat)."""
    try:
        vectorstore: VectorStore = cl.user_session.get("vectorstore")
        user_session_id = cl.user_session.get("id")

        if vectorstore:
            # Use RAG chain for document-based questions
            rag_chain = get_rag_chain()
            if not rag_chain:
                await cl.Message(
                    content="❌ Error: RAG chain not properly initialized."
                ).send()
                return

            msg = cl.Message(content="")
            
            async for chunk in rag_chain.astream(message.content):
                await msg.stream_token(chunk)
            await msg.send()
            
        else:
            # Use general conversational agent
            final_chain = cl.user_session.get("final_chain")
            if not final_chain:
                await cl.Message(
                    content="❌ Please configure the settings first or upload a PDF document."
                ).send()
                return

            domain = cl.user_session.get("domain", "IT")
            
            thanks_action = cl.Action(
                label="❤️",
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
            
    except Exception as e:
        await cl.Message(
            content=f"❌ Error processing your message: {str(e)}"
        ).send()
        print(f"Error in handle_message: {e}")


@cl.action_callback("thanks")
async def on_action(action: cl.Action):
    """Callback for the 'thanks' action."""
    try:
        print(f"Thanks action - message_id: {action.forId}, payload: {action.payload}")
        await action.remove()
        await cl.Message(content="You're welcome! 😊").send()
    except Exception as e:
        print(f"Error in thanks action: {e}")