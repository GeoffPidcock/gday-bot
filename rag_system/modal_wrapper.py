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
RAG_SYSTEM_DIR = os.path.join(BASE_DIR, "rag_system")

# Create a Modal image with required dependencies
image = modal.Image.debian_slim().pip_install(
    "fastapi",
    "uvicorn",
    "openai",
    "python-dotenv",
    "chromadb",
    "tiktoken",
)

# Add only the specific files we need
# 1. Add data file
image = image.add_local_file(DATA_PATH, "/app/data/australianisms.json")

# 2. Add rag_system Python files individually
for py_file in ["__init__.py", "main.py", "embedding.py", "retrieval.py", "storage.py"]:
    file_path = os.path.join(RAG_SYSTEM_DIR, py_file)
    if os.path.exists(file_path):
        image = image.add_local_file(file_path, f"/app/rag_system/{py_file}")

# Define the Modal app
app = modal.App("gday-rag-api")

@app.function(
    image=image,
    concurrency_limit=5,  # Limit concurrent instances
    secrets=[
        modal.Secret.from_name("openai-secret-3"),  # Secret for OpenAI API key
    ]
)
@modal.asgi_app()  # Register as an ASGI app (FastAPI)
def serve():
    """
    Main server function for the RAG API
    """
    # Create necessary directories
    os.makedirs("/app/data", exist_ok=True)
    os.makedirs("/app/chroma_db", exist_ok=True)
    
    import sys
    sys.path.append("/app")  # Add /app to Python path
    
    # Set environment variables for the app
    os.environ["AUSTRALIANISMS_PATH"] = "/app/data/australianisms.json"
    os.environ["CHROMA_DB_PATH"] = "/app/chroma_db"
    
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