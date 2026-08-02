"""
postgres_writer.py


Wraps a Postgres instance to use in ingestion of data.


"""
from pathlib import Path



class PostgresWriter():
    """
    ChromaDB Writer for persistent vector database.
    """
    pass

    # def __init__(self,persisten_path:str|Path,embedding_function):
    #     self.persistent_path = persisten_path
    #     self.embedding_function = embedding_function
    #     self.persistent_client = chromadb.PersistentClient(
    #         path=self.persistent_path
    #     )