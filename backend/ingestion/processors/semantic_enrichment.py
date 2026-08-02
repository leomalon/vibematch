"""
semantic_enrichment.py

"""
#Standard modules
import json

#Prompt builders
from backend.llm.promp_templates import build_event_classification

class SemanticEnrichmentProcessor:

    def __init__(self,llm_instance,moods):
        self.llm_instance = llm_instance
        self.moods = moods

    def process(self, events:list):
        enriched = []

        for event in events:

            moneda = event["moneda"]
            precio = event["precio"]

            #Clean description
            event["descripcion"] = event["descripcion"]

            #Add price range description
            # event["precio_rango"] = define_event_price_range(moneda,precio)

            prompt= build_event_classification(event,self.moods)
            
            response = self.llm_instance.invoke(prompt)


            try:
                moods_response = json.loads(response)

                emociones = moods_response.get("emociones", [])
                descripcion_resumen = moods_response.get("resumen", [])
                publico = moods_response.get("publico", [])

                #Clean moods in case adds a mood that is not allowed
                emociones = list(set([m for m in emociones if m in self.moods]))[:4]
                print(emociones)

            except:
                emociones = []

            event["mood"] = emociones
            event["descripcion"] = descripcion_resumen
            event["público"] = publico
            enriched.append(event)

        return enriched
        