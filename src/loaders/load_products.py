from creator import creator
from dmart.helper import governorates_mapper
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, create_meta_folder


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
            if role == 'fs' or role == 'franshise':
                body['role_shortnames'] = ['franchise']
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

    cat_en = db_row.get(db_manager.create_alias('CATEGORY.CATEGORY_NAME'))
    cat_ar = db_row.get(db_manager.create_alias('CATEGORY.NAME_AR'))
    cat_kd = db_row.get(db_manager.create_alias('CATEGORY.NAME_KU'))
    displayname = {'en': cat_en, 'ar': cat_ar, 'kd': cat_kd}
    create_meta_folder(
        space_name=space_name,
        subpath=f'products/{creator.shortname_fixer(cat_en)}',
        shortname=creator.shortname_fixer(cat_en),
        displayname=displayname
    )
    sub_cat_en = db_row.get(db_manager.create_alias('SUB_CATEGORY.SUB_CATEGORY_NAME'))
    sub_cat_ar = db_row.get(db_manager.create_alias('SUB_CATEGORY.NAME_AR'))
    sub_cat_kd = db_row.get(db_manager.create_alias('SUB_CATEGORY.NAME_KU'))
    subpath = f'products/{creator.shortname_fixer(cat_en)}/{creator.shortname_fixer(sub_cat_en)}'
    displayname = {'en': sub_cat_en, 'ar': sub_cat_ar, 'kd': sub_cat_kd}
    create_meta_folder(
        space_name=space_name,
        subpath=subpath,
        shortname=creator.shortname_fixer(sub_cat_en),
        displayname=displayname
    )
    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
