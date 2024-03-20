import pytest
from sqlmodel import Session
from corpusmaker.model import RawText


@pytest.fixture
def simple_raw_text():
    """
    Create a simple mock Raw Text
    """
    raw_text = RawText(content="This is a simple raw text.")
    yield raw_text


@pytest.fixture
def simple_raw_text_with_separator():
    """
    Create a simple mock Raw Text with a separator
    """
    raw_text = RawText(
        content="This raw text has a separator.SEPNot much else to it.", separator="SEP"
    )
    yield raw_text


@pytest.fixture
def db_instance(scope="session"):
    """
    Create a database instance
    """
    db = DB()
