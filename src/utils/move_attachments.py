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
from dmart.helper import split_file_name


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


def apply_compare_date(from_date, to_date, folder_date):
    try:
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            folder_date = datetime.strptime(folder_date, '%Y-%m-%d')
            if to_date:
                to_date = datetime.strptime(to_date, '%Y-%m-%d')
                return from_date < folder_date < to_date

            return from_date < folder_date
    except:
        print(f"can't convert dates (empty is ok) {from_date} or {folder_date} or {to_date} to Y-m-d")

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


def save_attachment(space_name, subpath, entry_shortname, owner_shortname, file_path: Path):
    folder_path = (
            creator.spaces_path
            / space_name
            / subpath
            / '.dm'
            / str(entry_shortname)
    )
    if not folder_path.exists():
        print(f'WARRING: this "{folder_path}" entry folder does not exist.')
        return None

    name, ext, type = split_file_name(file_path.name)
    payload = Payload(
        content_type=type,
        checksum=generate_checksum(file_path),
        body=file_path.name,
    )
    attach = Attachment(shortname=name, owner_shortname=owner_shortname, payload=payload)
    attachment_path = folder_path / 'attachments.media'
    if not attachment_path.exists():
        os.makedirs(attachment_path)
    shutil.copyfile(file_path, attachment_path / file_path.name)
    with open(attachment_path / f'meta.{name}.json', 'w') as file:
        file.write(attach.json(exclude_none=True))


def move_contracts(folder_path, space_name, subpath, extra: dict):
    contracts_paths = []
    # load zip files
    for _, dirs, _ in os.walk(folder_path):
        # loop into dates
        for dir in dirs:
            if not apply_compare_date(extra.get('from_date'), extra.get('to_date'), dir):
                continue
            for _, _, files in os.walk(f'{folder_path}/{dir}'):
                # loop into zip files
                for file in files:
                    if file.endswith(".zip"):
                        shortname, owner_shortname = extract_shortname_file_name(file)
                        if shortname:
                            contracts_paths.append(
                                {
                                    'shortname': shortname,
                                    'owner_shortname': owner_shortname,
                                    'path': f'{folder_path}/{dir}/{file}'
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

