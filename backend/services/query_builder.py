"""
query_builder.py

Builds the SQLAlchemy SELECT that filters Experiencia rows according to a
ResolvedQuery (structured filters derived from the user's free-text query).

Design notes:
- Multi-valued filters (categorias, moods, companias, tags) use joins over the
  association tables; `.distinct()` removes the duplicates those joins create.
- Availability uses a LEFT JOIN on programacion so permanent experiences
  (which have no programacion rows) are still returned.
- Ranking is performed in Python (RankingService), so no SQL ordering is needed.
"""

#Third-party modules
from sqlalchemy import and_, or_, select

#Models
from backend.db.models.models import (
    Experiencia, ExperienciaMood, Programacion, Tag, Ubicacion,
    experiencia_categoria, experiencia_compania, experiencia_tag,
)

#Schemas
from backend.schemas.search_filters import ResolvedQuery

#Helpers
from backend.ingestion.normalizers import normalize_key


def build_select(resolved: ResolvedQuery):
    stmt = select(Experiencia).distinct()

    if resolved.tipo_experiencia_id is not None:
        stmt = stmt.where(Experiencia.tipo_id == resolved.tipo_experiencia_id)

    if resolved.categoria_id:
        stmt = stmt.join(
            experiencia_categoria,
            experiencia_categoria.c.experiencia_id == Experiencia.id,
        ).where(experiencia_categoria.c.categoria_id.in_(resolved.categoria_id))

    if resolved.moods_id:
        stmt = stmt.join(
            ExperienciaMood,
            ExperienciaMood.experiencia_id == Experiencia.id,
        ).where(ExperienciaMood.mood_id.in_(resolved.moods_id))

    if resolved.compania_id:
        stmt = stmt.join(
            experiencia_compania,
            experiencia_compania.c.experiencia_id == Experiencia.id,
        ).where(experiencia_compania.c.compania_id.in_(resolved.compania_id))

    # Location filter (most specific one wins).
    if resolved.distrito_id or resolved.ciudad_id or resolved.pais_id:
        stmt = stmt.join(Ubicacion, Ubicacion.experiencia_id == Experiencia.id)

        if resolved.distrito_id:
            stmt = stmt.where(Ubicacion.distrito_id == resolved.distrito_id)
        elif resolved.ciudad_id:
            stmt = stmt.where(Ubicacion.ciudad_id == resolved.ciudad_id)
        elif resolved.pais_id:
            stmt = stmt.where(Ubicacion.pais_id == resolved.pais_id)

    # Budget: keep rows whose range overlaps the requested one.
    if resolved.precio_min is not None:
        stmt = stmt.where(
            or_(
                Experiencia.precio_max.is_(None),
                Experiencia.precio_max >= resolved.precio_min,
            )
        )
    if resolved.precio_max is not None:
        stmt = stmt.where(
            or_(
                Experiencia.precio_min.is_(None),
                Experiencia.precio_min <= resolved.precio_max,
            )
        )

    # Availability: date/hour overlap on programacion (LEFT JOIN keeps
    # permanent experiences, which have no programacion rows).
    av = resolved.disponibilidad
    if av.fecha_inicio or av.fecha_fin or av.hora_inicio or av.hora_fin:
        stmt = stmt.outerjoin(Programacion, Programacion.experiencia_id == Experiencia.id)

        overlap = []
        if av.fecha_inicio:
            overlap.append(or_(Programacion.fecha_fin.is_(None), Programacion.fecha_fin >= av.fecha_inicio))
        if av.fecha_fin:
            overlap.append(or_(Programacion.fecha_inicio.is_(None), Programacion.fecha_inicio <= av.fecha_fin))
        if av.hora_inicio:
            overlap.append(or_(Programacion.hora_fin.is_(None), Programacion.hora_fin >= av.hora_inicio))
        if av.hora_fin:
            overlap.append(or_(Programacion.hora_inicio.is_(None), Programacion.hora_inicio <= av.hora_fin))

        stmt = stmt.where(
            or_(Experiencia.es_permanente.is_(True), and_(*overlap))
        )

    # Tags: match stored normalized names.
    if resolved.tags:
        normalized_tags = [normalize_key(t) for t in resolved.tags]
        stmt = (
            stmt.join(experiencia_tag, experiencia_tag.c.experiencia_id == Experiencia.id)
            .join(Tag, Tag.id == experiencia_tag.c.tag_id)
            .where(Tag.nombre.in_(normalized_tags))
        )

    # Free text: title or description contains any of the terms.
    if resolved.busqueda_texto:
        like_terms = or_(
            *[
                or_(
                    Experiencia.titulo.ilike(f"%{term}%"),
                    Experiencia.descripcion.ilike(f"%{term}%"),
                )
                for term in resolved.busqueda_texto
            ]
        )
        stmt = stmt.where(like_terms)

    return stmt
