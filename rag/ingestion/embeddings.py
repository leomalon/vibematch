"""
Embedding function configuration module.

Provides factory functions to initialize embedding models from different providers,
with a unified interface for use in vector databases (e.g., ChromaDB).

Currently supported:
- Hugging Face SentenceTransformers models

Notes:
- Prefer multilingual models (e.g., BAAI/bge-m3) for non-English data.
- Device can be "cpu" or "cuda" depending on hardware availability.
"""

# Third-party modules
import chromadb.utils.embedding_functions as embedding_functions


# ==========================================
# EMBEDDING FACTORIES
# ==========================================

def get_huggingface_embedding(
    model_name: str = "BAAI/bge-small-en",
    device: str = "cpu"
):
    """
    Creates a Hugging Face embedding function compatible with ChromaDB.

    Args:
        model_name (str, optional): Name of the SentenceTransformer model.
            Defaults to "BAAI/bge-m3" (multilingual, recommended).
        device (str, optional): Execution device ("cpu" or "cuda").
            Defaults to "cpu".

    Returns:
        SentenceTransformerEmbeddingFunction: Configured embedding function.
    """
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name,
        device=device
    )

"""
Embedding function configuration module.

Provides factory functions to initialize embedding models from different providers,
with a unified interface for use in vector databases (e.g., ChromaDB).

Currently supported:
- Hugging Face SentenceTransformers models
- OpenAI embedding models

Notes:
- Prefer multilingual models (e.g., BAAI/bge-m3) for non-English data.
- OpenAI embeddings are strong for semantic search and multilingual tasks.
"""

# Third-party modules
import chromadb.utils.embedding_functions as embedding_functions
from openai import OpenAI


# ==========================================
# EMBEDDING FACTORIES
# ==========================================

def get_huggingface_embedding(
    model_name: str = "BAAI/bge-small-en",
    device: str = "cpu"
):
    """
    Creates a Hugging Face embedding function compatible with ChromaDB.
    """
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name,
        device=device
    )


def get_openai_embedding(
    model_name: str = "text-embedding-3-small"
):
    """
    Creates an OpenAI embedding function compatible with ChromaDB.

    Args:
        model_name (str, optional): OpenAI embedding model.
            Options:
            - "text-embedding-3-small" (cheap, fast)
            - "text-embedding-3-large" (higher quality)

    Returns:
        OpenAIEmbeddingFunction: Configured embedding function.
    """

    # ChromaDB already provides a wrapper for OpenAI
    return embedding_functions.OpenAIEmbeddingFunction(
        api_key=None,  # uses OPENAI_API_KEY env variable
        model_name=model_name
    )