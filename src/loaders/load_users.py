from utils.decorators import process_mapper
from utils.default_loader import default_loader


@process_mapper(mapper="users")
def load(*args, **kwargs):
    default_loader(args, kwargs)
    print("Successfully done.")
