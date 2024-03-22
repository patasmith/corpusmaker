import pytest


def test_create_raw_text(db_instance_empty, session, simple_raw_text):
    """
    Test the creation of raw text
    """
    db_instance_empty.create_raw_text(raw_text=simple_raw_text, session=session)


def test_delete_raw_text(
    db_instance_empty, session, simple_raw_text, simple_raw_text_with_separator
):
    """
    Test deletion of raw text
    """

    db_instance_empty.create_raw_text(session=session, raw_text=simple_raw_text)
    db_instance_empty.create_raw_text(
        session=session, raw_text=simple_raw_text_with_separator
    )

    db_instance_empty.delete_raw_text(session=session, text_id=1)
    # with pytest.raises(Exception):
