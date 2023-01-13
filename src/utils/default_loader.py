import re
import time
from datetime import datetime

from creator import creator
from dmart.helper import MSISDN_REGEX
from settings import settings
from utils.db import db_manager


def default_loader(args, kwargs, apply_modifier=None):
    # comes from process_mapper decorator
    mapper_data: dict = kwargs['mapper_data']
    remove_null_field: bool = kwargs['remove_null_field']
    only_matched_schema: bool = kwargs['only_matched_schema']
    appended_list: list = kwargs['appended_list']
    disable_duplication_appended_list: bool = kwargs['disable_duplication_appended_list']

    offset: int = 0
    before_time = time.time()
    # load all lockup table
    lookup: dict = db_manager.load_lookup()
    while True:
        sub_before_time = time.time()
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
            history_obj = None

            meta, body = creator.convert_db_to_meta(row, mapper_data, remove_null_field)
            creator.shortname_deep_fixer(meta)
            creator.shortname_deep_fixer(body)
            if apply_modifier:
                modified = apply_modifier(
                    space_name=space_name,
                    subpath=subpath,
                    resource_type=resource_type,
                    schema_shortname=schema_shortname,
                    meta=meta,
                    body=body,
                    db_row=row,
                    lookup=lookup,
                )
                if modified.get('ignore'):
                    continue
                meta = modified["meta"]
                body = modified["body"]
                space_name = modified["space_name"]
                subpath = modified["subpath"]
                resource_type = modified["resource_type"]
                if modified.get('history_obj'):
                    history_obj = modified["history_obj"]

            if not meta.get('owner_shortname'):
                meta['owner_shortname'] = 'dmart'

            creator.save(
                space_name=space_name,
                subpath=subpath,
                class_type=resource_type,
                schema_shortname=schema_shortname,
                meta=meta,
                body=body,
                history_obj=history_obj,
                only_matched_schema=only_matched_schema,
                appended_list=appended_list,
                disable_duplication_appended_list=disable_duplication_appended_list
            )
        print(f'Executed in {"{:.2f}".format(time.time() - sub_before_time)} sec')
        offset += db_result['returned']

        if offset > settings.max_records and settings.max_records != -1:
            break
        if db_result['returned'] != settings.fetch_limit:
            break
    print(f'total time: {"{:.2f}".format(time.time() - before_time)} sec')


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


def msisdn_fixer(msisdn: str):
    if not msisdn:
        return None
    if msisdn.startswith('964'):
        msisdn = msisdn[3:]
    if msisdn.startswith('07'):
        msisdn = msisdn[1:]
    if re.match(MSISDN_REGEX, msisdn):
        return msisdn
    return None

