from datetime import datetime

from utils.decorators import process_mapper
from utils.default_loader import default_loader


@process_mapper(
    mapper="pos_channels_type",
    appended_list=["body.type"]
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
        db_row: dict
):
    if not meta.get('updated_at'):
        meta['updated_at'] = datetime.now().isoformat()
    if not meta.get('created_at'):
        meta['created_at'] = datetime.now().isoformat()

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
