from creator import creator
from settings import settings
from utils.db import db_manager
from utils.decorators import process_mapper


@process_mapper(mapper="users")
def load(*args, **kwargs):
    # comes from process_mapper decorator
    mapper_data: dict = kwargs['mapper_data']
    offset: int = 0
    while True:
        db_result = db_manager.select_query(
            table_name=mapper_data.get('source').get('table'),
            columns=mapper_data.get('source').get('columns'),
            join_tables=mapper_data.get('source').get('join'),
            limit=settings.fetch_limit,
            offset=offset)

        print("-> processing query: " + db_result.get('query'))
        for row in db_result.get('data'):
            meta, body = creator.convert_db_to_meta(row, mapper_data)
            space_name = mapper_data.get('dest').get('space_name')
            subpath = mapper_data.get('dest').get('subpath')
            resource_type = mapper_data.get('dest').get('resource_type')
            creator.save(
                space_name=space_name,
                subpath=subpath,
                class_type=resource_type,
                meta=meta,
                body=body)
        offset += db_result['returned']
        if db_result['returned'] != settings.fetch_limit:
            break

    print("Successfully done.")
