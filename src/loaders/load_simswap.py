from creator import creator
from settings import settings
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader


@process_mapper(mapper="simswap")
def load(*args, **kwargs):
    default_loader(args, kwargs)
    print("Successfully done.")
