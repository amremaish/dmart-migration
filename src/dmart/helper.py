import re

from dmart.enums import ContentType

# regex
SUBPATH = r"^[\w\/]{1,64}$"
SHORTNAME = r"^\w{1,32}$"
FILENAME = re.compile(r"^\w{1,32}\.(gif|png|jpeg|jpg|pdf)$")
SPACENAME = r"^\w{1,32}$"
EXT = r"^(gif|png|jpeg|jpg|json|md|pdf)$"
IMG_EXT = r"^(gif|png|jpeg|jpg)$"
USERNAME = r"^\w{3,10}$"
# PASSWORD = r"^[\w._]{4,}$"
PASSWORD = r"^(?=.*\d)(?=.*[A-Z])[a-zA-Z\d]{8,24}$"
EMAIL = r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$"
META_DOC_ID = r"^\w*:\w*:meta:[\w\/]+$"
CALLBACK_REGEX = "^7[5789]\d{8}$"  # Exactly 10 digits, not starting with zero
MSISDN_REGEX = "7[89]\d{8}$"  # Exactly 10 digits, not starting with zero
ID_RECORD_NUMBER_REGEX = "^[a-zA-Z0-9؀-ۿ]{1,20}$"
ICCID_REGEX = "^89964\d{12,14}$"
OTP_CODE = r"^\d{6}$"  # Exactly 6 digits
INVITATION = r"^([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_\-\+\/=]*)$"
##################################################################################
default_branch = "master"

governorates_mapper: dict[str, str] = {
    'anbar': 'anbar',
    'hilla': 'babil',
    'baghdad': 'baghdad',
    'basra': 'basra',
    'diyala': 'diyala',
    'dahouk': 'duhook',
    'erbil': 'erbil',
    'karbala': 'karbala',
    'karkuk': 'kirkuk',
    'amara': 'amara',
    'samawa': 'muthanna',
    'najaf': 'najaf',
    'mosul': 'mousl',
    'dewaniya': 'qaddissiya',
    'salahaldeen': 'salahaldeen',
    'sulaimaniya': 'sulaimaniya',
    'nasriya': 'thiqar',
    'kut': 'wassit'
}


def split_file_name(file_name: str):
    file_name = file_name.split('.')
    ext = file_name[1]
    type = None
    if 'png' == ext or 'jpg' == ext or 'jpeg' == ext:
        type = ContentType.image
    elif 'pdf' == ext:
        type = ContentType.pdf
    elif 'json' == ext:
        type = ContentType.json
    elif 'xml' == ext:
        type = ContentType.markdown
    return file_name[0], file_name[1], type


def camel_case(snake_str):
    words = snake_str.split("_")
    return "".join(word.title() for word in words)


def branch_path(branch_name: str | None = default_branch):
    return (
        (f"branches/{branch_name}") if branch_name != default_branch else "./"
    )


def snake_case(camel_str):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()


def to_float(val: str):
    try:
        return float(val)
    except:
        return None


def to_int(val: str):
    try:
        return int(val)
    except:
        return None
