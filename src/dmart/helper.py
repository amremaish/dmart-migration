import re

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
MSISDN = r"^[1-9]\d{9}$"  # Exactly 10 digits, not starting with zero
OTP_CODE = r"^\d{6}$"  # Exactly 6 digits
INVITATION = r"^([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_=]+)\.([a-zA-Z0-9_\-\+\/=]*)$"
##################################################################################
default_branch = "master"


def camel_case(snake_str):
    words = snake_str.split("_")
    return "".join(word.title() for word in words)


def branch_path(branch_name: str | None = default_branch):
    return (
        (f"branches/{branch_name}") if branch_name != default_branch else "./"
    )


def snake_case(camel_str):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()
