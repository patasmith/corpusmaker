"""
CLI operations for Corpusmaker
"""

from dataclasses import dataclass, field
from corpusmaker.database import Database
from corpusmaker.exporter import Exporter
from corpusmaker.loader import Loader
from corpusmaker.model import RawText, Scene
from corpusmaker.requester import Requester
from loguru import logger
from sqlmodel import Session, select
from datetime import datetime


@dataclass
class Cli:
    db_file: str = "data/corpus.sqlite3"
    db: Database = field(init=False)

    def __post_init__(self) -> None:
        self.db = Database(self.db_file)
        logger.info(f"Initialized database at {self.db_file}")

    def import_files(
        self, filenames: list[str], separator: str = "", use_regex: bool = False
    ) -> None:
        loader = Loader(self.db)
        loader.import_files(filenames, separator, use_regex)

    def create_scenes(self, word_limit: int = 8000) -> None:
        with Session(self.db.engine) as session:
            statement = (
                select(RawText).join(Scene, isouter=True).where(Scene.text_id == None)
            )
            results = session.execute(statement).all()
            for result in results:
                self.db.create_scenes(session, result.id, word_limit)

    def summarize_scenes(
        self,
        system_prompt_file: str = "data/system_prompt.txt",
        model: str = "gpt-3.5-turbo",
    ) -> None:
        with Session(self.db.engine) as session:
            scenes = self.db.find_scenes_without_summaries(session)
            if scenes:
                with open(system_prompt_file) as f:
                    system_prompt = f.read()
                requester = Requester(system_prompt, model)
                for scene in scenes:
                    if scene.id:
                        self.db.update_summary(
                            session, scene.id, requester.generate_summary(scene.content)
                        )
            else:
                logger.info("No scenes need summarizing")

    def export_summaries(
        self,
        system_prompt_file: str = "data/system_prompt.txt",
        export_file: str = f"data/scenes_{datetime.today().strftime}.jsonl",
    ) -> None:
        with Session(self.db.engine) as session:
            with open(system_prompt_file) as f:
                system_prompt = f.read()
            exporter = Exporter(system_prompt, export_file)
            pcps = self.db.get_pcps(session)
            exporter.export_pcps_to_jsonl(pcps)