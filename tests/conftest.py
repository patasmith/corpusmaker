from typing import Generator
import pytest
from sqlmodel import Session
from corpusmaker.database import Database
from corpusmaker.model import RawText


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
    db_instance: Database, session: Session, scope: str = "function"
) -> Generator[Database, None, None]:
    """
    Create an empty database instance and clear after test
    """
    db_instance.delete_all_raw_text(session=session)
    yield db_instance
    db_instance.delete_all_raw_text(session=session)
