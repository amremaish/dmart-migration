from creator import creator
from dmart.helper import governorates_mapper
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer


@process_mapper(
    mapper="products",
    appended_list=["body.governorate_shortnames", "body.role_shortnames"],
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
        lookup: dict
):
    meta = meta_fixer(meta)

    if body.get('governorate_shortnames'):
        governorate = body.get('governorate_shortnames')
        governorate = None if len(governorate) == 0 else governorate[0]
        if governorate:
            governorate = governorates_mapper.get(creator.shortname_fixer(governorate))
            if governorate:
                if governorate == 'baghdad':
                    body['governorate_shortnames'] = ['baghdad_karkh', 'baghdad_rasafa']
                else:
                    body['governorate_shortnames'] = [governorate]
            else:
                body['governorate_shortnames'] = None

    if body.get('role_shortnames'):
        role = body.get('role_shortnames')
        role = None if len(role) == 0 else role[0]
        if role:
            if role == 'fs':
                body['role_shortnames'] = ['franshise']
            elif role == 'supermarket':
                body['role_shortnames'] = ['voucher_pos']
            elif role == 'ros':
                body['role_shortnames'] = ['ros']
            elif role == 'pos':
                body['role_shortnames'] = ['activating_pos']
            elif role == 'zain_light':
                body['role_shortnames'] = ['zain_lite']
            else:
                del body['role_shortnames']

    sub_cat = db_row.get(db_manager.create_alias('SUB_CATEGORY.SUB_CATEGORY_NAME'))
    cat = db_row.get(db_manager.create_alias('CATEGORY.CATEGORY_NAME'))
    subpath = f'products/{creator.shortname_fixer(cat)}/{creator.shortname_fixer(sub_cat)}'
    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
