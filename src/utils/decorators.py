from utils.mappers import mappers


def process_mapper(mapper):
    def decorator(function):
        def wrapper(*args, **kwargs):
            mappers.validate_file_entry(mapper, "mapper")
            kwargs['mapper_data'] = mappers.load(mapper)
            columns = kwargs['mapper_data'].get('source').get('columns')
            columns = [f'{col} {col.split(".")[0]}_{col.split(".")[1]}' for col in columns]
            kwargs['mapper_data']['source']['columns'] = columns
            kwargs['current_mapper'] = mapper
            function(*args, **kwargs)

        return wrapper

    return decorator
