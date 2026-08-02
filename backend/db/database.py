"""
Database engine configuration.
"""

#Standard modules
import os

#Third-party modules
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, #if PostgreSQL closes a conection, SQLAlchemy detects it and opens a new one.
    echo=False, #Does not print SQL.
    connect_args={"client_encoding": "UTF8"}
)
