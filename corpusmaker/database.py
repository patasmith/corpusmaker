"""
Database operations for Corpusmaker
"""

from typing import Optional
from dataclasses import dataclass
from hashlib import md5
from itertools import islice
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.engine import Engine
from corpusmaker.model import RawText, Scene
from loguru import logger


@dataclass
class Database:
    pathname: str = "sqlite:///data/database.sqlite3"

    def __post_init__(self) -> None:
        self.engine: Engine = create_engine(self.pathname, echo=True)
        SQLModel.metadata.create_all(self.engine)

    def create_raw_text(self, session: Session, raw_text: RawText) -> None:
        """
        Enter raw text in the database
        """
        logger.info("Entering raw text in database")
        raw_text.checksum = md5(raw_text.content.encode("utf-8")).hexdigest()
        statement = select(RawText).where(RawText.checksum == raw_text.checksum)
        results = session.exec(statement)
        duplicate = results.first()

        if not duplicate:
            session.add(raw_text)
            session.commit()
            logger.info("Raw text added to database")
        else:
            logger.error("Duplicate found, not adding")
            raise Exception("Duplicate found, not adding")

    def read_raw_text(self, session: Session, text_id: int) -> RawText:
        logger.info(f"Reading Text {text_id} from database")
        statement = select(RawText).where(RawText.id == text_id)
        result: Optional[RawText] = session.exec(statement).first()
        if result:
            return result
        else:
            logger.error("Raw text not found")
            raise Exception(f"Text {text_id} not found in database")

    def update_raw_text_separator(
        self, session: Session, text_id: int, separator: str
    ) -> None:
        logger.info(f"Updating Text {text_id} in database")
        statement = select(RawText).where(RawText.id == text_id)
        result = session.exec(statement).first()
        if result:
            result.separator = separator
            session.add(result)
            session.commit()
            logger.info(f"Updated Text {text_id} in database")
        else:
            logger.error(f"Text {text_id} not found in database")
            raise Exception(f"Text {text_id} not found")

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

    def convert_raw_text_without_separator_to_scenes(
        self, session: Session, content: str, word_limit: int = 100
    ) -> list[Scene]:
        """
        Split content of raw text into scenes

        Algorithm:
        - Split content by newline
        - For each line of content:
          - If it is under the word limit:
            - Add as many next lines as we can
            - Stop before it's over the limit
          - If it is over the word limit:
            - Split the line in half at each word
            - Keep doing that until the lines are under the limit
        - Convert each resulting line to a Scene

        Drawback:
        - Paragraphs longer than the word limit will be split by word, not sentence.

        """
        # Split raw text content on line breaks, remove blank lines
        raw_text_words_by_line = [
            line.split(" ") for line in content.split("\n") if line.strip()
        ]

        scene_lines = []
        previous_words = []
        for index, current_words in enumerate(raw_text_words_by_line):
            # If there was a previous line to add to this one, add it
            words = list(previous_words)
            words.extend(current_words)
            # Reset the previous line now that it's been added
            previous_words = []

            chunk_length = len(words)
            next_index = index + 1

            # If current line is below word limit, check if we can add
            # the next line to it without going over the limit. If we can,
            # skip this iteration and do that at the beginning of the next one
            if chunk_length < word_limit:
                if next_index < len(raw_text_words_by_line):
                    if (
                        chunk_length + len(raw_text_words_by_line[next_index])
                        < word_limit
                    ):
                        previous_words.extend(words)
                        continue

            # If current line is above word limit, define how we're going to
            # split it down to fit: halve the target length until it's below the limit.
            while chunk_length > word_limit:
                chunk_length = int(chunk_length / 2)

            # Split our current line down into sublists (chunks) as necessary
            chunks = [
                words[i : i + chunk_length] for i in range(0, len(words), chunk_length)
            ]

            # Each sublist of words becomes a string, and is added to the list
            # of strings to be turned into Scenes
            scene_lines.extend([" ".join(chunk) for chunk in chunks])

        return scene_lines

    def convert_raw_text_to_scenes(
        self, session: Session, text_id: int, word_limit: int = 100
    ) -> list[Scene]:
        raw_text = self.read_raw_text(session, text_id)
        content = []
        if raw_text.separator:
            content.extend(["separator"])
        else:
            content.extend(self.convert_raw_text_without_separator_to_scenes(
                session, raw_text.content, word_limit
            ))
        return [
            Scene(
                content=text,
                text_id=text_id,
                checksum=md5(text.encode("utf-8")).hexdigest(),
            )
            for text in content
        ]

    def create_scenes(self, session: Session, text_id: int) -> None:
        logger.info(f"Converting Text {text_id} into scenes")
        scenes = self.convert_raw_text_to_scenes(session, text_id)
        for scene in scenes:
            statement = select(Scene).where(Scene.checksum == scene.checksum)
            results = session.exec(statement)
            duplicate = results.first()

            if not duplicate:
                session.add(scene)
                session.commit()
                logger.info("Scene added to database")
            else:
                logger.error("Duplicate found, not adding")
                raise Exception("Duplicate found, not adding")

    def read_scene(self, session: Session, scene_id: int) -> Scene:
        logger.info(f"Reading Scene {scene_id} from database")
        statement = select(Scene).where(Scene.id == scene_id)
        result: Optional[Scene] = session.exec(statement).first()
        if result:
            return result
        else:
            logger.error("Scene not found")
            raise Exception(f"Scene {scene_id} not found in database")
