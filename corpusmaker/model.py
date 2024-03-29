"""
Model for storing text
"""

from typing import Optional

from sqlmodel import Field, SQLModel
from datetime import datetime, timezone


class RawText(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, primary_key=True, description="The ID of the raw text"
    )
    content: str = Field(description="The content of the raw text")
    checksum: str = Field(description="The checksum of the raw text")
    separator: str = Field(
        default="", description="The separator that delineates sections of the raw text"
    )
    use_regex: bool = Field(
        default=False,
        description="Determines whether the separator is to interpreted as regex or not",
    )
    created_at: datetime = Field(
        default=datetime.now(timezone.utc),
        nullable=False,
        description="The timestamp of when the raw text was added",
    )


class Scene(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None, primary_key=True, description="The ID of the scene"
    )
    content: str = Field(description="The content of the scene")
    checksum: str = Field(description="The checksum of the scene")
    text_id: int = Field(foreign_key="rawtext.id", description="The parent raw text")
    created_at: datetime = Field(
        default=datetime.now(timezone.utc),
        nullable=False,
        description="The timestamp of when the scene was added",
    )
