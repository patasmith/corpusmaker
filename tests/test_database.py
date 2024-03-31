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
    db_instance_empty.create_raw_text(session=session, raw_text=simple_raw_text)
    with pytest.raises(Exception):
        db_instance_empty.read_raw_text(session=session, text_id=2)


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


def split_raw_text(db: Database, session: Session, text_id: int) -> list[str]:
    return [
        line
        for line in db.read_raw_text(session=session, text_id=text_id).content.split(
            "\n"
        )
        if line.strip()
    ]


def test_split_raw_text_without_separator_into_scenes(
    db_instance_raw_text: Database, session: Session
) -> None:
    """
    Raw text without a separator can be split into properly sized scenes
    """
    raw_text_lines_1 = split_raw_text(db_instance_raw_text, session, 1)
    scenes_1 = db_instance_raw_text.convert_raw_text_to_scenes(
        session=session, text_id=1, word_limit=100
    )
    assert scenes_1[0].text_id == 1
    assert scenes_1[0].content == raw_text_lines_1[0]
    assert scenes_1[2].text_id == 1
    assert scenes_1[2].content == raw_text_lines_1[2][:411]

    raw_text_lines_4 = split_raw_text(db_instance_raw_text, session, 4)
    scenes_4 = db_instance_raw_text.convert_raw_text_to_scenes(
        session=session, text_id=4, word_limit=100
    )
    assert scenes_4[0].text_id == 4
    assert scenes_4[0].content == " ".join(raw_text_lines_4[:10])
    assert scenes_4[1].text_id == 4
    assert scenes_4[1].content == " ".join(raw_text_lines_4[10:14])
    assert scenes_4[2].text_id == 4
    assert scenes_4[2].content == raw_text_lines_4[14][:411]


def test_split_raw_text_with_separator_into_scenes(
    db_instance_raw_text: Database, session: Session
) -> None:
    """
    Raw text with a separator can be split into properly sized scenes
    """
    raw_text_lines_2 = split_raw_text(db_instance_raw_text, session, 2)

    scenes_2_100 = db_instance_raw_text.convert_raw_text_to_scenes(
        session=session, text_id=2, word_limit=100
    )
    assert scenes_2_100[0].text_id == 2
    assert scenes_2_100[0].content == raw_text_lines_2[0]

    scenes_2_60 = db_instance_raw_text.convert_raw_text_to_scenes(
        session=session, text_id=2, word_limit=60
    )
    assert scenes_2_60[0].text_id == 2
    assert scenes_2_60[0].content == raw_text_lines_2[0][:328]
    assert scenes_2_60[1].content == raw_text_lines_2[0][329:]
    assert scenes_2_60[2].content == raw_text_lines_2[2]
    assert scenes_2_60[3].content == " ".join(raw_text_lines_2[4].split(" ")[:33])
    assert scenes_2_60[4].content == " ".join(raw_text_lines_2[4].split(" ")[33:66])
    assert scenes_2_60[5].content == " ".join(raw_text_lines_2[4].split(" ")[66:99])
    assert scenes_2_60[6].content == " ".join(raw_text_lines_2[4].split(" ")[99:])


def test_split_raw_text_with_regex_separator_into_scenes(
    db_instance_raw_text: Database, session: Session
) -> None:
    """
    Raw text with a regex separator will be handled as above
    """
    raw_text_lines_3 = split_raw_text(db_instance_raw_text, session, 3)

    scenes_3_100 = db_instance_raw_text.convert_raw_text_to_scenes(
        session=session, text_id=3, word_limit=100
    )
    assert scenes_3_100[0].text_id == 3
    assert scenes_3_100[0].content == raw_text_lines_3[1]
    assert scenes_3_100[2].content == " ".join(raw_text_lines_3[5].split(" ")[:65])


def test_add_scenes_to_scene_table(
    db_instance_raw_text: Database, session: Session
) -> None:
    """
    Scenes can be added to scene table
    """
    db_instance_raw_text.create_scenes(session=session, text_id=1, word_limit=100)
    raw_text_lines = split_raw_text(db_instance_raw_text, session, 1)
    scene = db_instance_raw_text.read_scene(session=session, scene_id=1)
    assert scene.text_id == 1
    assert scene.content == raw_text_lines[0]


def test_find_scenes_without_summaries(
    db_instance_scenes: Database, session: Session
) -> None:
    """
    Get content of scenes that don't have summaries
    """
    scenes = db_instance_scenes.find_scenes_without_summaries(session)
    for i in range(0, 4):
        assert scenes[i].id == i + 1

    summary = "An example scene summary."
    db_instance_scenes.update_summary(session=session, scene_id=1, summary=summary)
    scene_1 = db_instance_scenes.read_scene(session=session, scene_id=1)
    assert scene_1.summary == summary

    db_instance_scenes.update_summary(session=session, scene_id=4, summary=summary)
    db_instance_scenes.find_scenes_without_summaries(session)
    for i in [2, 3, 5]:
        assert scenes[i - 1].id == i


def test_find_scenes_with_summaries(
    db_instance_summaries: Database, session: Session
) -> None:
    """
    Get list of all scenes that have summaries
    """
    scenes = db_instance_summaries.find_scenes_with_summaries(session)
    for scene in scenes:
        assert scene.summary == "mock summary"


def test_convert_summarized_scenes_to_pcps(
    db_instance_summaries: Database, session: Session
) -> None:
    """
    Convert contents and summaries of scenes to prompt-completion pairs
    """
    pcps = db_instance_summaries.get_pcps(session)
    assert len(pcps) == 5
    for pcp in pcps:
        assert pcp["prompt"] == "mock summary"
        assert type(pcp["completion"]) is str
        assert len(pcp["completion"]) > 0


def test_only_convert_valid_summaries(db_instance_real_summaries: Database) -> None:
    """
    PCPs must contain a specific phrase in the completion
    """
    with Session(db_instance_real_summaries.engine) as session:
        pcps = db_instance_real_summaries.get_pcps(session, "SUMMARY:")
        assert len(pcps) == 3
