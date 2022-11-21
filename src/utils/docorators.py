from utils.mappers import mappers


def process_mapper(mapper):
    def decorator(function):
        def wrapper(*args, **kwargs):
            mappers.validate_entry(mapper, "mapper")
            kwargs['mapper_data'] = mappers.load(mapper)
            function(*args, **kwargs)

        return wrapper

    return decorator
