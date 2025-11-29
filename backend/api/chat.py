import os
from unittest import result
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_core.prompts import PromptTemplate
from ..core.db import get_db
from ..core.models import Message, Session as ChatSession
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# --------------------------
# 🔹 Define your chat route
# --------------------------
@router.post("/")
async def chat(session_id: str, user_input: str, db: Session = Depends(get_db)):
    # 1️⃣ Retrieve or create session
    chat_session = db.query(ChatSession).filter_by(id=session_id).first()
    if not chat_session:
        chat_session = ChatSession(id=session_id)
        db.add(chat_session)
        db.commit()

    # 2️⃣ Save user message
    user_msg = Message(session_id=session_id, role="user", content=user_input)
    db.add(user_msg)
    db.commit()

    # 3️⃣ Initialize embedding + vector store
    # embedding_fn = AzureOpenAIEmbeddings(
    #     model="text-embedding-3-large",
    #     deployment=os.getenv("OPENAI_EMBED_DEPLOYMENT_NAME"),
    #     openai_api_base=os.getenv("OPENAI_ENDPOINT"),
    #     openai_api_key=os.getenv("OPENAI_API_KEY"),
    #     openai_api_type="azure"
    # )

    embedding_fn = AzureOpenAIEmbeddings(
    model="text-embedding-3-large",
    azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2024-12-01-preview"
)

    vectorstore = PGVector(
        connection_string=os.getenv("DATABASE_URL"),
        collection_name="rag_docs",
        embedding_function=embedding_fn,
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # 4️⃣ Build the prompt for GPT-4o
    template = """
    You are a helpful AI assistant.
    Use the following context from uploaded documents to answer the user's question.

    Context:
    {context}

    Chat history:
    {chat_history}

    Question:
    {question}
    """

    PROMPT = PromptTemplate(
        template=template,
        input_variables=["context", "chat_history", "question"]
    )

    # 5️⃣ Initialize LLM
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
        openai_api_version="2024-12-01-preview",
        deployment_name="gpt-4o-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_type="azure"
    )

    # 6️⃣ Create the conversational chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )

    # 7️⃣ Load previous messages for context
    chat_history = db.query(Message).filter_by(session_id=session_id).all()
    formatted_history = [(m.role, m.content) for m in chat_history if m.role in ["user", "assistant"]]

    # 8️⃣ Run the RAG chain
    result = qa_chain.invoke({"question": user_input, "chat_history": formatted_history})

    # 9️⃣ Save assistant response
    assistant_msg = Message(session_id=session_id, role="assistant", content=result["answer"])
    db.add(assistant_msg)
    db.commit()



    
    sources = [doc.metadata for doc in result["source_documents"]]

    # Add this for uniqueness
    unique_sources = [dict(t) for t in {tuple(sorted(d.items())) for d in sources}]

    return {
        "answer": result["answer"],
        "sources": unique_sources
    }


   
