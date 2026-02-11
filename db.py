import os
from langchain_community.vectorstores import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Initialize Qdrant Client
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

if qdrant_url:
    # Use Cloud/Server instance
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
else:
    # Use local file storage for persistence (Embedded mode)
    # Use local file storage for persistence (Embedded mode)
    # This requires no Docker or setup!
    QDRANT_PATH = "./qdrant_db"
    try:
        client = QdrantClient(path=QDRANT_PATH)
    except Exception as e:
        # If the database is locked, it means another instance is running
        print(f"CRITICAL ERROR: Could not open Qdrant database at {QDRANT_PATH}.")
        print(f"Details: {e}")
        print("SOLUTION: Please STOP any other running instances of this app (Ctrl+C in terminal) and try again.")
        raise e

def get_embeddings_model():
    """
    Returns the embedding model.
    Using all-MiniLM-L6-v2 for efficiency and zero cost.
    """
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_store(collection_name: str):
    """
    Returns the Qdrant vector store for a specific collection.
    """
    embeddings = get_embeddings_model()
    
    # Ensure collection exists
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    return vector_store

def list_collections():
    """Returns a list of all available collections (repos)."""
    try:
        collections_response = client.get_collections()
        return [c.name for c in collections_response.collections]
    except Exception as e:
        print(f"Error listing collections: {e}")
        return []
