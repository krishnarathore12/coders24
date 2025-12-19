import shutil
import os
import traceback
import hashlib
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from qdrant_client.models import PointStruct, VectorParams, Distance

# --- UPDATED IMPORTS (Relative) ---
from .pdf_parser import PDFParser
from .knowledge import knowledge_base

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class IngestResponse(BaseModel):
    status: str
    filename: str
    chunks_processed: int
    message: str

@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Uploads a PDF, parses it (Text+Tables), generates embeddings, and stores in Qdrant.
    """
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    
    try:
        # 1. Save File
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Parse Document
        print(f" Parsing {file.filename}...")
        parser = PDFParser()
        documents = parser.parse(file_location)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No content extracted.")

        print(f" Extracted {len(documents)} chunks. Generating embeddings...")

        # 3. Prepare Points for Qdrant (Manual Embedding & Construction)
        points = []
        
        client = knowledge_base.vector_db.client
        embedder = knowledge_base.vector_db.embedder
        collection_name = knowledge_base.vector_db.collection

        for doc in documents:
            # A. Generate Deterministic UUID
            content_hash = hashlib.md5(doc.content.encode("utf-8")).hexdigest()
            doc_uuid = str(uuid.UUID(hex=content_hash))
            
            # B. Generate Embedding
            vector = embedder.get_embedding(doc.content)
            
            # C. Create Qdrant Point
            payload = {
        "meta_data": doc.meta_data,  # Keep the key as 'meta_data' to match the error message
        "content": doc.content,
        "name": file.filename
        }
            
            points.append(PointStruct(id=doc_uuid, vector=vector, payload=payload))

        # 4. Ensure Collection Exists
        try:
            client.get_collection(collection_name)
        except Exception:
            print(f" Creating collection '{collection_name}'...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=len(points[0].vector), distance=Distance.COSINE)
            )

        # 5. Upsert to Qdrant
        print(f" Upserting {len(points)} vectors to Qdrant...")
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        print(" Indexing complete!")
        
    except Exception as e:
        print(" Error during ingestion:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_processed": len(documents),
        "message": "Document successfully ingested and indexed."
    }
