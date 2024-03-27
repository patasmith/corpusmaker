"""
Textfile operations for Corpusmaker
"""

from typing import Optional

from dataclasses import dataclass
from sqlmodel import Session
from corpusmaker.database import Database
from corpusmaker.model import RawText
from loguru import logger


@dataclass
class Loader:
    db: Database

    def read_file(self, filename: str, separator: str = "") -> Optional[RawText]:
        try:
            with open(filename, "r") as f:
                content = f.read()
                return RawText(content=content, separator=separator)
        except FileNotFoundError:
            logger.error(f"{filename} was not found.")
        except UnicodeDecodeError:
            logger.error(f"{filename} is not readable as text.")
        except Exception as e:
            logger.error(e)
        return None

    def import_file(self, filename: str, separator: str = "") -> None:
        raw_text = self.read_file(filename, separator)
        if raw_text:
            session = Session(self.db.engine)
            self.db.create_raw_text(session, raw_text)

    def import_files(self, filenames: list[str], separator: str = "") -> None:
        for filename in filenames:
            self.import_file(filename, separator)
