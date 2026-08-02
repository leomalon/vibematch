from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.db.models.models import Mood,Categoria,Compania,Tipo,Distrito,Ciudad,Pais


class CatalogRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all_moods(self):

        return (
            self.db.execute(
                select(Mood.id,Mood.nombre)
            )
            .mappings()
            .all()
        )

    def get_all_categories(self):
        return (
            self.db.execute(
                select(Categoria.id,Categoria.nombre)
            )
            .mappings()
            .all()
        )

    def get_all_types(self):
        return (
            self.db.execute(
                select(Tipo.id,Tipo.nombre)
            )
            .mappings()
            .all()
        )

    def get_all_companions(self):
        return (
            self.db.execute(
                select(Compania.id,Compania.nombre)
            )
            .mappings()
            .all()
        )

    def get_all_districts(self):
        return (
            self.db.execute(
                select(Distrito.id,Distrito.nombre)
            )
            .mappings()
            .all()
        )

    def get_all_cities(self):
        return (
            self.db.execute(
                select(Ciudad.id,Ciudad.nombre)
            )
            .mappings()
            .all()
        )

    def get_all_countries(self):
        return (
            self.db.execute(
                select(Pais.id,Pais.nombre)
            )
            .mappings()
            .all()
        )