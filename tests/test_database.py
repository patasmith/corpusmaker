import pytest
from corpusmaker.database import Database
from sqlmodel import Session
from corpusmaker.model import RawText


def test_add_raw_text_to_table(
    db_instance_empty: Database, session: Session, simple_raw_text: RawText
) -> None:
    """
    Raw text can be added to raw_text table
    Raw text separator can be updated
    Raw text entry can be deleted from raw_text table
    """
    db_instance_empty.create_raw_text(session=session, raw_text=simple_raw_text)
    raw_text = db_instance_empty.read_raw_text(session=session, text_id=1)
    content = simple_raw_text.content
    separator = simple_raw_text.separator
    assert raw_text.separator == separator
    assert raw_text.content == content

    db_instance_empty.update_raw_text_separator(
        session=session,
        text_id=1,
        separator="***",
    )
    assert raw_text.separator != separator
    assert raw_text.content == content

    db_instance_empty.delete_raw_text(session=session, text_id=1)
    with pytest.raises(Exception):
        db_instance_empty.read_raw_text(session=session, text_id=1)


def test_dont_add_duplicate_text_to_table(
    db_instance_empty: Database, session: Session, simple_raw_text: RawText
) -> None:
    """
    Duplicate text cannot be added to raw_text table
    """
    db_instance_empty.create_raw_text(session=session, raw_text=simple_raw_text)
    with pytest.raises(Exception):
        db_instance_empty.create_raw_text(session=session, raw_text=simple_raw_text)
