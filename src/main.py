from middleware import serve
from utils.mappers import mappers
from utils.db import db_manager
from utils.prompt import prompt


def init_db_connection():
    print(f'Connected database (test): {"OK" if db_manager.connect() else "NO"}.')


def scan_mappers():
    loaded_number = mappers.load_paths()
    print(f'Number of scanned mappers: {"can not find the path" if loaded_number == -1 else loaded_number}.')


def main_loop():
    init_db_connection()
    scan_mappers()
    while True:
        text = prompt.prompt("command: ")
        serve(text)
        if text in ["exit", "q", "quit"]:
            break


if __name__ == '__main__':
    main_loop()
