"""
LLM wrapper for returning a structured query.

"""

#Local Dependencies
from backend.llm.promp_templates import build_prompt_json_filters

class QueryUnderstanding:
    def __init__(self,llm_client):
        self.llm_client = llm_client
    
    def parse(self, query: str,catalogs:dict,date,time) -> dict:

        prompt = build_prompt_json_filters(query,catalogs,date,time)

        structured_json = self.llm_client.invoke(prompt)

        return structured_json