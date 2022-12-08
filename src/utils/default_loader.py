from datetime import datetime

from creator import creator
from settings import settings
from utils.db import db_manager


def default_loader(args, kwargs, apply_modifier=None):
    # comes from process_mapper decorator
    mapper_data: dict = kwargs['mapper_data']
    remove_null_field: bool = kwargs['remove_null_field']
    only_matched_schema: bool = kwargs['only_matched_schema']
    appended_list: bool = kwargs['appended_list']
    offset: int = 0
    while True:
        db_result = db_manager.select_query(
            table_name=mapper_data.get('source').get('table'),
            columns=mapper_data.get('source').get('columns'),
            join_tables=mapper_data.get('source').get('join'),
            where=mapper_data.get('source').get('where'),
            limit=settings.fetch_limit,
            offset=offset)
        for row in db_result.get('data'):
            space_name = mapper_data.get('dest').get('space_name')
            schema_shortname = mapper_data.get('dest').get('schema_shortname')
            subpath = mapper_data.get('dest').get('subpath')
            resource_type = mapper_data.get('dest').get('resource_type')
            meta, body = creator.convert_db_to_meta(row, mapper_data, remove_null_field)
            creator.shortname_deep_fixer(meta)
            creator.shortname_deep_fixer(body)
            if meta.get('shortname') != '78522222':
                continue
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

            creator.save(
                space_name=space_name,
                subpath=subpath,
                class_type=resource_type,
                schema_shortname=schema_shortname,
                meta=meta,
                body=body,
                only_matched_schema=only_matched_schema,
                appended_list=appended_list
            )
        offset += db_result['returned']

        if offset > settings.max_records and settings.max_records != -1:
            break
        if db_result['returned'] != settings.fetch_limit:
            break


def meta_fixer(meta: dict):
    if not meta.get('updated_at'):
        meta['updated_at'] = meta.get('created_at')

    if not meta.get('created_at'):
        meta['created_at'] = meta.get('updated_at')

    if not meta.get('updated_at'):
        meta['updated_at'] = datetime.now().isoformat()

    if not meta.get('created_at'):
        meta['created_at'] = datetime.now().isoformat()

    if not meta.get('is_active') or not isinstance(meta.get('is_active'), bool):
        meta['is_active'] = True

    return meta
