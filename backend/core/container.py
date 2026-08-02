"""
cointainer.py

Initializes services and dependencies.
"""

#Standard modules
from pathlib import Path

#Third-party modules
from dotenv import load_dotenv

#Services
from backend.services.search_service import SearchService
from backend.services.rag_service import RagService

#Rag dependencies
from backend.ingestion.embeddings.embeddings_service import get_openai_embedding
from backend.ingestion.storage.chroma_repository import ChromaVectorStore

# ==========================================
# 1. CONFIG
# ==========================================

BASE_DIR = Path(__file__).parent.parent.parent
vector_db_path =  BASE_DIR/"data"/ "chroma_db"

#Embedding model
load_dotenv()
embedding_function = get_openai_embedding(model_name = "text-embedding-3-large")


# ==========================================
# 2. DEPENDENCIES
# ==========================================
#Rag Retrieval
rag_retriever = ChromaVectorStore(vector_db_path,embedding_function)

#Services
rag_service = RagService(rag_retriever)
search_service = SearchService(rag_service)