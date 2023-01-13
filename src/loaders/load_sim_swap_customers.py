import re
from datetime import datetime

from dmart.helper import MSISDN_REGEX
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer


@process_mapper(mapper="sim_swap_customers", remove_null_field=True)
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

    if body.get('msisdn') and body.get('msisdn').startswith('964'):
        body['msisdn'] = body.get('msisdn')[3:]

    if body.get('msisdn') and not re.match(MSISDN_REGEX, body.get('msisdn')):
        ignore = True
    else:
        meta['shortname'] = str(body.get('msisdn'))

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body,
        'ignore': ignore
    }
