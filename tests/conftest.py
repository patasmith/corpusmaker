from typing import Generator
import pytest
from sqlmodel import Session
from corpusmaker.database import Database
from corpusmaker.model import RawText
from corpusmaker.loader import Loader
from corpusmaker.requester import Requester


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
    Preload a database with scenes
    """
    db_instance_raw_text.create_scenes(session, 3, 2000)
    yield db_instance_raw_text


@pytest.fixture
def requester(mocker, scope: str = "session") -> Generator[Requester, None, None]:
    """
    Create a requester object for making API calls
    """
    mocker.patch(
        "corpusmaker.requester.Requester.generate_summary", return_value="mock summary"
    )
    requester = Requester()
    yield requester
