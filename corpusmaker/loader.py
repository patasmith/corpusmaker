"""
Textfile operations for Corpusmaker
"""

from dataclasses import dataclass
from corpusmaker.database import Database
from corpusmaker.model import RawText
from loguru import logger


@dataclass
class Loader:
    db: Database

    def read_file(self, filename: str, separator: str = "") -> None:
        try:
            with open(filename, "r") as f:
                contents = f.read()
        except FileNotFoundError:
            logger.error(f"{filename} was not found.")
        except Exception as e:
            logger.error(e)
