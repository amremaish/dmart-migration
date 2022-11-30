from creator import creator
from dmart import core
from settings import settings
from utils.db import db_manager


def default_loader(args, kwargs, apply_modifier=None):
    # comes from process_mapper decorator
    mapper_data: dict = kwargs['mapper_data']
    remove_null_field: bool = kwargs['remove_null_field']
    only_matched_schema: bool = kwargs['only_matched_schema']
    offset: int = 0
    while True:
        db_result = db_manager.select_query(
            table_name=mapper_data.get('source').get('table'),
            columns=mapper_data.get('source').get('columns'),
            join_tables=mapper_data.get('source').get('join'),
            limit=settings.fetch_limit,
            offset=offset)
        for row in db_result.get('data'):
            space_name = mapper_data.get('dest').get('space_name')
            schema_shortname = mapper_data.get('dest').get('schema_shortname')
            subpath = mapper_data.get('dest').get('subpath')
            resource_type = mapper_data.get('dest').get('resource_type')
            meta, body = creator.convert_db_to_meta(row, mapper_data, remove_null_field)
            meta['shortname'] = meta['shortname'].strip().lower().replace(' ', '')
            if apply_modifier:
                modified = apply_modifier(
                    space_name=space_name,
                    subpath=subpath,
                    resource_type=resource_type,
                    schema_shortname=schema_shortname,
                    meta=meta,
                    body=body,
                    db_row=row,
                )
                meta = modified["meta"]
                body = modified["body"]
                space_name = modified["space_name"]
                subpath = modified["subpath"]
                resource_type = modified["resource_type"]

            if not meta.get('owner_shortname'):
                meta['owner_shortname'] = 'dmart'

            meta_obj = core.Meta(**meta)
            meta_obj.payload = core.Payload(
                content_type='json',
                schema_shortname=schema_shortname,
                body=f'{meta_obj.shortname}.json'
            )

            creator.save(
                space_name=space_name,
                subpath=subpath,
                class_type=resource_type,
                schema_shortname=schema_shortname,
                meta=meta_obj,
                body=body,
                only_matched_schema=only_matched_schema
            )
        offset += db_result['returned']

        if offset > settings.max_records and settings.max_records != -1:
            break
        if db_result['returned'] != settings.fetch_limit:
            break
