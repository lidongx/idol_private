"""
ChromaDB client for vector storage and semantic search
"""
import os
from typing import Optional
import chromadb
from chromadb.config import Settings


# ChromaDB configuration
CHROMADB_HOST = os.getenv("CHROMADB_HOST", "localhost")
CHROMADB_PORT = int(os.getenv("CHROMADB_PORT", "8000"))

# Singleton client instance
_client: Optional[chromadb.Client] = None


def get_chromadb_client() -> chromadb.Client:
    """
    Get or create ChromaDB client instance

    Uses HTTP client if CHROMADB_HOST is set (production),
    otherwise uses in-memory client (development/testing)
    """
    global _client

    if _client is None:
        if CHROMADB_HOST and CHROMADB_HOST != "localhost":
            # Production: Use HTTP client
            _client = chromadb.HttpClient(
                host=CHROMADB_HOST,
                port=CHROMADB_PORT,
                settings=Settings(
                    anonymized_telemetry=False,
                )
            )
            print(f"[ChromaDB] Connected to {CHROMADB_HOST}:{CHROMADB_PORT}")
        else:
            # Development: Use persistent client
            persist_directory = os.getenv("CHROMADB_PERSIST_DIR", "./data/chromadb")
            os.makedirs(persist_directory, exist_ok=True)

            _client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                )
            )
            print(f"[ChromaDB] Using persistent storage: {persist_directory}")

    return _client


def get_user_collection(user_id: int):
    """
    Get or create a ChromaDB collection for a specific user

    Each user has their own collection to store memory vectors

    Args:
        user_id: User ID

    Returns:
        ChromaDB Collection
    """
    client = get_chromadb_client()
    collection_name = f"user_memories_{user_id}"

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={
            "user_id": user_id,
            "description": f"Memory vectors for user {user_id}",
        }
    )

    return collection


def delete_user_collection(user_id: int) -> bool:
    """
    Delete a user's ChromaDB collection

    Used when user deletes their account

    Args:
        user_id: User ID

    Returns:
        True if deleted, False if not found
    """
    try:
        client = get_chromadb_client()
        collection_name = f"user_memories_{user_id}"
        client.delete_collection(name=collection_name)
        print(f"[ChromaDB] Deleted collection: {collection_name}")
        return True
    except Exception as e:
        print(f"[ChromaDB] Failed to delete collection: {e}")
        return False


def list_user_collections():
    """
    List all user collections in ChromaDB

    Useful for debugging and admin purposes

    Returns:
        List of collection names
    """
    try:
        client = get_chromadb_client()
        collections = client.list_collections()
        return [col.name for col in collections if col.name.startswith("user_memories_")]
    except Exception as e:
        print(f"[ChromaDB] Failed to list collections: {e}")
        return []


def reset_client():
    """Reset the singleton client (for testing)"""
    global _client
    _client = None
