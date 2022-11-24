from creator import creator
from settings import settings
from utils.db import db_manager


def default_loader(args, kwargs):
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

        for row in db_result.get('data'):
            meta, body = creator.convert_db_to_meta(row, mapper_data)
            space_name = mapper_data.get('dest').get('space_name')
            schema_shortname = mapper_data.get('dest').get('schema_shortname')
            subpath = mapper_data.get('dest').get('subpath')
            resource_type = mapper_data.get('dest').get('resource_type')
            creator.save(
                space_name=space_name,
                subpath=subpath,
                class_type=resource_type,
                schema_shortname=schema_shortname,
                meta=meta,
                body=body)
        offset += db_result['returned']

        print("-> Successfully executed")

        if offset > settings.max_records and settings.max_records != -1:
            break
        if db_result['returned'] != settings.fetch_limit:
            break
