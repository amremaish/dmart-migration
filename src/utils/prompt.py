import re

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory


class Prompt:

    def __init__(self):
        self.session = PromptSession(
            history=FileHistory(".history")
        )

    def prompt(self, message: str | None = None) -> str:
        text = self.session.prompt(
            message=message,
            complete_in_thread=True,
            complete_while_typing=True,
        )
        text = re.sub(r"^\s+", "", text)
        text = re.sub(r"\s+$", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def print(self, message):
        print(message)


prompt = Prompt()
