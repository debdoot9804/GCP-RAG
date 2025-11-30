import os
from langchain_community.vectorstores.pgvector import PGVector

from sqlalchemy import create_engine, text
import os

def delete_session_embeddings(session_id: str):
    """Deletes all embeddings for a given session_id."""
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM langchain_pg_embedding WHERE cmetadata->>'session_id' = :sid"),
            {"sid": session_id}
        )
        conn.commit()



def store_embeddings(chunks, embedding_fn, metadatas):
    """Store text + embeddings in PostgreSQL pgvector."""
    vector_store = PGVector(
        connection_string=os.getenv("DATABASE_URL"),
        collection_name="rag_docs",
        embedding_function=embedding_fn
    )
    vector_store.add_texts(texts=chunks, metadatas=metadatas)
