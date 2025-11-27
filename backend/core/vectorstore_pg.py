import os
from langchain_community.vectorstores.pgvector import PGVector

def store_embeddings(chunks, embedding_fn, metadatas):
    """Store text + embeddings in PostgreSQL pgvector."""
    vector_store = PGVector(
        connection_string=os.getenv("DATABASE_URL"),
        collection_name="rag_docs",
        embedding_function=embedding_fn
    )
    vector_store.add_texts(texts=chunks, metadatas=metadatas)
