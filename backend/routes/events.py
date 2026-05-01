"""
Events search API endpoint (HTTP)

Handles:

HTTP request/response and validation (via Pydantic)

"""

#Standard modules
import os
from pathlib import Path
import json

#Third-party modules
from fastapi import APIRouter
from dotenv import load_dotenv
import unicodedata

#Local modules
from backend.schemas.event import QueryRequest, EventResponse
from backend.services.retrieval import RetrievalService
from backend.services.understanding import QueryUnderstandingService
from backend.services.response_filter import ResponseFilterService

from rag.retrieval.query_pipeline import vector_db

#Llm clients
from rag.llm.openai import ChatOpenAI



# ==========================================
# 1. CONFIG VARIABLES
# ==========================================
load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")

llm_client = ChatOpenAI(api_key=openai_api_key,model="gpt-4.1-mini")

router = APIRouter()

query_understanding_service = QueryUnderstandingService(llm_client)
response_filter_service = ResponseFilterService(llm_client)
retrieval_service = RetrievalService(vectorstore=vector_db)

#Events

# Always resolve from root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

#Config paths
data_path  = BASE_DIR / "data" / "processed"/"semantic_events.json"

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def load_json_data(data_path: str | Path):

    with open(data_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

        if not content:
            return []

        return json.loads(content)

def normalize_text(text: str) -> str:
    return (
        unicodedata.normalize("NFD", text)
        .encode("ascii", "ignore")
        .decode("utf-8")
        .lower()
        .strip()
    )

# ==========================================
# 3. ENDPOINTS
# ==========================================
@router.post("/search", response_model=list[EventResponse])
def search_events(request: QueryRequest):
    structured_query = query_understanding_service.parse(request.query)
    results = retrieval_service.search_top_n(structured_query,"vibe_collection",12,8)

    parsed_results = results

    parsed_results = [
        {
            "titulo": event.get("titulo"),
            "descripcion": event.get("descripcion"),
            "url": event.get("url"),
            "direccion": event.get("direccion"),
            "precio": event.get("precio"),
            "moneda": event.get("moneda"),
            "categoria": event.get("categoria"),
            "tags": event.get("tags"),
        }
        for event in results
    ]

    return parsed_results

@router.get("/categories/{category}",response_model=list[EventResponse])
def get_events_by_category(category: str):
    
    events = load_json_data(data_path)
    
    results = []

    for event in events:
            
        # normalize both sides
        event_cat = normalize_text(event["categoria_espaniol"])

        if event_cat == category:
            results.append({
                    "categoria": event["categoria_espaniol"],
                    "url": event["url_evento"],
                    "titulo": event["titulo"],
                    "descripcion": event["descripcion"],
                    "precio": event["precio"],
                    "moneda": event["moneda"],
                    "mood": event["mood"],
                    "tags":event["tags"]
                })

    return results