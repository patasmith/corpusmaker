from corpusmaker.database import Database
from corpusmaker.exporter import Exporter
from sqlmodel import Session
import json


def test_convert_pcp_to_jsonl(exporter: Exporter) -> None:
    pcp = {"prompt": "mock prompt", "completion": "mock completion"}
    line = exporter.convert_pcp_to_chat_completion_jsonline(pcp)
    assert line == {
        "messages": [
            {"role": "system", "content": "mock system prompt"},
            {"role": "user", "content": "mock prompt"},
            {"role": "assistant", "content": "mock completion"},
        ]
    }


def test_export_pcps_to_jsonl(
    db_instance_summaries: Database, exporter: Exporter, session: Session
) -> None:
    pcps = db_instance_summaries.get_pcps(session)
    exporter.export_pcps_to_jsonl(pcps)
    with open(exporter.filename, encoding="utf-8-sig") as f:
        jsonl = f.read().split("\n")
    for index, pcp in enumerate(pcps):
        jsonline = exporter.convert_pcp_to_chat_completion_jsonline(pcp)
        assert json.loads(jsonl[index]) == jsonline
