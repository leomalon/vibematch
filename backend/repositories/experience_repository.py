"""
experience_repository.py

Read-side queries for the structured search: executes the query built by
QueryBuilder and loads the relationships needed for ranking and response
mapping. Also provides category-scoped queries (categories pages).
"""

#Third-party modules
import math

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

#Models
from backend.db.models.models import (
    Categoria, Experiencia, ExperienciaMood, Ubicacion,
    experiencia_categoria,
)

#Query builder
from backend.services.query_builder import build_select

#Helpers
from backend.ingestion.normalizers import to_slug

#Response schema
from backend.schemas.response import SearchResponse


def _load_options():
    return [
        selectinload(Experiencia.categorias),
        selectinload(Experiencia.companias),
        selectinload(Experiencia.tags),
        selectinload(Experiencia.experiencia_moods).selectinload(ExperienciaMood.mood),
        selectinload(Experiencia.programaciones),
        selectinload(Experiencia.ubicaciones),
    ]


def to_search_response(experiencia: Experiencia) -> SearchResponse:
    """Map an ORM Experiencia row to the public SearchResponse schema."""
    precio = None
    if experiencia.precio_min is not None:
        precio = float(experiencia.precio_min)
    elif experiencia.precio_max is not None:
        precio = float(experiencia.precio_max)

    direccion = ""
    latitud = None
    longitud = None
    if experiencia.ubicaciones:
        ubicacion = experiencia.ubicaciones[0]
        direccion = ubicacion.direccion or ""
        latitud = float(ubicacion.latitud) if ubicacion.latitud is not None else None
        longitud = float(ubicacion.longitud) if ubicacion.longitud is not None else None

    fecha_inicio = None
    hora_inicio = None
    if experiencia.programaciones:
        prog = experiencia.programaciones[0]
        fecha_inicio = prog.fecha_inicio.isoformat() if prog.fecha_inicio else None
        hora_inicio = prog.hora_inicio.strftime("%H:%M") if prog.hora_inicio else None

    return SearchResponse(
        titulo=experiencia.titulo,
        descripcion=experiencia.descripcion or "",
        url=experiencia.link_externo or "",
        direccion=direccion,
        categoria=experiencia.categorias[0].nombre if experiencia.categorias else "",
        precio=precio,
        moneda=experiencia.moneda or "PEN",
        mood=[em.mood.nombre for em in experiencia.experiencia_moods if em.mood],
        fecha_inicio=fecha_inicio,
        hora_inicio=hora_inicio,
        latitud=latitud,
        longitud=longitud,
    )


class ExperienceRepository:

    def __init__(self, db: Session):
        self.db = db

    def search(self, resolved) -> list[Experiencia]:
        stmt = build_select(resolved).options(*_load_options())
        return list(self.db.execute(stmt).scalars().all())

    def by_category(self, slug: str) -> list[Experiencia]:
        """Return experiences belonging to the category whose slug matches."""
        categorias = self.db.execute(select(Categoria)).scalars().all()

        match = next((c for c in categorias if to_slug(c.nombre) == slug), None)

        if match is None:
            return []

        stmt = (
            select(Experiencia)
            .join(experiencia_categoria, experiencia_categoria.c.experiencia_id == Experiencia.id)
            .where(experiencia_categoria.c.categoria_id == match.id)
            .options(*_load_options())
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_category_id(self, slug: str) -> int | None:
        categorias = self.db.execute(select(Categoria)).scalars().all()
        match = next((c for c in categorias if to_slug(c.nombre) == slug), None)
        return match.id if match else None

    def list_events(self, resolved, nearby_lat=None, nearby_lng=None, nearby_radius_km=5.0) -> list[Experiencia]:
        stmt = build_select(resolved).options(*_load_options())

        if nearby_lat is not None and nearby_lng is not None:
            lat_delta = nearby_radius_km / 111.0
            lng_delta = nearby_radius_km / (111.0 * math.cos(math.radians(nearby_lat)))
            stmt = stmt.outerjoin(Ubicacion, Ubicacion.experiencia_id == Experiencia.id)
            stmt = stmt.where(
                Ubicacion.latitud.isnot(None),
                Ubicacion.longitud.isnot(None),
                Ubicacion.latitud.between(nearby_lat - lat_delta, nearby_lat + lat_delta),
                Ubicacion.longitud.between(nearby_lng - lng_delta, nearby_lng + lng_delta),
            )

        return list(self.db.execute(stmt).scalars().all())
