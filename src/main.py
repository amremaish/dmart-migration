import jsonschema
import re
import jsonschema.exceptions

from enum import Enum

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from creator import creator
from utils.mappers import mappers
from utils.db import db_manager

session = PromptSession(
    history=FileHistory(".history")
)

class OperationsType(str, Enum):
    MIGRTAE = "migrate"


def import_from(module, name):
    module = __import__(module, fromlist=[name])
    return getattr(module, name)


def prompt(message: str | None = None) -> str:
    text = session.prompt(
        message=message,
        complete_in_thread=True,
        complete_while_typing=True,
    )
    text = re.sub(r"^\s+", "", text)
    text = re.sub(r"\s+$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def serve(text: str):
    inputs = text.split(" ")
    if len(inputs) < 2:
        return
    operation = inputs[0].lower()
    loader = inputs[1].lower()

    if operation == OperationsType.MIGRTAE:
        func = import_from(f'loaders.load_{loader}', 'load')
        func()


def main_loop():
    check = db_manager.connect()
    print(f'Connected database (test): {"OK" if check else "NO"}.')
    loaded_number = mappers.load_paths()
    print(f'Number of scanned mappers: {"can not find the path" if loaded_number == -1 else loaded_number}.')
    if not check or not loaded_number:
        print('Please fix your connection')
        return
    creator.scan()

    while True:
        text = prompt("command: ")
        try:
            serve(text)
        except jsonschema.exceptions.ValidationError as e:
            print(str(e.message) + '\n')
        except Exception as e:
            print(str(e) + '\n')
        if text in ["exit", "q", "quit"]:
            break


if __name__ == '__main__':
    main_loop()
