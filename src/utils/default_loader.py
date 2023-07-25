import os
import re
import time
from datetime import datetime
from multiprocessing import Process
from uuid import uuid4
from creator import creator
from dmart.core import Meta, Payload
from dmart.enums import ContentType
from dmart.helper import MSISDN_REGEX, governorates_mapper, CALLBACK_REGEX
from settings import settings
from utils.db import db_manager


def default_loader(args, kwargs, apply_modifier=None):
    # comes from process_mapper decorator

    offset: int = 0
    before_time = time.time()
    # load all lockup table
    lookup: dict = db_manager.load_lookup()
    while True:
        processes: list[Process] = []
        is_done = False
        for _ in range(8):
            process = Process(target=execute, args=(kwargs, apply_modifier, offset, lookup))
            process.start()
            processes.append(process)
            offset += settings.fetch_limit
            if offset > settings.max_records and settings.max_records != -1:
                break

        for p in processes:
            p.join()
            is_done |= p.exitcode

        if offset > settings.max_records and settings.max_records != -1:
            break

        if is_done:
            break
    print(f'total time: {"{:.2f}".format(time.time() - before_time)} sec')


def execute(kwargs, apply_modifier, offset, lookup):
    sub_before_time = time.time()
    mapper_data: dict = kwargs['mapper_data']
    remove_null_field: bool = kwargs['remove_null_field']
    only_matched_schema: bool = kwargs['only_matched_schema']
    appended_list: list = kwargs['appended_list']
    disable_duplication_appended_list: bool = kwargs['disable_duplication_appended_list']

    db_manager.refresh_connection()
    db_result = db_manager.select_query(
        table_name=mapper_data.get('source').get('table'),
        columns=mapper_data.get('source').get('columns'),
        join_tables=mapper_data.get('source').get('join'),
        where=mapper_data.get('source').get('where'),
        limit=settings.fetch_limit,
        offset=offset)

    if not db_result.get('data'):
        exit(True)

    for row in db_result.get('data'):
        space_name = mapper_data.get('dest').get('space_name')
        schema_shortname = mapper_data.get('dest').get('schema_shortname')
        subpath = mapper_data.get('dest').get('subpath')
        resource_type = mapper_data.get('dest').get('resource_type')
        history_obj = None

        meta, body = creator.convert_db_to_meta(row, mapper_data)
        creator.shortname_deep_fixer(meta)
        creator.shortname_deep_fixer(body)
        meta, body = fix_for_all(meta, body, lookup)
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

        if remove_null_field:
            # loop it for remove empty dict
            for i in range(3):
                meta = creator.delete_none(meta)
                body = creator.delete_none(body)

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
    exit(False)


def fix_for_all(meta: dict, body: dict, lookup: dict):
    if meta.get('collaborators', {}).get('processed_by'):
        meta['collaborators']['processed_by'] = creator.shortname_fixer(meta['collaborators']['processed_by'])
    else:
        if meta.get('collaborators', {}):
            del meta['collaborators']

    if meta.get('reporter', {}).get('governorate'):
        governorate = lookup[meta['reporter']['governorate']].get('NAME_EN')
        governorate = governorates_mapper.get(creator.shortname_fixer(governorate), None)
        if governorate == 'baghdad':
            governorate = 'baghdad_karkh'
        meta['reporter']['governorate'] = governorate
    return meta, body


def meta_fixer(meta: dict):
    meta = fix_reporter_type(meta)
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


def callback_fixer(msisdn: str):
    if not msisdn:
        return None
    if msisdn.startswith('964'):
        msisdn = msisdn[3:]
    elif msisdn.startswith('07'):
        msisdn = msisdn[1:]
    if re.match(CALLBACK_REGEX, msisdn):
        return msisdn
    return None


def msisdn_fixer(msisdn: str):
    if not msisdn:
        return None
    if msisdn.startswith('964'):
        msisdn = msisdn[3:]
    elif msisdn.startswith('07'):
        msisdn = msisdn[1:]
    if re.match(MSISDN_REGEX, msisdn):
        return msisdn
    return None


def fix_reporter_type(meta: dict):
    if meta.get('reporter', {}).get('msisdn'):
        meta['reporter']['msisdn'] = msisdn_fixer(meta['reporter']['msisdn'])
    if meta.get('reporter', {}).get('type'):
        role: str = meta.get('reporter', {}).get('type')
        if role:
            role = role.lower()
            if role == 'fs' or role == 'franshise':
                meta['reporter']['type'] = 'franchise'
            elif role == 'supermarket':
                meta['reporter']['type'] = 'voucher_pos'
            elif role == 'ros':
                meta['reporter']['type'] = 'ros'
            elif role == 'pos':
                meta['reporter']['type'] = 'activating_pos'
            elif role == 'zain_light':
                meta['reporter']['type'] = 'zain_lite'
            else:
                del meta['reporter']['type']
    return meta


def create_meta_folder(space_name: str, subpath: str, shortname: str, displayname: dict):
    path = creator.spaces_path / space_name / subpath / '.dm/meta.folder.json'
    directory = os.path.dirname(path)
    if path.is_file():
        return
    if not os.path.exists(directory):
        os.makedirs(directory)

    payload = Payload(content_type=ContentType.json, schema_shortname='folder_rendering', body=f'{shortname}.json')
    meta_obj = Meta(uuid=str(uuid4()), shortname=shortname, displayname=displayname, owner_shortname='dmart',
                    payload=payload)
    with open(path, "w") as f:
        f.write(meta_obj.json(exclude_none=True))
