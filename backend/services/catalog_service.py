"""
catalog_service.py

Catalog query and resolver layer

"""

#Schemas
from backend.schemas.catalogs import Catalogs, CatalogIds

class CatalogService:

    def __init__(self,catalog_repository):

        self.catalog_repository = catalog_repository

    def get_catalogs(self):

        return Catalogs(

            moods=self.catalog_repository.get_all_moods(),

            categorias=self.catalog_repository.get_all_categories(),

            distritos=self.catalog_repository.get_all_districts(),

            pais=self.catalog_repository.get_all_countries(),

            ciudad=self.catalog_repository.get_all_cities(),

            tipo_experiencia=self.catalog_repository.get_all_types(),

            compania=self.catalog_repository.get_all_companions()

        )
    