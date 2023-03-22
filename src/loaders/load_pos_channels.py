from creator import creator
from dmart.helper import governorates_mapper
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer


@process_mapper(mapper="pos_channels", remove_null_field=True)
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
    ignore = False
    if not meta.get('shortname'):
        ignore = True

    if body["type"] == '':
        body["type"] = 0
    body["type"] = str(body["type"])

    if body.get('location', {}).get('governorate', {}).get('shortname'):
        governorate = body.get('location', {}).get('governorate', {}).get('shortname')
        if governorate:
            governorate = governorates_mapper.get(creator.shortname_fixer(governorate))
            if governorate:
                if governorate == 'baghdad':
                    governorate = 'baghdad_karkh'
                body['location']['governorate']['shortname'] = governorate
            else:
                body['location']['governorate']['shortname'] = None
    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body,
        "ignore": ignore
    }
