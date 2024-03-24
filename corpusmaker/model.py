"""
Model for storing text
"""

from typing import Optional

from hashlib import md5
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone


class RawText(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, primary_key=True, description="The ID of the raw text"
    )
    content: str = Field(description="The content of the raw text")
    checksum: str = Field(description="The checksum of the raw text")
    separator: Optional[str] = Field(
        description="The separator that delineates sections of the raw text"
    )
    created_at: datetime = Field(
        default=datetime.now(timezone.utc),
        nullable=False,
        description="The timestamp of when the raw text was added",
    )
