"""
ingestion_service.py

IngestionService orchestrates the business use case.

"""


class IngestionService:

    def ingest(self, source, raw_storage, raw_data_path, events_data_path):

        full_events = source.scrape_webpage()
        raw_storage.save(raw_data_path, full_events)

        full_events = raw_storage.load(raw_data_path)

        events = source.scrape_events(full_events)

        # scrape_events regenerates the full set from the raw data: overwrite.
        raw_storage.save(events_data_path, events, overwrite=True)

        return events

