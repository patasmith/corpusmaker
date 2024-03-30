from corpusmaker.database import Database
from corpusmaker.requester import Requester
from sqlmodel import Session


def test_generate_summaries(
    mocker, db_instance_scenes: Database, session: Session, requester: Requester
) -> None:
    """
    Generate summaries from scene content
    """
    scenes = db_instance_scenes.find_scenes_without_summaries(session)
    assert scenes[2].summary == ""

    requester.generate_summaries(scenes)
    for scene in scenes:
        session.add(scene)
    session.commit()

    should_be_empty_now = db_instance_scenes.find_scenes_without_summaries(session)
    assert len(should_be_empty_now) == 0

    scene_3 = db_instance_scenes.read_scene(session, 3)
    assert scene_3.summary == "mock summary"
