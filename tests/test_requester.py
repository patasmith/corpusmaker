from pytest import fail
from corpusmaker.database import Database
from corpusmaker.requester import Requester
from sqlmodel import Session


def test_generate_summaries(
    db_instance_scenes: Database,
    session: Session,
    requester: Requester,
) -> None:
    """
    Generate summaries from scene content
    """
    scenes = db_instance_scenes.find_scenes_without_summaries(session)
    for scene in scenes:
        assert scene.summary == ""
        summary = requester.generate_summary(scene.content)
        assert summary == "mock summary"
        assert type(scene.id) is int
        db_instance_scenes.update_summary(
            session=session, scene_id=scene.id, summary=summary
        )
        updated_scene = db_instance_scenes.read_scene(
            session=session, scene_id=scene.id
        )
        assert updated_scene.summary == "mock summary"

    should_be_empty_now = db_instance_scenes.find_scenes_without_summaries(session)
    assert len(should_be_empty_now) == 0
