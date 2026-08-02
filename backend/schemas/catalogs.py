"""
catalogs.py

Schemas of responses and requests of catalogs.

"""

from pydantic import BaseModel

class CatalogItem(BaseModel):
    id: int
    nombre: str

class Catalogs(BaseModel):

    moods: list[CatalogItem]

    categorias: list[CatalogItem]

    distritos: list[CatalogItem]

    ciudad: list[CatalogItem]

    pais: list[CatalogItem]

    tipo_experiencia: list[CatalogItem]

    compania: list[CatalogItem]

class CatalogIds(BaseModel):

    pais_id: int| None

    ciudad_id:int| None

    distrito_id:int| None

    tipo_experiencia_id : int| None

    categoria_id : list[int|None]

    moods_id : list[int|None]

    compania_id: list[int|None]