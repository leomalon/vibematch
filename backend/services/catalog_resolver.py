"""
catalog_resolver.py

Transforms the JSON filters produced by the LLM (QueryUnderstanding) into a
concrete ResolvedQuery where catalog entries are plain IDs.

The LLM is told to return catalog entries as full objects ({"id": .., "nombre": ..});
this resolver is defensive: it also accepts raw ids/strings and falls back to
name-based resolution using the catalogs, so a slightly off LLM output does
not break the query.
"""

#Standard modules
from datetime import date, time
from typing import Any

#Schemas
from backend.schemas.search_filters import ResolvedQuery, ResolvedAvailability

#Helpers
from backend.ingestion.normalizers import normalize_key


def _extract_ids(value: Any) -> list[int]:
    """Coerce an object / list of objects / id into a flat list of int ids."""
    if not value:
        return []

    if isinstance(value, dict):
        value = [value]

    if not isinstance(value, list):
        value = [value]

    ids = []
    for item in value:
        if isinstance(item, dict) and item.get("id") is not None:
            ids.append(int(item["id"]))
        else:
            try:
                ids.append(int(item))
            except (TypeError, ValueError):
                continue
    return ids


def _extract_single_id(value: Any) -> int | None:
    ids = _extract_ids(value)
    return ids[0] if ids else None


def _resolve_by_name(catalogs: dict, key: str, name: str | None) -> int | None:
    """Resolve a catalog name to its id, using a normalized-name lookup."""
    if not name:
        return None

    items = catalogs.get(key, [])
    target = normalize_key(name)

    for item in items:
        if item.get("nombre") and normalize_key(item["nombre"]) == target:
            return item["id"]
    return None


class CatalogResolver:

    @staticmethod
    def resolve(filters: dict, catalogs: dict) -> ResolvedQuery:
        """Convert LLM filter JSON into a ResolvedQuery."""

        ubicacion = filters.get("ubicacion") or {}
        preferencias = filters.get("preferencias") or {}
        presupuesto = filters.get("presupuesto") or {}
        disponibilidad = filters.get("disponibilidad") or {}

        pais = ubicacion.get("pais")
        ciudad = ubicacion.get("ciudad")
        distrito = ubicacion.get("distrito")

        # Prefer ID from the object; fall back to name resolution.
        pais_id = _extract_single_id(pais)
        if pais_id is None:
            pais_id = _resolve_by_name(catalogs, "pais", pais.get("nombre") if isinstance(pais, dict) else pais)

        ciudad_id = _extract_single_id(ciudad)
        if ciudad_id is None:
            ciudad_id = _resolve_by_name(catalogs, "ciudad", ciudad.get("nombre") if isinstance(ciudad, dict) else ciudad)

        distrito_id = _extract_single_id(distrito)
        if distrito_id is None:
            distrito_id = _resolve_by_name(catalogs, "distritos", distrito.get("nombre") if isinstance(distrito, dict) else distrito)

        tipo_id = _extract_single_id(preferencias.get("tipo_experiencia"))
        if tipo_id is None:
            tipo_value = preferencias.get("tipo_experiencia")
            nombre = tipo_value.get("nombre") if isinstance(tipo_value, dict) else None
            tipo_id = _resolve_by_name(catalogs, "tipo_experiencia", nombre)

        categoria_ids = _extract_ids(preferencias.get("categoria"))
        mood_ids = _extract_ids(preferencias.get("moods"))
        compania_ids = _extract_ids(preferencias.get("companias"))

        return ResolvedQuery(
            disponibilidad=ResolvedAvailability(
                fecha_inicio=_parse_date(disponibilidad.get("fecha_inicio")),
                fecha_fin=_parse_date(disponibilidad.get("fecha_fin")),
                hora_inicio=_parse_time(disponibilidad.get("hora_inicio")),
                hora_fin=_parse_time(disponibilidad.get("hora_fin")),
            ),
            pais_id=pais_id,
            ciudad_id=ciudad_id,
            distrito_id=distrito_id,
            tipo_experiencia_id=tipo_id,
            categoria_id=categoria_ids,
            moods_id=mood_ids,
            compania_id=compania_ids,
            precio_min=_parse_number(presupuesto.get("precio_min")),
            precio_max=_parse_number(presupuesto.get("precio_max")),
            tags=[str(t).lower().strip() for t in (filters.get("tags") or []) if str(t).strip()],
            busqueda_texto=[str(t).strip() for t in (filters.get("busqueda_texto") or []) if str(t).strip()],
        )


def _parse_date(value) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        return None


def _parse_time(value) -> time | None:
    if not value:
        return None
    try:
        return time.fromisoformat(str(value).strip())
    except ValueError:
        return None


def _parse_number(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
