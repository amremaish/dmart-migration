import re

from creator import creator
from dmart.helper import governorates_mapper, ID_RECORD_NUMBER_REGEX, ICCID_REGEX
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, callback_fixer, msisdn_fixer


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

    if meta.get('owner_shortname'):
        meta['owner_shortname'] = f"pos_{meta['owner_shortname']}"

    if meta.get('state'):
        if meta.get('state') == 'PENDING':
            meta['state'] = 'pending'
        elif meta.get('state') == 'INCOMPLETE':
            meta['state'] = 'failed'
        elif meta.get('state') == 'UPLOADED':
            meta['state'] = 'uploaded'

    if body.get('msisdn'):
        body['msisdn'] = msisdn_fixer(body.get('msisdn'))

    if body.get('company_data', {}).get('contract_type'):
        val = lookup.get(body['company_data']['contract_type'], {}).get('KEY_VALUE', None)
        if val == 'PRE-PAID':
            body['company_data']['contract_type'] = 'prepaid'
        else:
            body['company_data']['contract_type'] = 'postpaid'

    if body.get('authorized_details', {}).get('nationality'):
        nationality = body.get('authorized_details', {}).get('nationality')
        if nationality:
            body['authorized_details']['nationality'] = lookup.get(nationality, {}).get('NAME_EN', None)

    if body.get('authorized_details', {}).get('governorate_shortname'):
        governorate = body.get('authorized_details', {}).get('governorate_shortname')
        if governorate:
            governorate = governorates_mapper.get(creator.shortname_fixer(governorate), None)
            if governorate == 'baghdad':
                governorate = 'baghdad_karkh'
            body['authorized_details']['governorate_shortname'] = governorate

    if body.get('company_details', {}).get('company_governorate_shortname'):
        governorate = body.get('company_details', {}).get('company_governorate_shortname')
        if governorate:
            governorate = governorates_mapper.get(creator.shortname_fixer(governorate), None)
            if governorate == 'baghdad':
                governorate = 'baghdad_karkh'
            body['company_details']['company_governorate_shortname'] = governorate

    id_record_number = body.get('authorized_details', {}).get('id_record_number')
    id_page_number = body.get('authorized_details', {}).get('id_page_number')

    if not id_record_number or not re.match(ID_RECORD_NUMBER_REGEX, id_record_number):
        del body['authorized_details']['id_record_number']

    if not id_page_number or not re.match(ID_RECORD_NUMBER_REGEX, id_page_number):
        del body['authorized_details']['id_page_number']

    if len(body.get('customer_details', [])) > 0:
        if body['customer_details'][0].get('iccid') and\
                not re.match(ICCID_REGEX, body['customer_details'][0].get('iccid')):
            del body['customer_details'][0]['iccid']

        if body['customer_details'][0].get('msisdn'):
            body['customer_details'][0]['msisdn'] = callback_fixer(body['customer_details'][0].get('msisdn'))

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
