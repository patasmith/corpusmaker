"""
Database operations for Corpusmaker
"""

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.engine import Engine
from corpusmaker.model import RawText
from loguru import logger


@dataclass
class Database:
    engine: Engine = create_engine("sqlite:///database.db", echo=True)

    def __post_init__(self) -> None:
        SQLModel.metadata.create_all(self.engine)

    def create_raw_text(self, session: Session, raw_text: RawText) -> None:
        """
        Enter raw text in the database
        """
        logger.info("Entering raw text in database")
        session.add(raw_text)
        session.commit()

    def delete_raw_text(self, session: Session, text_id: int) -> None:
        """
        Delete a raw text entry from the database
        """
        logger.info("Deleting raw text from the database")
        statement = select(RawText).where(RawText.id == text_id)
        results = session.exec(statement)
        raw_text = results.first()

        if raw_text:
            session.delete(raw_text)
            session.commit()

            results_post_delete = session.exec(statement)
            raw_text_post_delete = results_post_delete.first()

            if raw_text_post_delete is None:
                logger.info(f"Text {text_id} has been deleted")
            else:
                logger.error(f"Text {text_id} was not successfully deleted")
        else:
            logger.error(f"Text {text_id} not found")
            raise Exception(f"Text {text_id} not found")

    def delete_all_raw_text(self, session: Session) -> None:
        """
        Delete all raw text entries from the database
        """
        logger.info("Deleting all raw text from the database")
        statement = select(RawText)
        results = session.exec(statement)

        for raw_text in results:
            session.delete(raw_text)
            session.commit()

        results_post_delete = session.exec(statement)
        raw_text_post_delete = results_post_delete.all()

        if raw_text_post_delete == []:
            logger.info("All raw text has been deleted")
        else:
            logger.error("Deletion of all raw text failed")
            raise Exception("Deletion of all raw text failed")
