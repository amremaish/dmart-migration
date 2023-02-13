import hashlib
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from creator import creator
from dmart.core import Attachment, Payload
from dmart.helper import split_file_name, to_int
from utils.db import db_manager


def load_mover(mover: str):
    movers = 'movers'
    if Path(movers).absolute().exists():
        movers = Path(movers).absolute()
    elif Path('../' + movers).absolute():
        movers = Path('../' + movers).absolute()
    else:
        return -1
    path = movers / 'movers.json'
    if not path.exists():
        raise Exception("movers.json file doesn't exist.")
    mover_obj: dict = json.loads(path.read_bytes())
    if not mover_obj.get(mover):
        raise Exception(f"movers object '{mover}' doesn't exist.")
    if not mover_obj.get(mover).get('folder_path') or not mover_obj.get(mover).get('space_name') or not mover_obj.get(
            mover).get('subpath'):
        raise Exception(f"missing information in mover obj.")
    return mover_obj.get(mover)


def move_attachments(loader: str):
    mover: dict = load_mover(loader)
    func = getattr(sys.modules[__name__], f'move_{loader}')
    func(mover.get('folder_path'), mover.get('space_name'), mover.get('subpath'), mover.get('extra'))
    print("Successfully done.")


def apply_compare_date(from_date, to_date, folder_date, format: str = None):
    if not format:
        format = '%Y-%m-%d'
    try:
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            folder_date = datetime.strptime(folder_date, format)
            if to_date:
                to_date = datetime.strptime(to_date, '%Y-%m-%d')
                return from_date < folder_date < to_date

            return from_date < folder_date
    except:
        print(f"can't convert dates {from_date} or {folder_date} or {to_date} to Y-m-d")

    return False


def extract_shortname_file_name(file_name):
    # CMMC7971000055007230125_120601.zip -> 000055007, MMC797
    try:
        return int(file_name[:-17][-9:]), file_name[1:6]
    except:
        return 0, 0


def generate_checksum(file_path):
    with open(file_path, 'rb') as file:
        sha1 = hashlib.sha1()
        sha1.update(file.read())
        checksum = sha1.hexdigest()
        file.seek(0)
        return checksum


def fix_attachment_name(file_name):
    name, ext, type = split_file_name(file_name)
    if 'SECOND_FINGERPRINT' in file_name:
        name = 'second_fingerprint'
    elif 'SECOND_SIGNATURE' in file_name:
        name = 'second_signature'
    elif 'SECOND_CUST_PHOTO' in file_name:
        name = 'second_live_photo'
    elif 'FINGERPRINT' in file_name:
        name = 'fingerprint'
    elif 'SIGNATURE' in file_name:
        name = 'signature'
    elif 'CUST_PHOTO' in file_name:
        name = 'live_photo'
    else:
        name = file_name
    return name, ext, type


def save_attachment(space_name, subpath, entry_shortname, owner_shortname, file_path: Path):
    folder_path = (
            creator.spaces_path
            / space_name
            / subpath
            / '.dm'
            / str(entry_shortname)
    )
    if not folder_path.exists() or not entry_shortname:
        print(f'WARRING: this "{folder_path}" entry folder does not exist.')
        return None

    name, ext, type = fix_attachment_name(file_path.name)
    payload = Payload(
        content_type=type,
        checksum=generate_checksum(file_path),
        body=f'{name}.{ext}',
    )
    owner_shortname = creator.shortname_fixer(owner_shortname)
    attach = Attachment(shortname=name, owner_shortname=owner_shortname, payload=payload)
    attachment_path = folder_path / 'attachments.media'
    if not attachment_path.exists():
        os.makedirs(attachment_path)
    shutil.copyfile(file_path, attachment_path / f'{name}.{ext}')
    with open(attachment_path / f'meta.{name}.json', 'w') as file:
        file.write(attach.json(exclude_none=True))


def find_pos_shortname(pos_id):
    try:
        db_result = db_manager.select_query(
            table_name="POS_USER",
            columns=['ID', 'POS_ID'],
            where=f"ID = '{str(to_int(pos_id))}'",
            limit=1,
            offset=0)
        if db_result.get('total') > 0:
            return db_result.get('data')[0].get('POS_ID')
    except:
        pass
    return ''


def find_sim_swap_id(contract_name):
    try:
        db_result = db_manager.select_query(
            table_name="SIM_SWAP",
            columns=['ID', 'CONTRACT_NAME'],
            where=f"CONTRACT_NAME = '{contract_name}'",
            limit=1,
            offset=0)
        if db_result.get('total') > 0:
            return db_result.get('data')[0].get('ID')
    except:
        pass
    return ''


def move_contracts(folder_path, space_name, subpath, extra: dict):
    contracts_paths = []
    # load zip files
    for date_dir in os.scandir(folder_path):
        # loop into dates
        if not apply_compare_date(extra.get('from_date'), extra.get('to_date'), date_dir.name):
            continue
        for pos_dir in os.scandir(date_dir.path):
            for file in os.scandir(pos_dir.path):
                # loop into zip files
                if file.name.endswith(".zip"):
                    shortname, owner_shortname = extract_shortname_file_name(file.name)
                    if shortname:
                        contracts_paths.append(
                            {
                                'shortname': shortname,
                                'owner_shortname': pos_dir.name,
                                'path': file.path
                            }
                        )

    for contract in contracts_paths:
        shortname = contract.get('shortname')
        owner_shortname = contract.get('owner_shortname')
        path = Path(contract.get('path'))
        with zipfile.ZipFile(path, 'r') as zf:
            tmp_folder = f'{str(path.parent)}/tmp'
            zf.extractall(tmp_folder)
            files: list[zipfile.ZipInfo] = zf.filelist
            for file in files:
                save_attachment(space_name, subpath, shortname, owner_shortname, Path(f'{tmp_folder}/{file.filename}'))
            shutil.rmtree(tmp_folder)


def move_sim_swap(folder_path, space_name, subpath, extra: dict):
    contracts_paths = []
    for date_dir in os.scandir(folder_path):
        # loop into dates
        if not apply_compare_date(extra.get('from_date'), extra.get('to_date'), date_dir.name, '%y%m%d'):
            continue
        for pos_dir in os.scandir(date_dir.path):
            for contract_dir in os.scandir(pos_dir.path):
                contracts_paths.append(
                    {
                        'shortname': contract_dir.name,
                        'owner_shortname': pos_dir.name,
                        'path': contract_dir.path
                    }
                )

    for contract in contracts_paths:
        owner_shortname = find_pos_shortname(contract.get('owner_shortname'))
        if not owner_shortname:
            owner_shortname = 'dmart'
        shortname = find_sim_swap_id(contract.get('shortname'))
        for file in os.scandir(contract.get('path')):
            save_attachment(space_name, subpath, shortname, owner_shortname, Path(file.path))
