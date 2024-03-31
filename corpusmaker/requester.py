"""
API operations for Corpusmaker
"""

from dataclasses import dataclass
from openai import OpenAI


@dataclass
class Requester:
    client = OpenAI()
    system_prompt: str
    model: str

    def generate_summary(self, content: str) -> str:
        """
        Summarize the provided text
        """
        return str(
            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": content},
                ],
            )
            .choices[0]
            .message
        )
