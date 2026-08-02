"""
search_service.py

Coordination Layer

"""
#Standard modules
import os
from datetime import datetime
import json

#Third-party modules
from dotenv import load_dotenv

#Services
from proyectos_portafolio.VibeMatch.backend.services.understand_service import QueryUnderstanding
from backend.services.catalog_service import CatalogService
# from backend.services.query_builder import QueryBuilder

#Local Dependencies
from backend.llm.openai_client import ChatOpenAI

#Repositories
from backend.repositories.catalog_repository import CatalogRepository

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

today = datetime.now()

current_date = today.strftime("%Y-%m-%d")
current_time = today.strftime("%H:%M")

class SearchService:

    def __init__(self,rag_service):
        self.rag_service = rag_service

    def search(query: str, db):

        #---CATALOG SERVICE---
        catalog_repo = CatalogRepository(db)

        catalog_service = CatalogService(catalog_repo)

        catalogs = catalog_service.get_catalogs() #pydantic class
        catalogs_dict = catalogs.model_dump() #convert to dict

        #---QUERY UNDERSTANDING SERVICE---
        query_understanding = QueryUnderstanding(ChatOpenAI(openai_key))

        json_filters = query_understanding.parse(query, catalogs_dict,current_date, current_time)

        json_filters = json.loads(json_filters)

        #---CATALOG RESOLVER---
        print(json_filters)
        

        #---UPDATE JSON FILTERS---


        # return json_filters

        # resolved = CatalogResolver.resolve(filters)

        # sql = QueryBuilder.build(resolved)

        # experiences = repository.search(sql)

        # ranked = RankingService.rank(
        #     experiences,
        #     filters
        # )

        # return ranked

    def rag_search(self,query,collection,n_docs):
        
        docs = self.rag_service.retrieve(query, collection, n_docs)

        return docs