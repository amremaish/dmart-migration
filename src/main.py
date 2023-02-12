import traceback
import re
import jsonschema
import jsonschema.exceptions
import creator

from enum import Enum

from settings import settings
from utils.mappers import mappers
from utils.db import db_manager
from utils.move_attachments import move_attachments


class OperationsType(str, Enum):
    MIGRTAE = "migrate"
    MOVE = "move"


def import_from(module, name):
    module = __import__(module, fromlist=[name])
    return getattr(module, name)


def prompt(message: str | None = None) -> str:
    text = input(message)
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
    if operation == OperationsType.MOVE:
        move_attachments(loader)

def main_loop():
    check = db_manager.connect()
    print(f'Connected database ({settings.db_name}): {"OK" if check else "NO"}.')
    loaded_number = mappers.load_paths()
    print(f'Number of scanned mappers: {"can not find the path" if loaded_number == -1 else loaded_number}.')
    if not check or not loaded_number:
        print('Please fix your connection')
        return
    creator.creator.scan()
    while True:
        text = prompt("command: ")
        try:
            serve(text)
        except jsonschema.exceptions.ValidationError as e:
            print(str(e.message) + '\n')
            print(traceback.format_exc())
        except Exception as e:
            print(traceback.format_exc())
        if text in ["exit", "q", "quit"]:
            break


if __name__ == '__main__':
    main_loop()
