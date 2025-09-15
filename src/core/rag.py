import chainlit as cl
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


async def setup_rag_chain(file: cl.File):
    """Sets up the RAG chain for conversing with the uploaded PDF."""
    msg = cl.Message(content=f"Processing file: {file.name}...")
    await msg.send()

    loader = PyPDFLoader(file.path)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100
    )
    documents = loader.load_and_split(text_splitter)

    embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-base"
    )
    vectorstore = FAISS.from_documents(documents, embeddings)
    cl.user_session.set("vectorstore", vectorstore)

    await cl.Message(
        content=f"You can now ask questions about {file.name}."
    ).send()


def get_rag_chain():
    """Constructs the RAG chain for streaming answers."""
    vectorstore = cl.user_session.get("vectorstore")
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
    return rag_chain
