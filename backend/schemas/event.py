"""
API Schema for query and response.

"""

from pydantic import BaseModel

class EventResponse(BaseModel):
    titulo: str
    descripcion: str
    categoria: str
    precio: float | None
    moneda: str
    url: str


class QueryRequest(BaseModel):
    query: str