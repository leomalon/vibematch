"""
Events search API endpoint (HTTP)

Handles:

HTTP request/response and validation (via Pydantic)

"""

#Standard modules
from pathlib import Path
import json
from datetime import date, timedelta

#Third-party modules
from fastapi import APIRouter,Depends, Query
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

#Repositories
from backend.repositories.experience_repository import ExperienceRepository, to_search_response
from backend.db.models.models import Mood

#Schemas
from backend.schemas.search_filters import ResolvedQuery, ResolvedAvailability

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


@router.get("/categories/{slug}", response_model=list[SearchResponse])
def get_events_by_category(slug: str, db: Session = Depends(get_db)):

    experiences = ExperienceRepository(db).by_category(slug)

    return [to_search_response(exp) for exp in experiences]


@router.get("/list", response_model=list[SearchResponse])
def list_events(
    categoria: str | None = Query(None, description="Category slug"),
    mood: str | None = Query(None, description="Mood slug"),
    fecha: str | None = Query(None, description="hoy / manana / YYYY-MM-DD"),
    precio_max: float | None = Query(None, description="Max price (0 = free)"),
    nearby_lat: float | None = Query(None, description="Latitude for nearby search"),
    nearby_lng: float | None = Query(None, description="Longitude for nearby search"),
    nearby_radius_km: float = Query(5.0, description="Radius in km"),
    db: Session = Depends(get_db),
):

    repo = ExperienceRepository(db)
    resolved = ResolvedQuery()

    # Category filter.
    if categoria:
        cat_id = repo.get_category_id(categoria)
        if cat_id:
            resolved.categoria_id = [cat_id]

    # Mood filter.
    if mood:
        from backend.ingestion.normalizers import normalize_key
        mood_row = db.execute(select(Mood)).scalars().all()
        match = next((m for m in mood_row if normalize_key(m.nombre) == mood), None)
        if match:
            resolved.moods_id = [match.id]

    # Date filter.
    if fecha:
        today = date.today()
        if fecha == "hoy":
            resolved.disponibilidad = ResolvedAvailability(fecha_inicio=today, fecha_fin=today)
        elif fecha == "manana":
            tomorrow = today + timedelta(days=1)
            resolved.disponibilidad = ResolvedAvailability(fecha_inicio=tomorrow, fecha_fin=tomorrow)
        else:
            try:
                d = date.fromisoformat(fecha)
                resolved.disponibilidad = ResolvedAvailability(fecha_inicio=d, fecha_fin=d)
            except ValueError:
                pass

    # Price filter.
    if precio_max is not None:
        resolved.precio_max = precio_max

    experiences = repo.list_events(resolved, nearby_lat, nearby_lng, nearby_radius_km)

    return [to_search_response(e) for e in experiences]
