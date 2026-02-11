import os
import shutil
import tempfile
from git import Repo
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from db import get_vector_store

# Supported extensions for code application
SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".c", ".h", ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".scala", ".html", ".css", ".md", ".json", ".yaml", ".yml", ".toml", ".sql", ".sh", ".bat", ".ps1", ".dockerfile", ".Dockerfile"
}

def is_valid_file(file_path):
    """Check if the file has a supported extension and is not hidden."""
    if any(part.startswith(".") for part in file_path.split(os.sep)):
        return False
    ext = os.path.splitext(file_path)[1]
    return ext in SUPPORTED_EXTENSIONS

def ingest_repo(repo_url: str):
    """
    Clones a GitHub repo and ingests it into Qdrant.
    """
    repo_name = repo_url.rstrip("/").split("/")[-1]
    collection_name = repo_name.replace("-", "_").replace(".", "_").lower()
    
    # If updating, we might want to clear old data first
    # For MVP, we will recreate the collection to avoid duplicates
    try:
        from db import client
        client.delete_collection(collection_name)
    except:
        pass # Collection might not exist

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Cloning {repo_url} into {temp_dir}...")
        try:
            Repo.clone_from(repo_url, temp_dir, depth=1)
        except Exception as e:
            return {"status": "error", "message": f"Failed to clone repo: {str(e)}"}

        documents = []
        print("Loading documents...")
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if is_valid_file(file_path):
                    try:
                        loader = TextLoader(file_path, encoding="utf-8", autodetect_encoding=True)
                        docs = loader.load()
                        # Add metadata
                        for doc in docs:
                            doc.metadata["source"] = file_path
                            doc.metadata["repo"] = repo_name
                            # Make path relative to repo root
                            relative_path = os.path.relpath(file_path, temp_dir)
                            doc.metadata["file_path"] = relative_path
                        documents.extend(docs)
                    except Exception as e:
                        print(f"Skipping {file_path}: {e}")
        
        if not documents:
            return {"status": "error", "message": "No valid documents found in repository."}
            
        print(f"Loaded {len(documents)} documents. Splitting...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )
        splits = text_splitter.split_documents(documents)
        print(f"Created {len(splits)} chunks.")
        
        print("Vectorizing and storing...")
        vector_store = get_vector_store(collection_name)
        vector_store.add_documents(documents=splits)
        
        return {
            "status": "success",
            "message": f"Successfully ingested {repo_name} with {len(splits)} chunks.",
            "collection_name": collection_name
        }
