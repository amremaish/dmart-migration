from creator import creator
from dmart.helper import governorates_mapper
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer


@process_mapper(
    mapper="distributor_users",
    appended_list=["body.governorate_shortnames"],
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
    meta['shortname'] = f"dist_user_{meta['shortname']}"
    if body.get('language'):
        body['language'] = str(body['language'])

    if not body.get('registration_id'):
        body['registration_id'] = ''

    if not body.get('address'):
        body['address'] = {'longitude': 0, 'latitude': 0, }

    if body.get('governorate_shortnames'):
        governorate = body.get('governorate_shortnames')
        governorate = None if len(governorate) == 0 else governorate[0]
        if governorate:
            governorate = governorates_mapper.get(creator.shortname_fixer(governorate))
            if governorate:
                body['governorate_shortnames'] = [governorate]

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
