"""
Chroma DB configuration script.

Wraps a Chroma Persistent Client to use in ingestion and retrieval pipeline.


"""
from pathlib import Path
import chromadb


class Persistent_ChromaDB():

    def __init__(self,persisten_path:str|Path,embedding_function):
        self.persistent_path = persisten_path
        self.embedding_function = embedding_function
        self.persistent_client = chromadb.PersistentClient(
            path=self.persistent_path
        )


    def create_vector_db(self,collection_name:str,documents:list):

        client = self.persistent_client

        embedding_function = self.embedding_function

        # Create or get collection (equivalent to a table)
        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            configuration={
            "hnsw": {
                "space": "cosine",
                
                #Controls how many candidates are considered during the 
                # process of inserting a new vector and selecting the best connections neighbors
                "ef_construction": 100
            }}
        )

        collection.add(
            documents=documents,
            ids=[f"id{i+1}" for i in range(len(documents))]
        )
    
    def search_documents(self,query:str,collection_name:str,n_docs:int):
        
        client = self.persistent_client

        collection = client.get_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

        docs = collection.query(
            query_texts=[query],
            n_results=n_docs,
            include=["documents", "distances"]
        )

        return docs
