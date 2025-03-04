from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, callback_fixer, msisdn_fixer


@process_mapper(mapper="user_admins", remove_null_field=True)
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
    meta['shortname'] = f"admin_{meta['shortname']}"
    dprt = body.get('department')
    if not dprt:
        body['department'] = "others"
    else:
        if dprt == 'B.O' or dprt == 'BO' or dprt == 'Back office Team' \
                or dprt == 'Backoffice' or dprt == 'Back office'.strip():
            body['department'] = "backoffice"
        elif 'Sales' in dprt:
            body['department'] = "sales"
        elif dprt == 'Technical Support':
            body['department'] = "technical_support"
        else:
            body['department'] = "others"

    if meta.get('msisdn'):
        meta['msisdn'] = msisdn_fixer(meta.get('msisdn'))

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body
    }
