import re
from datetime import datetime

from creator import creator
from dmart.helper import ICCID_REGEX
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, callback_fixer, msisdn_fixer


@process_mapper(mapper="change_ownership_one", remove_null_field=True)
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

    # resolution_reason fixer
    if meta.get('resolution_reason'):
        meta['resolution_reason'] = creator.reason_fixer(meta['resolution_reason'])

    if body.get('msisdn'):
        body['msisdn'] = msisdn_fixer(body.get('msisdn'))

    if body.get('call_back_number'):
        body['call_back_number'] = callback_fixer(body.get('call_back_number'))

    if body.get('iccid') and not re.match(ICCID_REGEX, body.get('iccid')):
        del body['iccid']

    if body.get('frequently_called_numbers'):
        frequently_called_numbers = body.get('frequently_called_numbers')
        frequently_called_numbers = frequently_called_numbers[1:]
        frequently_called_numbers = frequently_called_numbers[:-1]
        frequently_called_numbers = frequently_called_numbers.replace(' ', '')
        frequently_called_numbers = frequently_called_numbers.split(',')
        fixed_number = []
        for number in frequently_called_numbers[:10]:
            fixed = callback_fixer(number)
            if fixed and fixed not in fixed_number:
                fixed_number.append(fixed)
        body['frequently_called_numbers'] = None if len(fixed_number) == 0 else fixed_number

    if body.get('contract_shortname'):
        body['contract_shortname'] = str(body['contract_shortname'])

    request_type = db_row.get(db_manager.create_alias('INFORMATION_SERVICE.REQUEST_TYPE'))
    if request_type and request_type == 'Check-Info':
        del body['contract_shortname']
    history_obj = None
    start = db_manager.create_alias('INFORMATION_SERVICE.ACTION_START_TIME')
    end = db_manager.create_alias('INFORMATION_SERVICE.ACTION_END_TIME')
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
