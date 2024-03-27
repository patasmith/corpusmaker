"""
Textfile operations for Corpusmaker
"""

from typing import Optional

from dataclasses import dataclass
from corpusmaker.model import RawText
from loguru import logger


@dataclass
class Loader:
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
