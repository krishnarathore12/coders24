import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import your agents from their respective modules
# Ensure these files (agents/query_router.py, etc.) exist in your directory structure
from agents.query_router import router_agent
from agents.query_enhancer import query_enhancer
from agents.query_responser import query_responser

from app import ingest

# Load environment variables
load_dotenv()

# Initialize FastAPI app
api = FastAPI(
    title="Agni RAG Pipeline",
    description="API for Query Routing, Enhancement, and RAG Response",
    version="0.1.0"
)

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str
    enhanced_query: str | None = None

# --- Endpoints ---

@api.get("/health")
def health_check():
    """Health check endpoint to ensure the server is running."""
    return {"status": "active", "backend": "fastapi"}


api.include_router(ingest.router, prefix="/api/documents", tags=["Documents"])


@api.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that processes the user query through the agent pipeline:
    1. Checks relevance via Router Agent.
    2. If relevant, enhances query via Enhancer Agent.
    3. Generates answer via Responser Agent.
    """
    user_input = request.message
    
    try:
        # Step 1: Route the query
        # We assume agent.run() returns an object with a .content attribute
        router_response = router_agent.run(user_input)
        route_decision = router_response.content.strip().lower()
        
        # Step 2: Conditional Logic
        if "yes" in route_decision:
            # Enhance the query
            enhanced_query_obj = query_enhancer.run(user_input)
            enhanced_query_text = enhanced_query_obj.content
            
            # Generate final response
            final_response_obj = query_responser.run(enhanced_query_text)
            
            return ChatResponse(
                response=final_response_obj.content,
                status="success",
                enhanced_query=enhanced_query_text
            )
        else:
            # Query deemed irrelevant
            return ChatResponse(
                response="Query is not related to the documents.",
                status="filtered",
                enhanced_query=None
            )

    except Exception as e:
        # Log the error in a real app
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)