from creator import creator
from dmart.helper import to_int
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, msisdn_fixer


@process_mapper(mapper="information_service_customers", remove_null_field=True)
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
    ignore = False
    meta = meta_fixer(meta)
    msisdn = msisdn_fixer(body.get('msisdn'))
    if msisdn:
        body['msisdn'] = str(msisdn)
        meta['shortname'] = str(msisdn)
    else:
        ignore = True

    # fix customer_type
    if body.get('customer_type') in lookup:
        body['customer_type'] = lookup[body.get('customer_type')].get('NAME_EN').lower()

    # fix gender
    if body.get('gender') == 'M':
        body['gender'] = 'male'
    elif body.get('gender') == 'F':
        body['gender'] = 'female'

    # nationality
    if body.get('nationality') in lookup:
        body['nationality'] = lookup[body.get('nationality')].get('NAME_EN')

    # governorate_shortname
    if body.get('address', {}).get('governorate_shortname') in lookup:
        body['address']['governorate_shortname'] = creator.shortname_fixer(
            lookup[body['address']['governorate_shortname']].get('NAME_EN'))

    # fix governorate_shortname
    if body.get('id_page_no'):
        body['id_page_no'] = to_int(body.get('id_page_no'))

    # fix residence_number
    if body.get('residence_number'):
        body['residence_number'] = to_int(body.get('residence_number'))

    if not body.get('gender') and not body.get('address', {}).get('line'):
        ignore = True

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body,
        'ignore': ignore
    }
