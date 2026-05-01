"""
RAG Retrieval wrapper for API call.

"""

class RetrievalService:

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def search_top_n(self, query: str, collection_name:str, k: int = 7,top_n:int=5):
        results = self.vectorstore.search_documents(query,collection_name,k)

        events = results["documents"][0]
        events_metadata = results["metadatas"][0]
        distances = results["distances"][0]

        # Pair and sort (lower distance = better)
        ranked_events = sorted(zip(events, distances,events_metadata), key=lambda x: x[1])

        # Keep top-n only
        top_events = [metadata for event, _,metadata in ranked_events[:top_n]]

        return top_events