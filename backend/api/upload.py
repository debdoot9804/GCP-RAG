# backend/api/upload.py
from fastapi import APIRouter, UploadFile, File
from typing import List
from ..core.embeddings import process_and_store_documents

router = APIRouter()

@router.post("/")   # 👈 remove '/upload' here
async def upload_files(session_id: str, files: List[UploadFile] = File(...)):
    if len(files) > 3:
        return {"error": "Maximum 3 files allowed"}
    
    results = process_and_store_documents(files, session_id)
    return {"message": "Files processed successfully", "details": results}
