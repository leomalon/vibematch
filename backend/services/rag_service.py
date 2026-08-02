"""
rag_service.py

Retrieval service script

"""

# ==========================================
# 1. RAG RETRIEVAL SERVICE
# ==========================================

class RagService:

    def __init__(self, retriever):
        self.retriever = retriever

    def retrieve(self, query, collection, n_docs):
        return self.retriever.retrieve_documents(query, collection, n_docs)




        