from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class RequestType(StrEnum):
    create = "create"
    update = "update"
    delete = "delete"
    move = "move"


class Language(StrEnum):
    ar = "arabic"
    en = "english"
    ku = "kurdish"
    fr = "french"
    tr = "trukish"


class ResourceType(StrEnum):
    user = "user"
    group = "group"
    folder = "folder"
    schema = "schema"
    content = "content"
    acl = "acl"
    comment = "comment"
    media = "media"
    locator = "locator"
    relationship = "relationship"
    alteration = "alteration"
    history = "history"
    space = "space"
    branch = "branch"
    permission = "permission"
    role = "role"
    ticket = "ticket"
    json = "json"
    plugin_wrapper = "plugin_wrapper"


class ContentType(StrEnum):
    text = "text"
    markdown = "markdown"
    json = "json"
    image = "image"
    python = "python"
    pdf = "pdf"


class TaskType(StrEnum):
    query = "query"


class UserType(StrEnum):
    web = "web"
    mobile = "mobile"
    bot = "bot"


class LockAction(StrEnum):
    lock = "lock"
    extend = "extend"
    unlock = "unlock"
    cancel = "cancel"
