"""
Database operations for Corpusmaker
"""

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.engine import Engine
from corpusmaker.model import RawText


@dataclass
class Database:
    engine: Engine = create_engine("sqlite:///database.db", echo=True)

    def __post_init__(self) -> None:
        print("Poop")
