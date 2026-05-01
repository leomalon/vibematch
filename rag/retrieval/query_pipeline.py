"""
Retrieval pipeline script

"""

#Standard module
from pathlib import Path

#Third-party modules
from dotenv import load_dotenv

#Local modules
from rag.ingestion.embeddings import get_openai_embedding
from rag.vectordb.chroma_db import Persistent_ChromaDB

# ==========================================
# 1. INITIAL CONFIGURATION (PATHS AND VARIABLES)
# ==========================================

BASE_DIR = Path(__file__).parent.parent.parent

persistent_db_path =  BASE_DIR/"data"/ "chroma_db"

#Embedding model
load_dotenv()
embedding_function = get_openai_embedding(model_name = "text-embedding-3-large")

# ==========================================
# 2. VECTOR DB SETUP
# ==========================================

#---SEARCH AND RANK RELEVANT DOCS---
vector_db = Persistent_ChromaDB(persistent_db_path,embedding_function)

