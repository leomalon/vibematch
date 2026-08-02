"""
daily_ingestion.py

"""
#Standard modules
from pathlib import Path
import os

#Services
from backend.services.ingestion_service import IngestionService
from backend.ingestion.embeddings.embeddings_service import get_openai_embedding

#Repositories
from backend.db.session import SessionLocal
from backend.repositories.catalog_repository import CatalogRepository

#Sources
from backend.ingestion.sources.joinnus_scraper import JoinnusScraper
from backend.ingestion.sources.entradalibre_scraper import EntradaLibreScraper

#LLMs
from backend.llm.ollama_client import ChatOllama

#Processors
from backend.ingestion.processors.semantic_enrichment import SemanticEnrichmentProcessor

#Writers
from backend.ingestion.storage.postgres_writer import PostgresWriter
from backend.ingestion.storage.chroma_repository import ChromaVectorStore
from backend.ingestion.raw.json_storage import JsonStorage

#Pipelines
from backend.ingestion.pipelines.postgres_pipeline import PostgresPipeline
from backend.ingestion.pipelines.chroma_pipeline import ChromaPipeline


# ==========================================
# 1. CONFIG PATHS
# ==========================================

# Always resolve from root
BASE_DIR = Path(__file__).resolve().parent.parent

#Web page entries
web_config_path = BASE_DIR / "config" / "sites.json"

#Categories
joinnus_categories = BASE_DIR / "config" / "joinnus_categories.json"
entradalibre_categories = BASE_DIR / "config" / "entradalibre_categories.json"

#Raw data paths
joinnus_raw_path = BASE_DIR/"data"/"raw"/"joinnus_raw.json"
entradalibre_raw_path = BASE_DIR/"data"/"raw"/"entradalibre_raw.json"

#Raw events data paths
joinnus_events_raw_path = BASE_DIR/"data"/"raw"/"joinnus_events_raw.json"
entradalibre_events_raw_path = BASE_DIR/"data"/"raw"/"entradalibre_events_raw.json"

#Semantic events data paths
events_with_moods_path = BASE_DIR / "data" / "processed" / "events_with_moods.json"
ig_places_path = BASE_DIR/"data"/"processed"/"ig_places.json"

#Vector DB path
# persistent_db_path = BASE_DIR / "data" / "chroma_db"
persistent_db_path = "C:/chroma_db"

# ==========================================
# 2. SCRAPING VARIABLES
# ==========================================

json_storage = JsonStorage()

# Web pages
sites = json_storage.load(web_config_path)[0]

#Joinnus
joinnus_origin = sites["joinnus"]["origin"]
joinnus_categories = json_storage.load(joinnus_categories)
joinnus_tag_data = sites["joinnus"]["id_tag_data"]
joinnus_static_data = sites["joinnus"]["static_tag_data"]

#EntradaLibre
entradalibre_origin = sites["entradalibre"]["origin"]
entradalibre_parameters = sites["entradalibre"]
entradalibre_categories = json_storage.load(entradalibre_categories)
print(entradalibre_parameters)

# ==========================================
# 2. DEPENDENCIES
# ==========================================

#---LLMS---
llm_enrichment = ChatOllama(os.environ.get("OLLAMA_API_KEY"))

#---MOODS EXTRACTION---
db = SessionLocal()
try:
    catalog_repo = CatalogRepository(db)

    moods = catalog_repo.get_all_moods()

    moods = [mood["nombre"] for mood in moods]

finally:
    db.close()

#---SCRAPERS---
joinnus_scraper = JoinnusScraper(origin=joinnus_origin,categories=joinnus_categories,
                                 id_tag=joinnus_tag_data,static_tag=joinnus_static_data)

entradalibre_scraper = EntradaLibreScraper(origin=joinnus_origin,web_parameters = entradalibre_parameters,web_categories=entradalibre_categories)

# entradalibre_scraper = EntradaLibreScraper()


#---PIPELINES---
postgres_pipeline = PostgresPipeline(
            processors = [SemanticEnrichmentProcessor(llm_enrichment,moods)],
            processed_storage=json_storage,
            writer=PostgresWriter(),
            semantic_events_path = events_with_moods_path
        )

# chroma_pipeline = ChromaPipeline(
#     processors=[SemanticEnrichmentProcessor(llm_enrichment,moods)],
#     processed_storage=json_storage,
#     writer = ChromaVectorStore(persistent_db_path,get_openai_embedding("text-embedding-3-large")),
#     semantic_events_path=events_with_moods_path,
#     collection_name="vibematch_collection"
# )


# ==========================================
# 3. MAIN EXECUTION
# ==========================================

def main():
    service = IngestionService()

    # service.ingest(
    #     source=joinnus_scraper,
    #     raw_storage=json_storage,
    #     raw_data_path=joinnus_raw_path,
    #     events_data_path=joinnus_events_raw_path,
    #     pipeline=postgres_pipeline
    # )
    service.ingest(
        source=entradalibre_scraper,
        raw_storage=json_storage,
        raw_data_path=entradalibre_raw_path,
        events_data_path=entradalibre_events_raw_path,
        pipeline=postgres_pipeline
    )

if __name__ == "__main__":

    main()
