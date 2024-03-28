import pytest
from corpusmaker.database import Database
from sqlmodel import Session
from corpusmaker.model import RawText, Scene


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


def test_change_separator_for_raw_text_entry(
    db_instance_empty: Database, session: Session, simple_raw_text: RawText
) -> None:
    """
    Raw text separator can be changed
    """
    separator = "new separator"
    db_instance_empty.create_raw_text(session=session, raw_text=simple_raw_text)
    db_instance_empty.update_raw_text_separator(
        session=session, text_id=1, separator=separator
    )
    raw_text = db_instance_empty.read_raw_text(session=session, text_id=1)
    assert raw_text.separator == separator


def test_split_raw_text_without_separator_into_scenes(
    db_instance_raw_text: Database, session: Session
) -> None:
    """
    Raw text without a separator can be split into properly sized scenes
    """
    raw_text_lines = [
        line
        for line in db_instance_raw_text.read_raw_text(
            session=session, text_id=1
        ).content.split("\n")
        if line.strip()
    ]
    scenes = db_instance_raw_text.convert_raw_text_to_scenes(
        session=session, text_id=1, word_limit=100
    )
    assert scenes[0].text_id == 1
    assert scenes[0].content == raw_text_lines[0]
    assert scenes[2].text_id == 1
    assert scenes[2].content == raw_text_lines[2][:411]


def test_add_scenes_to_scene_table(
    db_instance_raw_text: Database, session: Session
) -> None:
    """
    Scenes can be added to scene table
    """
    db_instance_raw_text.create_scenes(session=session, text_id=1)
    raw_text = db_instance_raw_text.read_raw_text(session=session, text_id=1)
    scene = db_instance_raw_text.read_scene(session=session, scene_id=1)
    assert raw_text.content == scene.content
