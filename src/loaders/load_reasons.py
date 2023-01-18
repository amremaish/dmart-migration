from creator import creator
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, msisdn_fixer


@process_mapper(
    mapper="reasons",
    appended_list=['body.resolutions'],
    remove_null_field=True)
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
    if body.get('resolutions') and len(body.get('resolutions')) > 0:
        body['resolutions'][0]['key'] = creator.reason_fixer(body['resolutions'][0]['key'])
    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
