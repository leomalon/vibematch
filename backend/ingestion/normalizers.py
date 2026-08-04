"""
normalizers.py

Text and catalog normalization helpers used during ingestion.

The scraped events come from different sources with inconsistent casing,
accents and formats (e.g. "PE" vs "Perú", "lima" vs "Lima", empty districts).
These helpers bring everything to a common, comparable shape before writing
to the database or matching against the catalog tables.
"""

#Standard modules
import unicodedata
import re


# ==========================================
# 1. TEXT NORMALIZATION
# ==========================================

def normalize_key(value: str | None) -> str:
    """
    Lowercase, strip accents and collapse whitespace.

    Examples:
        "cafetería" -> "cafeteria"
        "  San   Isidro " -> "san isidro"
        "Perú" -> "peru"
    """
    if not value:
        return ""

    text = unicodedata.normalize("NFD", str(value))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def to_slug(value: str | None) -> str:
    """
    Normalize and replace whitespace with hyphens (URL-friendly).

    Mirrors the frontend `toSlug` so category slugs match on both sides.

    Examples:
        "Arte-cultura" -> "arte-cultura"
        "Cafetería" -> "cafeteria"
        "Viaje-aventura" -> "viaje-aventura"
    """
    return normalize_key(value).replace(" ", "-")


# ==========================================
# 2. COUNTRY / DISTRICT RESOLUTION
# ==========================================

PERU_ALIASES = {"pe", "peru", "per"}


def resolve_country(value: str | None) -> str | None:
    """Map any Peru variant ("PE", "Peru", "Perú") to the canonical 'Perú'."""
    if not value:
        return None

    if normalize_key(value) in PERU_ALIASES:
        return "Perú"

    return str(value).strip()


def resolve_district(district_hint: str | None, address: str | None, lookup: dict) -> str | None:
    """
    Resolve a district from the explicit hint, falling back to scanning the
    address string for a known district name.

    Args:
        district_hint: The `distrito` field of the event (often empty).
        address: The full `direccion` string (often contains the district).
        lookup: dict mapping normalized district names to canonical names,
            e.g. {"miraflores": "Miraflores"}.

    Returns:
        The canonical district name, or None if it cannot be resolved.
    """
    if district_hint:
        key = normalize_key(district_hint)
        if key in lookup:
            return lookup[key]

    if address:
        norm_address = normalize_key(address)
        for key, canonical in lookup.items():
            if key and key in norm_address:
                return canonical

    return None


# ==========================================
# 3. NUMERIC HELPERS
# ==========================================

def clean_number(value) -> float | None:
    """Coerce a scraped price to float, tolerating None and bad strings."""
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None
