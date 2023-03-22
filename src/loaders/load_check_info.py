from datetime import datetime

from creator import creator
from dmart.helper import governorates_mapper
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, callback_fixer, msisdn_fixer


@process_mapper(mapper="check_info", remove_null_field=True)
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
        db_row: dict,
        lookup: dict
):
    meta = meta_fixer(meta)

    meta['workflow_shortname'] = 'check_info'
    if meta.get('state'):
        if meta.get('state') == 'DELIVERED':
            meta['state'] = 'delivered'
        elif meta.get('state') == 'Assigned to driver':
            meta['state'] = 'assigned_to_driver'
        elif meta.get('state') == 'Pending':
            meta['state'] = 'pending'
        elif meta.get('state') == 'Rejected' or meta.get('state') == 'Rejected validation':
            meta['state'] = 'rejected'
        elif meta.get('state') == 'Approved' or meta.get('state') == 'Approved validation':
            meta['state'] = 'approved'
        elif meta.get('state') == 'Completed':
            meta['state'] = 'completed'
        elif meta.get('state') == 'Canceled':
            meta['state'] = 'cancelled'
        else:
            meta['state'] = ''

    # resolution_reason fixer
    if meta.get('resolution_reason'):
        meta['resolution_reason'] = creator.reason_fixer(meta['resolution_reason'])


    if body.get('msisdn'):
        body['msisdn'] = msisdn_fixer(body.get('msisdn'))

    if body.get('call_back_number'):
        body['call_back_number'] = callback_fixer(body.get('call_back_number'))

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
