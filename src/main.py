import jsonschema
import jsonschema.exceptions

from middleware import serve
from modules.creator import spaces_creator
from utils.mappers import mappers
from utils.db import db_manager
from utils.prompt import prompt
from settings import settings


def init_db_connection():
    check = db_manager.connect()
    print(f'Connected database (test): {"OK" if check else "NO"}.')
    return check


def scan_mappers():
    loaded_number = mappers.load_paths()
    print(f'Number of scanned mappers: {"can not find the path" if loaded_number == -1 else loaded_number}.')
    return loaded_number


def main_loop():
    check_db = init_db_connection()
    check_mapper = scan_mappers()
    spaces_creator.scan()
    if not check_db or not check_mapper:
        prompt.print('Please fix your connection')
        return

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
