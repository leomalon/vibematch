"""
main.py

Initializes FastAPI app and registers routes

"""

#Standard modules 
import os

#Local modules
from backend.routes import events

#Third-party libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
environment = os.getenv("ENVIRONMENT")
next_url = os.getenv("NEXT_PUBLIC_URL")

allow_origins = ["*" if environment=="DEV" else next_url]

#FastAPI configuration
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/events")