from datetime import datetime

from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer


@process_mapper(mapper="change_ownership_two", remove_null_field=True)
def load(*args, **kwargs):
    default_loader(args, kwargs, apply_modifier)
    print("Successfully done.")


def apply_modifier(
        space_name: str,
        subpath: str,
        resource_type: str,
        schema_shortname: str,
        meta: dict,
        body: dict,
        db_row: dict
):
    meta = meta_fixer(meta)
    meta['workflow_shortname'] = 'change_ownership'
    if meta.get('state'):
        if meta.get('state') == 'Pending':
            meta['state'] = 'pending'
        elif meta.get('state') == 'Completed':
            meta['state'] = 'completed'
        elif meta.get('state') == 'Rejected':
            meta['state'] = 'rejected'
        elif meta.get('state') == 'Approved':
            meta['state'] = 'approved'
        else:
            meta['state'] = ''

    if meta.get('owner_shortname'):
        meta['owner_shortname'] = f'pos_{meta["owner_shortname"]}'

    if body.get('msisdn') and body.get('msisdn').startswith('964'):
        body['msisdn'] = body.get('msisdn')[3:]

    history_obj = None
    start = db_manager.create_alias('SIM_SWAP.ACTION_START_TIME')
    end = db_manager.create_alias('SIM_SWAP.ACTION_END_TIME')
    if db_row.get(start) and db_row.get(end):
        start = datetime.strptime(db_row.get(start), '%Y/%m/%d %H:%M:%S'),
        end = datetime.strptime(db_row.get(end), '%Y/%m/%d %H:%M:%S'),
        history_obj = [
            {"history_diff": {"lock_type": {"old": "null", "new": "lock"}}, "timestamp": start},
            {"history_diff": {"lock_type": {"old": "null", "new": "unlock"}}, "timestamp": end}
        ]

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body,
        "history_obj": history_obj,
    }
