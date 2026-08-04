"""
search_service.py

Coordination Layer

Orchestrates the structured search:

1. Loads the catalogs from the database.
2. Asks the LLM (QueryUnderstanding) to turn the user query into filter JSON.
3. Resolves those filters to catalog IDs (CatalogResolver).
4. Executes the query (ExperienceRepository).
5. Ranks the results (RankingService).
6. Maps them to the public SearchResponse schema.
"""

#Standard modules
import os
from datetime import datetime
import json

#Third-party modules
from dotenv import load_dotenv

#Services
from backend.services.understand_service import QueryUnderstanding
from backend.services.catalog_service import CatalogService
from backend.services.catalog_resolver import CatalogResolver
from backend.services.ranking_service import RankingService

#LLM
from backend.llm.openai_client import ChatOpenAI

#Repositories
from backend.repositories.catalog_repository import CatalogRepository
from backend.repositories.experience_repository import ExperienceRepository, to_search_response

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")


class SearchService:

    def __init__(self, rag_service):
        self.rag_service = rag_service

    def search(self, query: str, db):

        today = datetime.now()
        current_date = today.strftime("%Y-%m-%d")
        current_time = today.strftime("%H:%M")

        #---CATALOG SERVICE---
        catalog_service = CatalogService(CatalogRepository(db))
        catalogs_dict = catalog_service.get_catalogs().model_dump()

        #---QUERY UNDERSTANDING SERVICE---
        query_understanding = QueryUnderstanding(ChatOpenAI(openai_key))
        json_filters = query_understanding.parse(query, catalogs_dict, current_date, current_time)
        json_filters = json.loads(json_filters)

        #---CATALOG RESOLVER---
        resolved = CatalogResolver.resolve(json_filters, catalogs_dict)

        #---SEARCH + RANKING---
        experiences = ExperienceRepository(db).search(resolved)
        ranked = RankingService.rank(experiences, resolved)

        return [to_search_response(exp) for exp in ranked[:20]]

    def rag_search(self, query: str, collection, n_docs):
        return self.rag_service.retrieve(query, collection, n_docs)
