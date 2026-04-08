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