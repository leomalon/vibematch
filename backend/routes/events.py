"""
Events search API endpoint (HTTP)

Handles:

HTTP request/response and validation (via Pydantic)

"""

#Standard modules
from pathlib import Path
import json

#Third-party modules
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
import unicodedata
from dotenv import load_dotenv

#Schemas
from backend.schemas.request import SearchRequest
from backend.schemas.response import SearchResponse

#DB Dependencies
from backend.db.session import get_db

#Service dependencies
from backend.core.container import search_service

# ==========================================
# 1. CONFIG
# ==========================================

router = APIRouter()


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
@router.post("/search", response_model=list[SearchResponse])
def search_events(request: SearchRequest,db: Session = Depends(get_db)):

    return search_service.search(request.query,db)


@router.post("/rag_search", response_model=list[SearchResponse])
def rag_search(request: SearchRequest):

    return search_service.rag_search(request.query,"vibematch_collection",10)


# @router.get("/categories/{category}")
# def get_events_by_category(category: str):
    
#     events = load_json_data(data_path)
    
#     results = []

#     for event in events:
            
#         # normalize both sides
#         event_cat = normalize_text(event["categoria_espaniol"])

#         if event_cat == category:
#             results.append({
#                     "categoria": event["categoria_espaniol"],
#                     "url": event["url_evento"],
#                     "titulo": event["titulo"],
#                     "descripcion": event["descripcion"],
#                     "precio": event["precio"],
#                     "moneda": event["moneda"],
#                     "mood": event["mood"],
#                     "tags":event["tags"]
#                 })

#     return results
