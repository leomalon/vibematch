"""
LLM wrapper for returning a structured query.

"""
#Standard modules
import os

#Local modules
from rag.llm.prompt_templates import build_query

#Third-party modules
from dotenv import load_dotenv

load_dotenv()
raw_moods = os.getenv("MOODS","")
ALLOWED_MOODS = [m.strip() for m in raw_moods.split(",") if m.strip()]

class QueryUnderstandingService:
    def __init__(self,llm_client):
        self.llm_client = llm_client
    
    def parse(self, query: str) -> dict:
        # call LLM
        llm = self.llm_client

        prompt = build_query(query,ALLOWED_MOODS)

        structured_query = llm.invoke(prompt)

        return structured_query