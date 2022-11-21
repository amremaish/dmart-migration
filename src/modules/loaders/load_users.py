from modules.creator import spaces_creator
from modules.mapper import convert_db_to_meta
from settings import settings
from utils.db import db_manager
from utils.docorators import process_mapper
from utils.prompt import prompt


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

        prompt.print("-> processing query: " + db_result.get('query'))
        for row in db_result.get('data'):
            meta, body = convert_db_to_meta(row, mapper_data)
            space_name = mapper_data.get('dest').get('space_name')
            subpath = mapper_data.get('dest').get('subpath')
            resource_type = mapper_data.get('dest').get('resource_type')
            spaces_creator.save(
                space_name=space_name,
                subpath=subpath,
                class_type=resource_type,
                meta=meta,
                body=body)
        offset += db_result['returned']
        if db_result['returned'] != settings.fetch_limit:
            break

    prompt.print("Successfully done.")
