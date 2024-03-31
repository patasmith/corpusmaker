"""
Export operations for Corpusmaker
"""

from dataclasses import dataclass
import json


@dataclass
class Exporter:
    system_prompt: str
    filename: str

    def make_message(self, role: str, content: str) -> dict[str, str]:
        return {"role": role, "content": content}

    def convert_pcp_to_chat_completion_jsonline(
        self, pcp: dict[str, str]
    ) -> dict[str, list[dict[str, str]]]:
        system_message = self.make_message(
            "system", self.system_prompt.encode("unicode_escape").decode("utf-8")
        )
        user_message = self.make_message("user", pcp["prompt"])
        assistant_message = self.make_message(
            "assistant", pcp["completion"].encode("unicode_escape").decode("utf-8")
        )
        return {"messages": [system_message, user_message, assistant_message]}

    def export_pcps_to_jsonl(self, pcps: list[dict[str, str]]) -> None:
        with open(self.filename, "w", encoding="utf-8-sig") as f:
            for pcp in pcps:
                json.dump(self.convert_pcp_to_chat_completion_jsonline(pcp), f)
                f.write("\n")
