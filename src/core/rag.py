# src/core/rag.py
import chainlit as cl
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


async def setup_rag_chain(file: cl.File):
    """Sets up the RAG chain for conversing with the uploaded PDF."""
    try:
        msg = cl.Message(content=f"Processing file: {file.name}...")
        await msg.send()

        # Load and split the PDF
        loader = PyPDFLoader(file.path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100
        )
        splits = text_splitter.split_documents(documents)

        # Create embeddings and vectorstore
        embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-base"
        )
        vectorstore = FAISS.from_documents(splits, embeddings)
        cl.user_session.set("vectorstore", vectorstore)

        await cl.Message(
            content=f"✅ Successfully processed {file.name}. You can now ask questions about the document!"
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ Error processing file: {str(e)}"
        ).send()
        print(f"Error in setup_rag_chain: {e}")


def get_rag_chain():
    """Constructs the RAG chain for streaming answers."""
    try:
        vectorstore = cl.user_session.get("vectorstore")
        if not vectorstore:
            return None
            
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        model = cl.user_session.get("model", "gpt-oss:20b")
        temperature = cl.user_session.get("temperature", 0.1)

        rag_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a helpful assistant. Use the following context to answer the question. "
                "If the answer is not in the context, say so clearly.\n\nContext: {context}"
            ),
            ("human", "{question}"),
        ])
        
        llm = ChatOllama(
            model=model,
            temperature=float(temperature),
        )
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        rag_chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough(),
            }
            | rag_prompt
            | llm
            | StrOutputParser()
        )
        
        return rag_chain
        
    except Exception as e:
        print(f"Error creating RAG chain: {e}")
        return None