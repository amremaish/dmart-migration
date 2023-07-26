import json
import os
import re
from pathlib import Path

import settings
from creator import creator
from dmart.enums import UserType
from dmart.helper import to_float, governorates_mapper, ICCID_REGEX
from utils.db import db_manager
from utils.decorators import process_mapper
from utils.default_loader import default_loader, meta_fixer, callback_fixer, msisdn_fixer


@process_mapper(
    mapper="pos_users",
    remove_null_field=True
)
def load(*args, **kwargs):
    load_channels()
    default_loader(args, kwargs, apply_modifier)
    print("Successfully done.")


# contains key => channel name, value => (uuid) shortname
channels: dict = {}


def load_channels():
    print("loading channels ...")
    path = creator.spaces_path / "management/collections/channels/.dm"
    for entry in os.scandir(path):
        if entry.is_dir():
            with open(Path(path / entry.name / "meta.content.json"), "r") as json_file:
                meta = json.load(json_file)
                channels[meta.get('displayname', {}).get('ar')] = meta.get('shortname')


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

    meta['type'] = UserType.mobile

    if body.get('sim_iccid') is not None and not re.match(ICCID_REGEX, body.get('sim_iccid')):
        del body['sim_iccid']

    if not body.get('address'):
        body['address'] = {'line': '', 'longitude': 0, 'latitude': 0, 'governorate_shortnames': []}
    else:
        if not body['address']['longitude']:
            body['address']['longitude'] = 0
        else:
            body['address']['longitude'] = to_float(body['address']['longitude'])

        if not body['address']['latitude']:
            body['address']['latitude'] = 0
        else:
            body['address']['latitude'] = to_float(body['address']['latitude'])

    if body.get('address', {}).get('governorate', {}).get('shortname'):
        governorate = body.get('address', ).get('governorate').get('shortname')
        if governorate:
            governorate = governorates_mapper.get(creator.shortname_fixer(governorate))
            if governorate:
                if governorate == 'baghdad':
                    body['address']['governorate']['shortnames'] = 'baghdad_karkh'
                else:
                    body['address']['governorate']['shortnames'] = governorate
            else:
                body['address']['governorate']['shortnames'] = None

    if meta.get('msisdn'):
        meta['msisdn'] = msisdn_fixer(meta.get('msisdn'))

    # add roles
    role = db_row.get(db_manager.create_alias('USER_TYPE.NAME'))
    role = role.lower() if role else ""
    if role == 'fs' or role == 'franshise':
        meta['roles'] = ['franchise', "rc_compensation", "change_ownership", "sim_swap", "migration", "order",
                         "contract"]
    elif role == 'supermarket':
        meta['roles'] = ['voucher_pos', "connect_disconnect", "migration", "correct_info", "rc_compensation",
                         "dummy", "postpaid_prime", "change_ownership", "contract", "sim_swap", "add_remove_vas",
                         "order"]
    elif role == 'ros':
        meta['roles'] = ['ros', "connect_disconnect", "migration", "correct_info", "rc_compensation", "dummy",
                         "postpaid_prime", "change_ownership", "sim_swap", "add_remove_vas"]
    elif role == 'pos':
        meta['roles'] = ['activating_pos', "connect_disconnect", "migration", "correct_info", "rc_compensation",
                         "dummy", "postpaid_prime", "change_ownership", "sim_swap", "add_remove_vas", "contract"]
    elif role == 'zain_light':
        meta['roles'] = ['zain_lite', "sim_swap", "order"]

    # set channel shortname
    if body.get('channel_shortname'):
        channel = channels.get(body.get('channel_shortname', ''))
        if channel:
            body['channel_shortname'] = channel[0]

    return {
        "space_name": space_name,
        "subpath": subpath,
        "resource_type": resource_type,
        "schema_shortname": schema_shortname,
        "meta": meta,
        "body": body,
        "ignore": ignore
    }
