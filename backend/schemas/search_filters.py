"""
search_filters.py

Resolved query filters used by the structured search pipeline.

The LLM turns a free-text query into a JSON of filters; the CatalogResolver
turns that JSON into this concrete, ID-based structure that the query builder
and ranking service can consume.
"""

from datetime import date, time

from pydantic import BaseModel, Field


class ResolvedAvailability(BaseModel):
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    hora_inicio: time | None = None
    hora_fin: time | None = None


class ResolvedQuery(BaseModel):
    """All filters normalized to catalog IDs, ready for SQL building."""

    disponibilidad: ResolvedAvailability = Field(default_factory=ResolvedAvailability)

    pais_id: int | None = None
    ciudad_id: int | None = None
    distrito_id: int | None = None

    tipo_experiencia_id: int | None = None
    categoria_id: list[int] = Field(default_factory=list)
    moods_id: list[int] = Field(default_factory=list)
    compania_id: list[int] = Field(default_factory=list)

    precio_min: float | None = None
    precio_max: float | None = None

    tags: list[str] = Field(default_factory=list)
    busqueda_texto: list[str] = Field(default_factory=list)
    mood_slug: str | None = None
