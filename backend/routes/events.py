"""
Events search API endpoint (HTTP)

Handles:

HTTP request/response and validation (via Pydantic)

"""

#Third-party modules
from fastapi import APIRouter

#Local modules
from schemas.event import QueryRequest, EventResponse
from services.retrieval import RetrievalService
from ...rag.retrieval.query_pipeline import vector_db

router = APIRouter()

retrieval_service = RetrievalService(vectorstore=vector_db)


@router.post("/search", response_model=list[EventResponse])
def search_events(request: QueryRequest):
    results = retrieval_service.search(request.query)
    return results