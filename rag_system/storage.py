"""
Vector database storage for the G'Day Bot RAG system
"""
import os
import json
import chromadb
from typing import Dict, List, Any
from .embedding import generate_embedding

# Constants
CHROMA_DB_PATH = os.environ.get("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "australianisms")

def get_chroma_client():
    """
    Initialize and return a ChromaDB client with persistence
    
    Returns:
        ChromaDB client
    """
    # Create the directory if it doesn't exist
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    
    # Initialize ChromaDB with persistence
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client

def get_collection(client, collection_name=COLLECTION_NAME):
    """
    Get an existing collection from ChromaDB
    
    Args:
        client: ChromaDB client
        collection_name: Name of the collection
        
    Returns:
        ChromaDB collection
    """
    try:
        # Try to get the existing collection
        collection = client.get_collection(name=collection_name)
        return collection
    except Exception as e:
        # If collection doesn't exist, create and initialize it
        print(f"Collection {collection_name} not found. Creating and initializing...")
        collection = init_collection(client, collection_name)
        return collection

def init_collection(client, collection_name=COLLECTION_NAME):
    """
    Initialize a collection with australianisms data
    
    Args:
        client: ChromaDB client
        collection_name: Name of the collection
        
    Returns:
        Number of records added to the collection
    """
    # Create or get the collection
    try:
        # If collection exists, delete it first for clean initialization
        client.delete_collection(name=collection_name)
    except:
        pass  # Collection didn't exist, that's fine
        
    # Create a new collection
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Australian slang and phrases"}
    )
    
    # Get the data file path from environment or use default
    data_path = os.environ.get("AUSTRALIANISMS_PATH", "./data/australianisms.json")
    
    # Load the australianisms data
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            australianisms = json.load(f)
    except Exception as e:
        print(f"Error loading australianisms data: {str(e)}")
        # Create minimal dataset if file loading fails
        australianisms = [
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
    
    # Add the australianisms to the collection
    ids = []
    documents = []
    embeddings = []
    metadatas = []
    
    for i, item in enumerate(australianisms):
        # Create unique ID
        item_id = f"phrase_{i}"
        ids.append(item_id)
        
        # Format the document
        doc_text = json.dumps(item)
        documents.append(doc_text)
        
        # Generate embeddings
        # For embedding, use the phrase and meaning together
        text_to_embed = f"{item['phrase']} - {item['meaning']}"
        embedding = generate_embedding(text_to_embed)
        embeddings.append(embedding)
        
        # Add metadata
        metadata = {
            "phrase": item["phrase"],
            "length": len(item["phrase"]),
        }
        metadatas.append(metadata)
    
    # Add documents to collection
    if ids:
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
    
    return len(ids)