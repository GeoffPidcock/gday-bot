"""
Embedding generation for the G'Day Bot RAG system
"""
import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables for API access
load_dotenv()

# Constants
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")

def get_openai_client():
    """
    Initialize and return an OpenAI client
    
    Returns:
        OpenAI client instance
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    return OpenAI(api_key=api_key)

def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding vector for text using OpenAI's API
    
    Args:
        text: The text to generate an embedding for
        
    Returns:
        List of floats representing the embedding vector
    """
    client = get_openai_client()
    
    try:
        # Request the embedding from OpenAI
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        
        # Extract the embedding vector from the response
        embedding = response.data[0].embedding
        
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        # Return a dummy embedding in case of error (all zeros)
        # In production, you'd want better error handling
        return [0.0] * 1536  # Default embedding size for OpenAI models