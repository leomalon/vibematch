"""
postgres_pipeline.py

Orchestrates the Postgres ingestion workflow:

1. Enrich events with semantic metadata (moods, tags, publico).
2. Persist the full set to a single JSON file (semantic_experiences.json).
3. Write every event to the PostgreSQL database.

The pipeline receives ALL events (Joinnus + EntradaLibre + curated points);
the semantic processor skips events that are already enriched.
"""

# ==========================================
# 1. PIPELINE
# ==========================================


class PostgresPipeline:

    def __init__(
        self,
        processors: list,
        processed_storage,
        writer,
        semantic_events_path
    ):
        self.processors = processors
        self.processed_storage = processed_storage
        self.semantic_events_path = semantic_events_path
        self.writer = writer

    def run(self, events):

        for processor in self.processors:
            events = processor.process(events)

        # Persist the combined, enriched set to the single semantic file.
        self.processed_storage.save(
            self.semantic_events_path,
            events,
            overwrite=True,
        )

        # Write each event into PostgreSQL.
        self.writer.save(events)
