import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from .vectorstore_pg import store_embeddings
from ..utils.parser import parse_file


load_dotenv()

os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("OPENAI_ENDPOINT")
os.environ["AZURE_OPENAI_API_VERSION"] = os.getenv("API_VERSION")

def process_and_store_documents(files, session_id: str):
    """Process uploaded files, extract text, split, embed, and store in Postgres."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    results = []

    for f in files:
        # Read file content
        file_bytes = f.file.read()
        text = parse_file(f.filename, file_bytes)
        chunks = splitter.split_text(text)

        
        embeddings = AzureOpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBED_DEPLOYMENT_NAME"),
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version=os.environ["AZURE_OPENAI_API_VERSION"]
        )

        # Store embeddings in PGVector
        store_embeddings(
            chunks,
            embeddings,
            [{"session_id": session_id, "filename": f.filename}] * len(chunks)
        )

        results.append({
            "filename": f.filename,
            "chunks": len(chunks)
        })

    return results
