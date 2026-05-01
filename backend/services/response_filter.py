"""
LLM wrapper for response filter.

"""

#Standard module
import json

from rag.llm.prompt_templates import build_recommendation_query

class ResponseFilterService:

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def json_response(self,context:str,query:str):
        llm = self.llm_client
        prompt = build_recommendation_query(context,query)
        response = llm.invoke(prompt)

        print("RAW LLM RESPONSE:", response)
        print("TYPE:", type(response))

        if not response:
            return []

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("Invalid JSON from LLM:")
            print(response)
            return []
