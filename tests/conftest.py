from typing import Generator
from pytest_mock import MockerFixture

import os
import pytest
from sqlmodel import Session
from corpusmaker.database import Database
from corpusmaker.model import RawText
from corpusmaker.loader import Loader
from corpusmaker.requester import Requester
from corpusmaker.exporter import Exporter
from corpusmaker.cli import Cli
from loguru import logger


@pytest.fixture
def simple_raw_text() -> Generator[RawText, None, None]:
    """
    Create a simple mock Raw Text
    """
    raw_text = RawText(content="This is a simple raw text.")
    yield raw_text


@pytest.fixture
def simple_raw_text_with_separator() -> Generator[RawText, None, None]:
    """
    Create a simple mock Raw Text with a separator
    """
    raw_text = RawText(
        content="This raw text has a separator.SEPNot much else to it.", separator="SEP"
    )
    yield raw_text


@pytest.fixture
def db_instance(scope: str = "session") -> Generator[Database, None, None]:
    """
    Create a database instance
    """
    db = Database("sqlite://")
    yield db


@pytest.fixture
def session(
    db_instance: Database, scope: str = "session"
) -> Generator[Session, None, None]:
    """
    Create a session and close after test
    """
    session = Session(db_instance.engine)
    yield session
    session.close()


@pytest.fixture
def db_instance_empty(
    db_instance: Database, session: Session
) -> Generator[Database, None, None]:
    """
    Create an empty database instance and clear after test
    """
    db_instance.delete_all_raw_text(session=session)
    yield db_instance
    db_instance.delete_all_raw_text(session=session)


@pytest.fixture
def loader(
    db_instance_empty: Database, session: Session
) -> Generator[Loader, None, None]:
    """
    Create a loader
    """
    loader = Loader(db_instance_empty)
    yield loader


@pytest.fixture
def db_instance_raw_text(
    loader: Loader, session: Session
) -> Generator[Database, None, None]:
    """
    Preload a database with raw text
    """
    loader.import_file("tests/files/test_file_1.txt")
    loader.import_file("tests/files/test_file_2.txt", "* * * * *")
    loader.import_file("tests/files/test_file_3.txt", "Chapter \\d+", True)
    loader.import_file("tests/files/test_file_4.txt")
    yield loader.db


@pytest.fixture
def db_instance_scenes(
    db_instance_raw_text: Database, session: Session
) -> Generator[Database, None, None]:
    """
    Preload a database with blank scenes
    """
    db_instance_raw_text.create_scenes(session, 3, 2000)
    yield db_instance_raw_text


@pytest.fixture
def requester(
    mocker: MockerFixture, scope: str = "session"
) -> Generator[Requester, None, None]:
    """
    Create a requester object for making API calls
    """
    mocker.patch(
        "corpusmaker.requester.Requester.generate_summary", return_value="mock summary"
    )
    requester = Requester(system_prompt="mock system prompt", model="gpt-3.5-turbo")
    yield requester


@pytest.fixture
def db_instance_summaries(
    db_instance_scenes: Database, requester: Requester, session: Session
) -> Generator[Database, None, None]:
    """
    Preload a database with summarized scenes
    """
    scenes = db_instance_scenes.find_scenes_without_summaries(session)
    for scene in scenes:
        assert type(scene.id) is int
        db_instance_scenes.update_summary(
            session, scene.id, requester.generate_summary(scene.content)
        )
    yield db_instance_scenes


@pytest.fixture
def exporter(scope: str = "module") -> Generator[Exporter, None, None]:
    exporter = Exporter(
        system_prompt="mock system prompt", filename="tests/files/test_output.jsonl"
    )
    yield exporter


@pytest.fixture
def cli() -> Generator[Cli, None, None]:
    filename = "tests/files/test.sqlite3"
    cli = Cli(db_file="sqlite:///" + filename)
    yield cli
    try:
        os.remove(filename)
    except FileNotFoundError:
        logger.error(f"Can't delete missing file: {filename}")


@pytest.fixture
def db_instance_real_summaries() -> Generator[Database, None, None]:
    db = Database("sqlite:///tests/files/summaries.sqlite3")
    yield db
