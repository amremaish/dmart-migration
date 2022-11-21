import jsonschema

from middleware import serve
from modules.creator import SpaceCreator, spaces_creator
from utils.mappers import mappers
from utils.db import db_manager
from utils.prompt import prompt


def init_db_connection():
    print(f'Connected database (test): {"OK" if db_manager.connect() else "NO"}.')


def scan_mappers():
    loaded_number = mappers.load_paths()
    print(f'Number of scanned mappers: {"can not find the path" if loaded_number == -1 else loaded_number}.')
    return loaded_number


def main_loop():
    init_db_connection()
    scan_mappers()
    spaces_creator.load()
    while True:
        text = prompt.prompt("command: ")
        try:
            serve(text)
        except jsonschema.exceptions.ValidationError as e:
            prompt.prompt(str(e.message) + '\n')
        except Exception as e:
            prompt.prompt(str(e) + '\n')
        if text in ["exit", "q", "quit"]:
            break


if __name__ == '__main__':
    main_loop()
