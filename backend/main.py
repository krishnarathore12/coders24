import os
from dotenv import load_dotenv

# Load environment variables from .env file immediately
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routes
from app.api.endpoints import ingest

app = FastAPI(
    title="Agni RAG API",
    description="Backend for Agni RAG system using Agno, FastAPI, and Qdrant Cloud.",
    version="1.0.0"
)

# --- CORS Configuration ---
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routers ---
app.include_router(ingest.router, prefix="/api/documents", tags=["Documents"])


@app.get("/")
def health_check():
    return {"status": "active", "system": "Agni RAG Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)