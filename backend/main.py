# backend/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from core.db import get_db
from api.upload import router as upload_router

# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot Backend",
    description="Backend API for a production-grade RAG chatbot using Azure OpenAI + PostgreSQL + LangChain.",
    version="1.0.0"
)

# ------------------------------------------------------
# 1️⃣ Allow CORS (important if you build a frontend later)
# ------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # You can restrict later, e.g. ["https://yourfrontend.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------
# 2️⃣ Health check / test endpoint
# ------------------------------------------------------
@app.get("/")
async def root():
    return {"message": "RAG Backend is running ✅"}

# ------------------------------------------------------
# 3️⃣ Database connectivity test
# ------------------------------------------------------
@app.get("/test-db")
async def test_db(db=Depends(get_db)):
    result = db.execute(text("SELECT version();"))
    version = list(result)[0][0]
    return {"message": "Connected to PostgreSQL!", "version": version}

# ------------------------------------------------------
# 4️⃣ Include your file upload / embedding routes
# ------------------------------------------------------
app.include_router(upload_router, prefix="/upload", tags=["Upload"])

# ------------------------------------------------------
# 5️⃣ Ready for Phase 5 (Chatbot routes)
# ------------------------------------------------------
# We will add a /chat route later to handle conversations using Azure GPT-4o
