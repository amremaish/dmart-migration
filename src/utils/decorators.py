from utils.db import db_manager
from utils.mappers import mappers


def process_mapper(mapper):
    def decorator(function):
        def wrapper(*args, **kwargs):
            mappers.validate_file_entry(mapper, "mapper")
            kwargs['mapper_data'] = mappers.load(mapper)
            columns = db_manager.create_aliases(kwargs['mapper_data']['source']['columns'])
            kwargs['mapper_data']['source']['columns'] = columns
            kwargs['current_mapper'] = mapper
            function(*args, **kwargs)

        return wrapper

    return decorator
