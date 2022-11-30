from utils.db import db_manager
from utils.mappers import mappers


def process_mapper(mapper: str, remove_null_field: bool = False, only_matched_schema: bool = False):
    def decorator(function):
        def wrapper(*args, **kwargs):
            mappers.validate_file_entry(mapper, "mapper")
            kwargs['mapper_data'] = mappers.load(mapper)
            columns = db_manager.create_aliases(kwargs['mapper_data']['source']['columns'])
            kwargs['mapper_data']['source']['columns'] = columns
            kwargs['current_mapper'] = mapper
            kwargs['remove_null_field'] = remove_null_field
            kwargs['only_matched_schema'] = only_matched_schema

            function(*args, **kwargs)

        return wrapper

    return decorator
