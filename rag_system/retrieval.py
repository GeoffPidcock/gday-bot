"""
Retrieval logic for the G'Day Bot RAG system
"""
import os
import json
from typing import Dict, List, Any
from .embedding import generate_embedding
from .storage import get_chroma_client, get_collection

def load_australianisms(file_path: str = None) -> List[Dict[str, Any]]:
    """
    Load australianisms data from JSON file
    
    Args:
        file_path: Path to the australianisms JSON file
        
    Returns:
        List of dictionaries containing australianisms data
    """
    # Default path if none provided
    if file_path is None:
        file_path = os.environ.get("AUSTRALIANISMS_PATH", "./data/australianisms.json")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading australianisms: {str(e)}")
        # Return a minimal dataset if file can't be loaded
        return [
            {
                "phrase": "G'day",
                "meaning": "Hello, good day",
                "usage_example": "G'day mate, how's it going?"
            },
            {
                "phrase": "Fair dinkum",
                "meaning": "True, genuine, authentic",
                "usage_example": "Is that fair dinkum or are you pulling my leg?"
            }
        ]

def search_australianisms(
    query: str, 
    max_results: int = 3, 
    threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Search for australianisms that match the query using vector similarity
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        threshold: Minimum similarity score threshold
        
    Returns:
        List of matching australianisms with similarity scores
    """
    # Generate embedding for the query
    query_embedding = generate_embedding(query)
    
    # Get chroma client and collection
    client = get_chroma_client()
    collection = get_collection(client)
    
    # Query the collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=max_results
    )
    
    matches = []
    
    # Process results if available
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            # Skip results below threshold
            distance = results["distances"][0][i] if "distances" in results else 0.5
            # Convert distance to similarity (higher is better)
            # For scores that can exceed 1.0, subtract from 2.0
            similarity = 2.0 - distance
            
            # Skip results below threshold
            if similarity < threshold:
                continue
            
            # Parse document content and add to matches with the similarity score
            try:
                data = json.loads(doc)
                matches.append({
                    "phrase": data["phrase"],
                    "meaning": data["meaning"],
                    "usage_example": data["usage_example"],
                    "score": similarity  # Use similarity instead of distance
                })
            except json.JSONDecodeError:
                # If not valid JSON, use the document text directly
                matches.append({
                    "phrase": doc.split("\n")[0] if "\n" in doc else doc,
                    "meaning": "Unknown",
                    "usage_example": "Unknown",
                    "score": distance
                })
    
    return matches

def get_random_australianism() -> Dict[str, Any]:
    """
    Get a random australianism for fun responses
    
    Returns:
        Dictionary containing a random australianism
    """
    import random
    
    # Load all australianisms
    australianisms = load_australianisms()
    
    # Return a random one
    return random.choice(australianisms)