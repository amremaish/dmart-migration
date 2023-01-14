from creator import creator
from dmart.enums import UserType
from dmart.helper import to_float, governorates_mapper
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer


@process_mapper(
    mapper="pos_users",
    appended_list=["body.address.governorate_shortnames"],
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
        lookup: dict
):
    meta = meta_fixer(meta)
    meta['shortname'] = f"pos_{meta['shortname']}"
    meta['type'] = UserType.mobile

    if not body.get('language'):
        body['language'] = ''

    if not body.get('registration_id'):
        body['registration_id'] = ''

    if not body.get('sim_iccid'):
        body['sim_iccid'] = ''

    if not body.get('device_serial'):
        body['device_serial'] = ''

    if not body.get('device_id'):
        body['device_id'] = ''

    if not body.get('language'):
        body['language'] = 'english'
    else:
        body['language'] = body.get('language').lower()
    if not body.get('address'):
        body['address'] = {'line': '', 'longitude': 0, 'latitude': 0, 'governorate_shortnames': []}
    else:
        if not body['address']['longitude']:
            body['address']['longitude'] = 0
        else:
            body['address']['longitude'] = to_float(body['address']['longitude'])

        if not body['address']['latitude']:
            body['address']['latitude'] = 0
        else:
            body['address']['latitude'] = to_float(body['address']['latitude'])

    if body.get('address').get('governorate_shortnames'):
        governorate = body.get('address').get('governorate_shortnames')
        governorate = None if len(governorate) == 0 else governorate[0]
        if governorate:
            governorate = governorates_mapper.get(creator.shortname_fixer(governorate))
            if governorate:
                body['address']['governorate_shortnames'] = [governorate]
            else:
                body['address']['governorate_shortnames'] = None
    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
