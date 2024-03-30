"""
API operations for Corpusmaker
"""

from dataclasses import dataclass
from corpusmaker.model import Scene
from openai import OpenAI


@dataclass
class Requester:
    client = OpenAI()

    def generate_summary(self, content: str) -> str:
        """
        Summarize the provided text
        """
        return str(
            self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "system prompt"},
                    {"role": "user", "content": "user prompt"},
                ],
            )
            .choices[0]
            .message
        )
