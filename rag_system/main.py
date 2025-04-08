"""
FastAPI app for the G'Day Bot RAG system
"""
import os
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Import these directly to avoid circular imports
try:
    from .retrieval import search_australianisms
    from .storage import get_chroma_client, init_collection
except ImportError:
    # For direct execution
    from retrieval import search_australianisms
    from storage import get_chroma_client, init_collection

# Define the FastAPI app
# Important: This needs to be named 'app' to match the import in modal_wrapper.py
app = FastAPI(
    title="G'Day Bot RAG API",
    description="API for retrieving Australian slang and phrases",
    version="0.1.0"
)

# Define request/response models
class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 3
    threshold: Optional[float] = 0.7

class AustralianismMatch(BaseModel):
    phrase: str
    meaning: str
    usage_example: str
    score: float

class QueryResponse(BaseModel):
    matches: List[AustralianismMatch]
    query: str
    
# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if the API is running"""
    return {"status": "healthy"}

# Query endpoint
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the australianisms database for matches"""
    try:
        matches = search_australianisms(
            query=request.query,
            max_results=request.max_results,
            threshold=request.threshold
        )
        
        return {
            "matches": matches,
            "query": request.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# Initialize database endpoint
@app.post("/init", status_code=201)
async def initialize_database():
    """Initialize or refresh the vector database"""
    try:
        # Get chroma client and initialize collection
        client = get_chroma_client()
        count = init_collection(client)
        return {
            "status": "success", 
            "message": f"Initialized database with {count} entries"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Direct execution for development/testing
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)