"""
Retrieval pipeline script

"""

#Standard module
from pathlib import Path

#Langchain module

#Local modules
from rag.ingestion.embeddings import get_huggingface_embedding
from rag.vectordb.chroma_db import Persistent_ChromaDB

# ==========================================
# 1. INITIAL CONFIGURATION (PATHS AND VARIABLES)
# ==========================================

BASE_DIR = Path(__file__).parent.parent.parent

persistent_db_path =  BASE_DIR/"data"/ "chroma_db"

#Embedding model (HuggingFace)
embedding_function = get_huggingface_embedding()

# ==========================================
# 2. VECTOR DB SETUP
# ==========================================

#---SEARCH AND RANK RELEVANT DOCS---
vector_db = Persistent_ChromaDB(persistent_db_path,get_huggingface_embedding())

