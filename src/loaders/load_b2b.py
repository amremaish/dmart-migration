from datetime import datetime

from creator import creator
from dmart.helper import governorates_mapper
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, msisdn_fixer


@process_mapper(mapper="b2b", remove_null_field=True)
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

    if meta.get('state'):
        if meta.get('state') == 'PENDING':
            meta['state'] = 'pending'
        elif meta.get('state') == 'INCOMPLETE':
            meta['state'] = 'failed'
        elif meta.get('state') == 'UPLOADED':
            meta['state'] = 'pending'

    if body.get('msisdn'):
        body['msisdn'] = msisdn_fixer(body.get('msisdn'))

    if body.get('contract_type'):
        val = lookup.get(body['contract_type'], {}).get('KEY_VALUE', None)
        if val == 'PRE-PAID':
            body['contract_type'] = 'prepaid'
        else:
            body['contract_type'] = 'postpaid'

    if body.get('governorate_shortname'):
        governorate = body.get('governorate_shortname')
        if governorate:
            governorate = governorates_mapper.get(creator.shortname_fixer(governorate))
            if governorate:
                body['governorate_shortname'] = governorate
            else:
                body['governorate_shortname'] = None

    if body.get('company_governorate_shortname'):
        governorate = body.get('company_governorate_shortname')
        if governorate:
            governorate = governorates_mapper.get(creator.shortname_fixer(governorate))
            if governorate:
                body['company_governorate_shortname'] = governorate
            else:
                body['company_governorate_shortname'] = None

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
