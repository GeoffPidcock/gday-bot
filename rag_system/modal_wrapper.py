"""
Modal deployment wrapper for the G'Day Bot RAG system
"""
import os
import modal
import sys
from fastapi import FastAPI

# Add the parent directory to sys.path to allow imports from the rag_system package
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Get the project root directory
BASE_DIR = parent_dir
DATA_PATH = os.path.join(BASE_DIR, "data/australianisms.json")

# Create data directory if it doesn't exist
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# Create a Modal image with required dependencies
image = modal.Image.debian_slim().pip_install(
    "fastapi",
    "uvicorn",
    "openai",
    "python-dotenv",
    "chromadb",
    "tiktoken",
)

# Add the data file to the image
image = image.add_local_file(DATA_PATH, "/root/data/australianisms.json")

# Define the Modal app
app = modal.App("gday-rag-api")

@app.function(
    image=image,
    concurrency_limit=5,  # Limit concurrent instances
    secrets=[
        modal.Secret.from_name("openai-secret"),  # Secret for OpenAI API key
    ]
)
@modal.asgi_app()  # Register as an ASGI app (FastAPI)
def serve():
    """
    Main server function for the RAG API
    """
    # Set environment variables for the app
    os.environ["AUSTRALIANISMS_PATH"] = "/root/data/australianisms.json"
    os.environ["CHROMA_DB_PATH"] = "/root/chroma_db"
    
    # Import the FastAPI app directly
    # Dynamically import here to avoid circular imports
    from rag_system.main import app as fastapi_app
    
    return fastapi_app

@app.local_entrypoint()
def main():
    """
    Local development entry point
    """
    # Easier to run the app directly for local development
    import uvicorn
    
    # Set environment variables for local development
    os.environ["AUSTRALIANISMS_PATH"] = os.path.join(BASE_DIR, "data/australianisms.json")
    os.environ["CHROMA_DB_PATH"] = os.path.join(BASE_DIR, "chroma_db")
    
    print(f"Using data file: {os.environ['AUSTRALIANISMS_PATH']}")
    print("Starting RAG API server for local development...")
    
    # Import the app here to ensure environment variables are set first
    from rag_system.main import app as fastapi_app
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)