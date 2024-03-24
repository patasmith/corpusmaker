"""
Textfile operations for Corpusmaker
"""

from dataclasses import dataclass
from corpusmaker.model import RawText
from loguru import logger


@dataclass
class Loader:
    filename: str
    separator: str = ""

    def read_file(self) -> None:
        try:
            with open(self.filename, "r") as f:
                contents = f.read()
        except FileNotFoundError:
            logger.error(f"{self.filename} was not found.")
        except Exception as e:
            logger.error(e)
