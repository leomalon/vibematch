"""
API Schema for requests.

"""

from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str