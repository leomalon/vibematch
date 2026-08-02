"""
postgres_pipeline.py

Adds semantic moods to the events, stores the events in json and 
write the events to the database.

Pipeline orchestrates a technical processing workflow (implementation workflow)

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

        print(events)