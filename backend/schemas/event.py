"""
API Schema for query and response.

"""

from pydantic import BaseModel

class EventResponse(BaseModel):
    titulo: str
    descripcion:str
    url: str
    direccion:str
    categoria: str
    precio: float | None
    moneda: str


class QueryRequest(BaseModel):
    query: str