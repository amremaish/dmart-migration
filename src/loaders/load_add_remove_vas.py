from datetime import datetime

from creator import creator
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, callback_fixer, msisdn_fixer


@process_mapper(
    mapper="add_remove_vas",
    appended_list=['body.service_short_codes'],
    disable_duplication_appended_list=True,
    remove_null_field=True
)
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
        lookup: dict,
):
    meta = meta_fixer(meta)

    meta['workflow_shortname'] = 'add_remove_vas'

    # resolution_reason fixer
    if meta.get('resolution_reason'):
        meta['resolution_reason'] = creator.reason_fixer(meta['resolution_reason'])

    if meta.get('state'):
        if meta.get('state') == 'Pending':
            meta['state'] = 'pending'
        elif meta.get('state') == 'Rejected':
            meta['state'] = 'rejected'
        elif meta.get('state') == 'Approved':
            meta['state'] = 'approved'
        else:
            meta['state'] = ''
    service_short_codes = body.get('service_short_codes')
    if len(service_short_codes) > 0 and service_short_codes[0] is None:
        body['service_short_codes'] = []

    if body.get('msisdn'):
        body['msisdn'] = msisdn_fixer(body.get('msisdn'))

    if body.get('call_back_number'):
        body['call_back_number'] = callback_fixer(body.get('call_back_number'))

    if body.get('service_short_code'):
        body['service_short_code'] = body['service_short_code'].split(',')

    if body.get('service_type') and body.get('service_type') in lookup:
        body['service_type'] = lookup[body.get('service_type')].get('KEY_VALUE').lower()
    else:
        del body['service_type']

    if body.get('sub_service_type') and body.get('sub_service_type') in lookup:
        body['sub_service_type'] = lookup[body.get('sub_service_type')].get('KEY_VALUE').lower()
    else:
        del body['sub_service_type']

    if body.get('msisdn') and body.get('msisdn').startswith('964'):
        body['msisdn'] = body.get('msisdn')[3:]

    history_obj = None
    start = db_manager.create_alias('OTHER_SERVICE.ACTION_START_TIME')
    end = db_manager.create_alias('OTHER_SERVICE.ACTION_END_TIME')
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
