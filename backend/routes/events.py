"""
Events search API endpoint (HTTP)

Handles:

HTTP request/response and validation (via Pydantic)

"""

#Standard modules
import os

#Third-party modules
from fastapi import APIRouter
from dotenv import load_dotenv

#Local modules
from backend.schemas.event import QueryRequest, EventResponse
from backend.services.retrieval import RetrievalService
from backend.services.understanding import QueryUnderstandingService
from backend.services.response_filter import ResponseFilterService

from rag.retrieval.query_pipeline import vector_db


load_dotenv()

ollama_api_key = os.environ.get("OLLAMA_API_KEY")

router = APIRouter()

query_understanding_service = QueryUnderstandingService(ollama_api_key)
response_filter_service = ResponseFilterService(ollama_api_key)
retrieval_service = RetrievalService(vectorstore=vector_db)


@router.post("/search", response_model=list[EventResponse])
def search_events(request: QueryRequest):
    structured_query = query_understanding_service.parse(request.query)
    results = retrieval_service.search_top_n(structured_query,"vibe_collection",7,5)

    if not results:
        return []

    filter_response = response_filter_service.json_response(results,structured_query)

    return filter_response