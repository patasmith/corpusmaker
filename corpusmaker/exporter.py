"""
Export operations for Corpusmaker
"""

from dataclasses import dataclass


@dataclass
class Exporter:
    system_prompt: str

    def make_message(self, role: str, content: str) -> str:
        return '{"role": "' + role + '", "content": "' + content + '"}'

    def convert_pcp_to_chat_completion_jsonline(self, pcp: dict) -> str:
        system_message = self.make_message("system", self.system_prompt)
        user_message = self.make_message("user", pcp["prompt"])
        assistant_message = self.make_message("assistant", pcp["completion"])
        return (
            '{"messages": ['
            + system_message
            + ", "
            + user_message
            + ", "
            + assistant_message
            + "]}"
        )
