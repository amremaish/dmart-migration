from uuid import uuid4

from creator import creator
from dmart.helper import governorates_mapper
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer


@process_mapper(mapper="pos_channels", remove_null_field=True)
def load(*args, **kwargs):
    default_loader(args, kwargs, apply_modifier)
    print("Successfully done.")


# contains key => channel name, value => [(uuid) shortname, address]
channels: dict = {}


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
    # check channel if exists
    if meta.get('displayname', {}).get('ar'):
        name = meta['displayname']["ar"]
        if not channels.get(name):
            uuid = str(uuid4())
            shortname = uuid[:8]
            meta['shortname'] = shortname
            meta['uuid'] = uuid
            channels[name] = [shortname, body.get('location', {}).get('line')]
        elif channels[name] and channels[name][1] and body.get('location', {}).get('line'):
            # if channels exists but has a valid value then replace it
            channels[name][1] = body.get('location', {}).get('line')
            meta['shortname'] = channels[name][0]
        else:
            ignore = True

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

    if body.get('type'):
        role = body.get('type')
        role = role.lower() if role else ""
        if role:
            if role == 'fs' or role == 'franshise':
                body['type'] = 'franchise'
            elif role == 'supermarket':
                body['type'] = 'voucher_pos'
            elif role == 'ros':
                body['type'] = 'ros'
            elif role == 'pos':
                body['type'] = 'activating_pos'
            elif role == 'zain_light':
                body['type'] = 'zain_lite'
            else:
                del body['type']

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body,
        "ignore": ignore
    }
