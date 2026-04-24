"""
main.py

Initializes FastAPI app and registers routes

"""

from fastapi import FastAPI
from backend.routes import events
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vibeematch.xyz"],  # for dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/events")