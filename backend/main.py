"""
main.py

Initializes FastAPI app and registers routes

"""

from fastapi import FastAPI
from routes import events

app = FastAPI()

app.include_router(events.router, prefix="/events")