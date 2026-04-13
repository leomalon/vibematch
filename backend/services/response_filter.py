"""
LLM wrapper for response filter.

"""

#Standard module
import json

from rag.llm.ollama import ChatOllama
from rag.llm.prompt_templates import build_recommendation_query

class ResponseFilterService:

    def __init__(self, api_key):
        self.api_key= api_key

    def json_response(self,context:str,query:str):
        llm = ChatOllama(self.api_key)
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
