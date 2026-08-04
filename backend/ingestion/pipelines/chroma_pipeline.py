"""
chroma_pipeline.py

Adds semantic moods to the events, converts the events into embeddings
and stores them in a vector database.

Pipeline orchestrates a technical processing workflow (implementation workflow)

"""

# ==========================================
# 1. PIPELINE
# ==========================================

def format_event_for_embedding(event: dict) -> str:
    return f"""

    Moods: {", ".join(event['mood'])}
    Moods: {", ".join(event['mood'])}

    Tags clave: {", ".join([tag.replace("#", "") for tag in event['tags']])}

    Público objetivo:
    {event["publico"]}

    Descripción corta:
    {event['descripcion']}

    Categoría: {event['categoria_espaniol']}

    Ubicación: {event["ciudad"]}

    """


class ChromaPipeline:

    def __init__(
        self,
        processors: list,
        processed_storage,
        writer,
        semantic_events_path,
        collection_name:str
    ):
        self.processors = processors
        self.processed_storage = processed_storage
        self.semantic_events_path = semantic_events_path
        self.collection_name = collection_name
        self.writer = writer

    def run(self, events):

        for processor in self.processors:
            events = processor.process(events)

        # Save enriched events
        self.processed_storage.save(self.semantic_events_path,events)

        formatted_events = [format_event_for_embedding(event) for event in events]

        event_metadatas = []

        for event in events:
            metadata = {
                "titulo": event.get("titulo"),
                "descripcion": event.get("descripcion"),
                "url": event.get("url_evento"),
                "direccion": event.get("direccion"),
                "categoria": event.get("categoria_espaniol"),
                "precio": event.get("precio"),
                "moneda": event.get("moneda"),
            }

            tags = event.get("tags")

            # Only add tags if valid and non-empty
            if isinstance(tags, list) and len(tags) > 0:
                metadata["tags"] = tags

            event_metadatas.append(metadata)


        self.writer.save(self.collection_name,formatted_events,event_metadatas)
