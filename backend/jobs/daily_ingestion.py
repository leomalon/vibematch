"""
daily_ingestion.py

Daily job:

1. (Optional) scrapes Joinnus and EntradaLibre into their raw event files.
2. Loads the event sets (Joinnus + EntradaLibre + curated points).
3. Enriches events with semantic metadata (moods, tags, publico) via LLM.
4. Persists the combined set to a single JSON file (semantic_experiences.json).
5. Writes every event into PostgreSQL.

Run offline by leaving RUN_SCRAPING=False: it uses the already scraped files.
"""
#Standard modules
from pathlib import Path
import os

#Services
from backend.services.ingestion_service import IngestionService

#DB
from backend.db.session import SessionLocal
from backend.repositories.catalog_repository import CatalogRepository

#Sources
from backend.ingestion.sources.joinnus_scraper import JoinnusScraper
from backend.ingestion.sources.entradalibre_scraper import EntradaLibreScraper

#LLMs
from backend.llm.ollama_client import ChatOllama

#Processors
from backend.ingestion.processors.semantic_enrichment import SemanticEnrichmentProcessor

#Writers / storage
from backend.ingestion.storage.postgres_writer import PostgresWriter
from backend.ingestion.raw.json_storage import JsonStorage

#Pipelines
from backend.ingestion.pipelines.postgres_pipeline import PostgresPipeline


# ==========================================
# 1. CONFIG PATHS
# ==========================================

# backend/ (daily_ingestion.py lives at backend/jobs/)
BASE_DIR = Path(__file__).resolve().parent.parent

#Web page entries
web_config_path = BASE_DIR / "config" / "sites.json"

#Categories
joinnus_categories_path = BASE_DIR / "config" / "joinnus_categories.json"
entradalibre_categories_path = BASE_DIR / "config" / "entradalibre_categories.json"

#Raw data paths
joinnus_raw_path = BASE_DIR / "data" / "raw" / "joinnus_raw.json"
entradalibre_raw_path = BASE_DIR / "data" / "raw" / "entradalibre_raw.json"

#Raw events data paths
joinnus_events_raw_path = BASE_DIR / "data" / "raw" / "joinnus_events_raw.json"
entradalibre_events_raw_path = BASE_DIR / "data" / "raw" / "entradalibre_events_raw.json"

#Curated points (restaurants, bars, etc.) - already semantically enriched
points_path = BASE_DIR / "data" / "processed" / "point_experiences.json"

#Single combined semantic file
semantic_events_path = BASE_DIR / "data" / "processed" / "semantic_experiences.json"

#Scraping requires network + Playwright; keep False to work offline.
RUN_SCRAPING = False


# ==========================================
# 2. MAIN EXECUTION
# ==========================================

def _scrape_sources(json_storage: JsonStorage):
    service = IngestionService()

    sites = json_storage.load(web_config_path)[0]

    #---JOINNUS---
    joinnus_categories = json_storage.load(joinnus_categories_path)
    joinnus_scraper = JoinnusScraper(
        origin=sites["joinnus"]["origin"],
        categories=joinnus_categories,
        id_tag=sites["joinnus"]["id_tag_data"],
        static_tag=sites["joinnus"]["static_tag_data"],
    )
    service.ingest(
        source=joinnus_scraper,
        raw_storage=json_storage,
        raw_data_path=joinnus_raw_path,
        events_data_path=joinnus_events_raw_path,
    )

    #---ENTRADALIBRE---
    entradalibre_categories = json_storage.load(entradalibre_categories_path)
    entradalibre_scraper = EntradaLibreScraper(
        origin=sites["entradalibre"]["origin"],
        web_parameters=sites["entradalibre"],
        web_categories=entradalibre_categories,
    )
    service.ingest(
        source=entradalibre_scraper,
        raw_storage=json_storage,
        raw_data_path=entradalibre_raw_path,
        events_data_path=entradalibre_events_raw_path,
    )


def main():
    json_storage = JsonStorage()

    # Optional scraping (network + Playwright).
    if RUN_SCRAPING:
        _scrape_sources(json_storage)

    db = SessionLocal()
    try:
        catalog_repo = CatalogRepository(db)

        moods = [mood["nombre"] for mood in catalog_repo.get_all_moods()]
        companias = [compania["nombre"] for compania in catalog_repo.get_all_companions()]

        # LLM enrichment (requires OLLAMA_API_KEY).
        llm_enrichment = ChatOllama(os.environ.get("OLLAMA_API_KEY"))

        pipeline = PostgresPipeline(
            processors=[SemanticEnrichmentProcessor(llm_enrichment, moods, companias)],
            processed_storage=json_storage,
            writer=PostgresWriter(db),
            semantic_events_path=semantic_events_path,
        )

        joinnus_events = json_storage.load(joinnus_events_raw_path)
        entradalibre_events = json_storage.load(entradalibre_events_raw_path)
        points = json_storage.load(points_path)

        all_events = joinnus_events + entradalibre_events + points

        print(f"[daily_ingestion] {len(joinnus_events)} joinnus, "
              f"{len(entradalibre_events)} entradalibre, {len(points)} points")

        pipeline.run(all_events)

    finally:
        db.close()


if __name__ == "__main__":
    main()
