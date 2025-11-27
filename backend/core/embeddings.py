from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from .vectorstore_pg import store_embeddings
from ..utils.parser import parse_file
import os

def process_and_store_documents(files, session_id: str):
    """Process uploaded files, extract text, split, embed, and store in Postgres."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    results = []

    for f in files:
        file_bytes = f.file.read()
        text = parse_file(f.filename, file_bytes)
        chunks = splitter.split_text(text)

        embeddings = AzureOpenAIEmbeddings(
            model="text-embedding-3-large",
            deployment=os.getenv("OPENAI_EMBED_DEPLOYMENT_NAME"),
            openai_api_base=os.getenv("OPENAI_ENDPOINT"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_type="azure"
        )

        store_embeddings(chunks, embeddings, [{"session_id": session_id, "filename": f.filename}] * len(chunks))
        results.append({"filename": f.filename, "chunks": len(chunks)})

    return results
