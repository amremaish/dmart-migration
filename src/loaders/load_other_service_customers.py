from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, msisdn_fixer


@process_mapper(mapper="other_service_customers", remove_null_field=True)
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
    ignore = False
    meta = meta_fixer(meta)
    msisdn = msisdn_fixer(body.get('msisdn'))
    if msisdn:
        body['msisdn'] = str(msisdn)
        meta['shortname'] = str(msisdn)
    else:
        ignore = True

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body,
        'ignore': ignore
    }
