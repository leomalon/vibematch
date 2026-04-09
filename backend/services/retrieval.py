"""
RAG Retrieval wrapper for API call.

"""

class RetrievalService:

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def search_top_n(self, query: str, collection_name:str, k: int = 5,top_n:int=7):
        results = self.vectorstore.search_documents(query,collection_name,k)

        docs = results["documents"][0]
        docs_metadata = results["metadatas"][0]
        distances = results["distances"][0]

        # Pair and sort (lower distance = better)
        ranked_documents = sorted(zip(docs, distances,docs_metadata), key=lambda x: x[1])

        # Keep top-n only
        top_docs = [(doc,metadata) for doc, _,metadata in ranked_documents[:top_n]]


        events = [
            f"[EVENTO {i+1}]\n"
            f"{doc}\n"
            f"Título: {meta.get('titulo')}\n"
            f"URL: {meta.get('url')}"
            f"Categoria evento: {meta.get("categoria")}"
            f"Precio: {meta.get("moneda")} {meta.get("precio")}"
            for i, (doc, meta) in enumerate(top_docs)
        ]

        return events