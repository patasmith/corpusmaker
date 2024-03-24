import pytest
from corpusmaker.database import Database
from sqlmodel import Session
from corpusmaker.model import RawText


# Text within textfile can be added to raw_text table
def test_add_raw_text_to_table(
    db_instance_empty: Database, session: Session, simple_raw_text: RawText
) -> None:
    db_instance_empty.create_raw_text(session=session, raw_text=simple_raw_text)

    raw_text = db_instance_empty.read_raw_text(session=session, text_id=1)
    assert raw_text.separator == simple_raw_text.separator
    assert raw_text.content == simple_raw_text.content


# Entries can be removed from raw_text table
def test_remove_raw_text_from_table(
    db_instance_empty: Database,
    session: Session,
    simple_raw_text: RawText,
    simple_raw_text_with_separator: RawText,
) -> None:
    db_instance_empty.create_raw_text(session=session, raw_text=simple_raw_text)
    db_instance_empty.create_raw_text(
        session=session, raw_text=simple_raw_text_with_separator
    )

    db_instance_empty.delete_raw_text(session=session, text_id=1)
    with pytest.raises(Exception):
        db_instance_empty.read_raw_text(session=session, text_id=1)


# Duplicate text cannot be added to raw_text table
# Use checksum
def test_dont_add_duplicate_text_to_table(
    db_instance_empty: Database, session: Session, simple_raw_text: RawText
) -> None:
    db_instance_empty.create_raw_text(session=session, raw_text=simple_raw_text)
    with pytest.raises(Exception):
        db_instance_empty.create_raw_text(session=session, raw_text=simple_raw_text)


# Multiple textfiles can be added at once
# Each textfile will be a separate entry
def test_add_multiple_texts_to_table() -> None:
    pass


# Separator can be specified for textfile(s) when added
def test_associate_separator_with_text() -> None:
    pass


# Separator can be changed for individual textfiles
def test_change_associated_separator_for_text() -> None:
    pass
