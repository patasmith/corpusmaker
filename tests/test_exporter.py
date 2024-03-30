from corpusmaker.exporter import Exporter


def test_convert_pcp_to_jsonl(exporter: Exporter) -> None:
    pcp = {"prompt": "mock prompt", "completion": "mock completion"}
    line = exporter.convert_pcp_to_chat_completion_jsonline(pcp)
    assert line == (
        '{"messages": [{"role": "system", "content": "mock system prompt"}, '
        '{"role": "user", "content": "mock prompt"}, '
        '{"role": "assistant", "content": "mock completion"}]}'
    )
