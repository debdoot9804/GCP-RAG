import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal will manage connections for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Dependency helper (used in FastAPI endpoints later)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#✅ What this does:

# Connects SQLAlchemy to your Cloud SQL instance

# Prepares a session maker for queries

# Loads .env variables automatically