import re

from creator import creator
from dmart.helper import to_int, governorates_mapper, ICCID_REGEX
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, callback_fixer, msisdn_fixer


@process_mapper(mapper="b2b_contracts", remove_null_field=True)
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

    body['ticket_locator']['shortname'] = str(body['ticket_locator']['shortname'])

    if meta.get('state'):
        if meta.get('state') == 'PENDING':
            meta['state'] = 'pending'
        elif meta.get('state') == 'INCOMPLETE':
            meta['state'] = 'failed'
        elif meta.get('state') == 'UPLOADED':
            meta['state'] = 'uploaded'

    if body.get('ticket_locator'):
        body['ticket_locator']['subpath'] = 'tickets/b2b'

    msisdn = msisdn_fixer(body.get('msisdn'))
    if msisdn:
        body['msisdn'] = str(msisdn)

    # fix customer_type
    if body.get('customer_type') in lookup:
        body['customer_type'] = lookup[body.get('customer_type')].get('NAME_EN').lower().replace(' ', '_')

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
    if body.get('address', {}).get('governorate_shortname'):
        governorate = body.get('address', {}).get('governorate_shortname')
        if governorate:
            governorate = governorates_mapper.get(creator.shortname_fixer(governorate))
            if governorate:
                if governorate == 'baghdad':
                    governorate = 'baghdad_karkh'
                body['address']['governorate_shortname'] = governorate
            else:
                body['address']['governorate_shortname'] = None
    # fix governorate_shortname
    if body.get('id_page_no'):
        body['id_page_no'] = to_int(body.get('id_page_no'))

    if body.get('iccid') and not re.match(ICCID_REGEX, body.get('iccid')):
        del body['iccid']

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
