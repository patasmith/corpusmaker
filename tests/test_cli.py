from pytest_mock import MockerFixture

import json
from corpusmaker.cli import Cli
from sqlmodel import Session


def test_import_files(cli: Cli) -> None:
    filename = "tests/files/test_file_5.txt"
    separator = "* * * * *"
    cli.import_files([filename], separator)
    with open(filename) as f:
        content = f.read()

    with Session(cli.db.engine) as session:
        raw_text = cli.db.read_raw_text(session, 1)
        assert raw_text.content == content
        assert raw_text.separator == separator


def test_create_and_summarize_in_stages(mocker: MockerFixture, cli: Cli) -> None:
    filenames = ["tests/files/test_file_5.txt", "tests/files/test_file_2.txt"]
    separator = "* * * * *"
    cli.import_files(filenames, separator)
    cli.create_scenes()

    with Session(cli.db.engine) as session:
        scenes = cli.db.find_scenes_without_summaries(session)
        assert len(scenes) == 10
        for index, scene in enumerate(scenes):
            if index < 5:
                assert scenes[index].content == f"Scene {index + 1}"

        mocker.patch(
            "corpusmaker.requester.Requester.generate_summary",
            return_value="mock summary",
        )

    cli.summarize_scenes("tests/files/system_prompt.txt")

    with Session(cli.db.engine) as session:
        summarized_scenes = cli.db.find_scenes_with_summaries(session)
        assert len(summarized_scenes) == 10
        for scene in summarized_scenes:
            assert scene.summary == "mock summary"

    filename2 = "tests/files/test_file_1.txt"
    cli.import_files([filename2])
    cli.create_scenes(word_limit=250)

    with Session(cli.db.engine) as session:
        scenes = cli.db.find_scenes_without_summaries(session)
        assert len(scenes) == 2

    cli.summarize_scenes("tests/files/system_prompt.txt")

    with Session(cli.db.engine) as session:
        summarized_scenes = cli.db.find_scenes_with_summaries(session)
        assert len(summarized_scenes) == 12


def test_export_to_jsonl(mocker: MockerFixture, cli: Cli) -> None:
    filenames = ["tests/files/test_file_5.txt", "tests/files/test_file_2.txt"]
    separator = "* * * * *"
    system_prompt = "tests/files/system_prompt.txt"
    jsonl = "tests/files/scenes.jsonl"
    cli.import_files(filenames, separator)
    cli.create_scenes()

    mocker.patch(
        "corpusmaker.requester.Requester.generate_summary",
        return_value="mock summary",
    )

    cli.summarize_scenes(system_prompt)
    cli.export_summaries(system_prompt, jsonl)
    with open(jsonl, "r") as f:
        content = [json.loads(line) for line in f]
    assert len(content) == 10
