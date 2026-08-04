"""
semantic_enrichment.py

Adds semantic metadata (moods, tags, publico) to each scraped event using an
LLM. Events that already carry a `mood` list (e.g. curated points) are left
untouched.
"""
#Standard modules
import json

#Prompt builders
from backend.llm.promp_templates import build_event_classification


class SemanticEnrichmentProcessor:

    def __init__(self, llm_instance, moods, companias=None):
        self.llm_instance = llm_instance
        self.moods = moods
        self.companias = companias or []

    def process(self, events: list):
        enriched = []

        for event in events:

            # Curated events (points) already have semantic data: keep as-is.
            if event.get("mood"):
                enriched.append(event)
                continue

            prompt = build_event_classification(event, self.moods, self.companias)

            response = self.llm_instance.invoke(prompt)

            # Defaults applied if the LLM output is missing or malformed.
            emociones = []
            resumen = event.get("descripcion", "")
            publico = []
            tags = list(event.get("tags") or [])

            try:
                data = json.loads(response)

                # Keep only moods that belong to the allowed list.
                emociones = list(
                    dict.fromkeys(
                        m for m in data.get("emociones", []) if m in self.moods
                    )
                )[:4]
                print(emociones)

                resumen = data.get("resumen") or resumen
                publico = list(
                    dict.fromkeys(
                        p for p in data.get("publico", []) if p in self.companias
                    )
                )
                tags = list(data.get("tags") or tags)

            except (json.JSONDecodeError, TypeError):
                print("[SemanticEnrichment] respuesta LLM inválida, se usa default")

            event["mood"] = emociones
            event["descripcion"] = resumen
            event["publico"] = publico
            event["tags"] = tags
            enriched.append(event)
            print(enriched)

        return enriched
