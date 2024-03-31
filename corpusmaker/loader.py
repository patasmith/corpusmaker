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

    def read_file(
        self, filename: str, separator: str = "", use_regex: bool = False
    ) -> Optional[RawText]:
        try:
            with open(filename, "r") as f:
                content = f.read()
                return RawText(
                    content=content, separator=separator, use_regex=use_regex
                )
        except FileNotFoundError:
            logger.error(f"{filename} was not found.")
        except UnicodeDecodeError:
            logger.error(f"{filename} is not readable as text.")
        except Exception as e:
            logger.error(e)
        return None

    def import_file(
        self, filename: str, separator: str = "", use_regex: bool = False
    ) -> None:
        raw_text = self.read_file(filename, separator, use_regex)
        if raw_text:
            session = Session(self.db.engine)
            self.db.create_raw_text(session, raw_text)
            logger.info(f"Loaded {filename}")

    def import_files(
        self, filenames: list[str], separator: str = "", use_regex: bool = False
    ) -> None:
        regex = (use_regex and "regex") or ""
        logger.info(f"Reading files with {regex} separator: {separator}")
        for filename in filenames:
            self.import_file(filename, separator, use_regex)
