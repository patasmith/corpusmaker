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
        return "not working"
        """
        return (
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
        """

    def generate_summaries(self, scenes: list[Scene]) -> None:
        """
        Generate summaries for each scene in a list
        """
        for scene in scenes:
            scene.summary = self.generate_summary(scene.content)
