from enum import Enum


class OperationsType(str, Enum):
    MIGRTAE = "migrate"


def import_from(module, name):
    module = __import__(module, fromlist=[name])
    return getattr(module, name)


def serve(text: str):
    inputs = text.split(" ")
    if len(inputs) < 2:
        return
    operation = inputs[0].lower()
    loader = inputs[1].lower()

    if operation == OperationsType.MIGRTAE:
        func = import_from(f'modules.loaders.load_{loader}', 'load')
        func()
