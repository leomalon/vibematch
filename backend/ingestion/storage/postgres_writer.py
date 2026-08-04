"""
postgres_writer.py

Writes scraped + semantically enriched events into the normalized PostgreSQL
schema (experiencia, programacion, ubicacion, tag and association tables).

The writer is idempotent: it uses `experiencia.link_externo` (the event URL)
as a natural key and skips events that already exist.
"""

#Standard modules
from datetime import date, time

#Third-party modules
from sqlalchemy import select
from sqlalchemy.orm import Session

#Models
from backend.db.models.models import (
    Experiencia, ExperienciaMood, Programacion, Ubicacion,
    Categoria, Mood, Compania, Tag, Tipo, Pais, Ciudad, Distrito, Negocio,
    experiencia_categoria, experiencia_compania, experiencia_tag,
)

#Helpers
from backend.ingestion.normalizers import normalize_key, resolve_country, resolve_district, clean_number


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


class PostgresWriter:
    """
    Persists events to PostgreSQL.

    Args:
        db: SQLAlchemy Session.
    """

    def __init__(self, db: Session):
        self.db = db
        self._catalogs_loaded = False

    # ==========================================
    # 1. PUBLIC API
    # ==========================================

    def save(self, events: list[dict]) -> int:
        """
        Write every event to the database. Each event is wrapped in a savepoint
        so a single failing event is skipped without breaking the rest.

        Returns the number of events actually written (excluding skips).
        """
        if not self._catalogs_loaded:
            self._load_catalogs()

        written = skipped = failed = 0

        for event in events:
            try:
                with self.db.begin_nested():
                    result = self._write_event(event)
            except Exception as exc:  # noqa: BLE001 - keep ingestion alive
                print(f"[PostgresWriter] error en evento '{event.get('titulo')}': {exc}")
                failed += 1
                continue

            if result == "written":
                written += 1
            else:
                skipped += 1

        self.db.commit()

        print(
            f"[PostgresWriter] escritos={written} omitidos={skipped} fallidos={failed}"
        )
        return written

    # ==========================================
    # 2. CATALOG LOOKUPS
    # ==========================================

    def _load_catalogs(self):
        db = self.db

        self.categoria_lookup = self._build_lookup(select(Categoria))
        self.mood_lookup = self._build_lookup(select(Mood))
        self.compania_lookup = self._build_lookup(select(Compania))
        self.pais_lookup = self._build_lookup(select(Pais))
        self.ciudad_lookup = self._build_lookup(select(Ciudad))

        self.tipo_by_id = {
            t.id: t for t in db.execute(select(Tipo)).scalars().all()
        }

        districts = db.execute(select(Distrito)).scalars().all()

        # distrito may contain duplicate names (e.g. "Villa El Salvador");
        # index by normalized name keeping the first row.
        self.district_lookup = {}
        self.district_rows = {}

        for d in districts:
            key = normalize_key(d.nombre)
            self.district_lookup.setdefault(key, d.nombre)
            self.district_rows.setdefault(key, d)

        self.negocio_ids = set(db.execute(select(Negocio.id)).scalars().all())

        self._catalogs_loaded = True

    def _build_lookup(self, stmt) -> dict:
        """Return {normalized_name: orm_row} for a catalog table."""
        rows = self.db.execute(stmt).scalars().all()
        return {normalize_key(r.nombre): r for r in rows}

    def _get_or_create(self, lookup, model, name: str | None):
        """Fetch by normalized name or create the row (and refresh the lookup)."""
        if not name:
            return None

        key = normalize_key(name)

        if key in lookup:
            return lookup[key]

        row = model(nombre=str(name).strip())
        self.db.add(row)
        self.db.flush()
        lookup[key] = row
        return row

    # ==========================================
    # 3. RESOLVERS
    # ==========================================

    def _resolve_tipo(self, value) -> int:
        try:
            tipo_id = int(value)
        except (TypeError, ValueError):
            return 1  # default: evento

        if tipo_id in self.tipo_by_id:
            return tipo_id

        return 1

    def _resolve_negocio(self, value) -> int | None:
        try:
            negocio_id = int(value)
        except (TypeError, ValueError):
            return None

        return negocio_id if negocio_id in self.negocio_ids else None

    # ==========================================
    # 4. EVENT WRITING
    # ==========================================

    def _write_event(self, event: dict) -> str:
        url = event.get("url_evento")

        if not url:
            return "skipped"

        exists = self.db.execute(
            select(Experiencia.id).where(Experiencia.link_externo == url)
        ).scalar_one_or_none()

        if exists is not None:
            return "skipped"

        experiencia = Experiencia(
            tipo_id=self._resolve_tipo(event.get("tipo_experiencia")),
            titulo=(event.get("titulo") or "Sin título").strip(),
            descripcion=event.get("descripcion"),
            es_permanente=bool(event.get("es_permanente", False)),
            precio_min=clean_number(event.get("precio_min")),
            precio_max=clean_number(event.get("precio_max")),
            moneda=(event.get("moneda") or "PEN").upper()[:3],
            link_externo=url,
            negocio_id=self._resolve_negocio(event.get("negocio")),
        )
        self.db.add(experiencia)
        self.db.flush()  # assign experiencia.id

        self._link_categoria(experiencia, event)
        self._link_moods(experiencia, event)
        self._link_companias(experiencia, event)
        self._link_tags(experiencia, event)
        self._write_programacion(experiencia, event)
        self._write_ubicacion(experiencia, event)

        return "written"

    def _link_categoria(self, experiencia: Experiencia, event: dict):
        categoria = self._get_or_create(self.categoria_lookup, Categoria, event.get("categoria_espaniol"))

        if categoria is None:
            return

        self.db.execute(
            experiencia_categoria.insert().values(
                experiencia_id=experiencia.id, categoria_id=categoria.id
            )
        )

    def _link_moods(self, experiencia: Experiencia, event: dict):
        for mood_name in dict.fromkeys(event.get("mood") or []):
            mood = self._get_or_create(self.mood_lookup, Mood, mood_name)

            if mood is None:
                continue

            self.db.add(
                ExperienciaMood(
                    experiencia_id=experiencia.id,
                    mood_id=mood.id,
                    peso=1.0,
                )
            )

    def _link_companias(self, experiencia: Experiencia, event: dict):
        for publico in dict.fromkeys(event.get("publico") or []):
            compania = self._get_or_create(self.compania_lookup, Compania, publico)

            if compania is None:
                continue

            self.db.execute(
                experiencia_compania.insert().values(
                    experiencia_id=experiencia.id, compania_id=compania.id
                )
            )

    def _link_tags(self, experiencia: Experiencia, event: dict):
        for raw_tag in dict.fromkeys(event.get("tags") or []):
            if not raw_tag:
                continue

            # Normalize tag for a unique, lowercase-friendly table.
            tag_name = normalize_key(str(raw_tag).lstrip("#"))

            if not tag_name:
                continue

            tag = self._get_or_create(self._tag_lookup(), Tag, tag_name)

            if tag is None:
                continue

            self.db.execute(
                experiencia_tag.insert().values(
                    experiencia_id=experiencia.id, tag_id=tag.id
                )
            )

    def _write_programacion(self, experiencia: Experiencia, event: dict):
        fecha_inicio = _parse_date(event.get("fecha_inicio"))
        fecha_fin = _parse_date(event.get("fecha_fin"))
        hora_inicio = _parse_time(event.get("hora_inicio"))
        hora_fin = _parse_time(event.get("hora_fin"))

        if not any([fecha_inicio, fecha_fin, hora_inicio, hora_fin]):
            return

        self.db.add(
            Programacion(
                experiencia_id=experiencia.id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
            )
        )

    def _write_ubicacion(self, experiencia: Experiencia, event: dict):
        pais_name = resolve_country(event.get("pais"))
        ciudad_name = event.get("ciudad")

        pais = self.pais_lookup.get(normalize_key(pais_name)) if pais_name else None
        ciudad = self.ciudad_lookup.get(normalize_key(ciudad_name)) if ciudad_name else None

        if pais is None or ciudad is None:
            return

        distrito = resolve_district(
            event.get("distrito"), event.get("direccion"), self.district_lookup
        )
        distrito_row = self.district_rows.get(normalize_key(distrito)) if distrito else None

        self.db.add(
            Ubicacion(
                pais_id=pais.id,
                ciudad_id=ciudad.id,
                distrito_id=distrito_row.id if distrito_row else None,
                direccion=event.get("direccion"),
                latitud=clean_number(event.get("latitud")),
                longitud=clean_number(event.get("longitud")),
                experiencia_id=experiencia.id,
            )
        )

    # ------------------------------------------------------------
    # Tag lookup is maintained separately because Tag has its own table
    # and its normalized name is stored directly.
    # ------------------------------------------------------------
    def _tag_lookup(self) -> dict:
        if not hasattr(self, "tag_lookup"):
            self.tag_lookup = self._build_lookup(select(Tag))
        return self.tag_lookup
