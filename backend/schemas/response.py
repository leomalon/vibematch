"""
API Schema for query and response.

"""

from pydantic import BaseModel

class SearchResponse(BaseModel):
    titulo: str
    descripcion:str
    url: str
    direccion:str
    categoria: str
    precio: float | None
    moneda: str
    mood: list[str] = []
    fecha_inicio: str | None = None
    hora_inicio: str | None = None
    latitud: float | None = None
    longitud: float | None = None
