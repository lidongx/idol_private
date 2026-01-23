"""
Embedding service for generating text vectors
"""
import os
from typing import List
from sentence_transformers import SentenceTransformer


# Model configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Singleton model instance
_model = None


def get_embedding_model() -> SentenceTransformer:
    """
    Get or load the embedding model

    Uses sentence-transformers for generating embeddings
    Default model: all-MiniLM-L6-v2 (384 dimensions)

    Returns:
        SentenceTransformer model
    """
    global _model

    if _model is None:
        print(f"[Embedding] Loading model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"[Embedding] Model loaded successfully (dim={_model.get_sentence_embedding_dimension()})")

    return _model


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for a single text

    Args:
        text: Input text

    Returns:
        List of floats representing the embedding vector
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    model = get_embedding_model()

    # Generate embedding
    embedding = model.encode(text, convert_to_numpy=True)

    # Convert to list for JSON serialization
    return embedding.tolist()


async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embedding vectors for multiple texts (batch)

    Args:
        texts: List of input texts

    Returns:
        List of embedding vectors
    """
    if not texts:
        raise ValueError("Texts list cannot be empty")

    model = get_embedding_model()

    # Generate embeddings in batch (more efficient)
    embeddings = model.encode(texts, convert_to_numpy=True)

    # Convert to list for JSON serialization
    return [emb.tolist() for emb in embeddings]


def get_embedding_dimension() -> int:
    """
    Get the dimension of the embedding model

    Returns:
        Dimension size (e.g., 384 for all-MiniLM-L6-v2)
    """
    model = get_embedding_model()
    return model.get_sentence_embedding_dimension()


def reset_model():
    """Reset the singleton model (for testing)"""
    global _model
    _model = None
