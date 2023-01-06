from creator import creator
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer


@process_mapper(
    mapper="products",
    appended_list=["body.governorate_shortnames", "body.role_shortnames"],
    disable_duplication_appended_list=True
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

    cat = db_row.get(db_manager.create_alias('SUB_CATEGORY.SUB_CATEGORY_NAME'))
    sub_cat = db_row.get(db_manager.create_alias('CATEGORY.CATEGORY_NAME'))
    subpath = f'ordering/products/{creator.shortname_fixer(cat)}/{creator.shortname_fixer(sub_cat)}'
    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
