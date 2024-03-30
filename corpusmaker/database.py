"""
Database operations for Corpusmaker
"""

from typing import Optional
from dataclasses import dataclass
from hashlib import md5
import re
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

    def convert_raw_text_to_scenes(
        self, session: Session, text_id: int, word_limit: int
    ) -> list[Scene]:
        """
        Split content of raw text into scenes

        Algorithm:
        - Split content by separator (newline by default)
        - For each section of content:
          - If it is under the word limit:
            - Add as many next sections as we can
            - Stop before it's over the limit
          - If it is over the word limit:
            - Split the section in half by word
            - Keep doing that until the subsections are under the limit
        - Convert each resulting section to a Scene

        Drawback:
        - Sections longer than the word limit will be split by word, not sentence or line.

        """
        raw_text = self.read_raw_text(session, text_id)
        raw_text_words_by_section = []
        if raw_text.use_regex:
            raw_text_words_by_section.extend(
                [
                    section.strip().split(" ")
                    for section in re.split(
                        re.compile(raw_text.separator), raw_text.content
                    )
                    if section.strip()
                ]
            )
        else:
            raw_text_words_by_section.extend(
                [
                    section.strip().split(" ")
                    for section in raw_text.content.split(raw_text.separator or "\n")
                    if section.strip()
                ]
            )

        sections = []
        previous_words: list[str] = []
        for index, current_words in enumerate(raw_text_words_by_section):
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
            if (not raw_text.separator) and chunk_length < word_limit:
                if next_index < len(raw_text_words_by_section):
                    if (
                        chunk_length + len(raw_text_words_by_section[next_index])
                        < word_limit
                    ):
                        previous_words.extend(words)
                        continue

            # If current line is above word limit, define how we're going to
            # split it down to fit: halve the target length until it's below the limit.
            while chunk_length > word_limit:
                chunk_length = -(-chunk_length // 2)

            # Split our current line down into sublists (chunks) as necessary
            chunks = [
                words[i : i + chunk_length] for i in range(0, len(words), chunk_length)
            ]
            sections.extend([" ".join(chunk) for chunk in chunks])

        return [
            Scene(
                content=section,
                text_id=text_id,
                checksum=md5(section.encode("utf-8")).hexdigest(),
            )
            for section in sections
        ]

    def create_scenes(self, session: Session, text_id: int, word_limit: int) -> None:
        """
        Split up a stored Raw Text into scenes
        """
        logger.info(f"Converting Text {text_id} into scenes")
        scenes = self.convert_raw_text_to_scenes(session, text_id, word_limit)
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
        """
        Find a specific scene
        """
        logger.info(f"Reading Scene {scene_id} from database")
        statement = select(Scene).where(Scene.id == scene_id)
        result: Optional[Scene] = session.exec(statement).first()
        if result:
            return result
        else:
            logger.error("Scene not found")
            raise Exception(f"Scene {scene_id} not found in database")

    def find_scenes_without_summaries(self, session: Session) -> list[Scene]:
        """
        Find all stored Scenes that do not yet have a summary
        """
        logger.info("Grabbing unsummarized scenes from database")
        statement = select(Scene).where(Scene.summary == "")
        return list(session.exec(statement).all())

    def update_summary(
        self, session: Session, scene_id: int, summary: str = ""
    ) -> None:
        """
        Add a summary to a Scene. If no summary is provided, clear the current summary.
        """
        logger.info(f"Summarizing Scene {scene_id}")
        scene = self.read_scene(session, scene_id)
        scene.summary = summary
        session.add(scene)
        session.commit()

    def find_scenes_with_summaries(self, session: Session) -> list[Scene]:
        """
        Find all stored Scenes that have a summary
        """
        logger.info("Grabbing summarized scenes from database")
        statement = select(Scene).where(Scene.summary != "")
        return list(session.exec(statement).all())

    def get_pcps(self, session: Session) -> list[dict]:
        """
        Get a list of prompt-completion pairs for all summarized scenes
        """
        logger.info("Grabbing PCPs")
        scenes = self.find_scenes_with_summaries(session)
        return [{"prompt": scene.summary, "completion": scene.content} for scene in scenes]
