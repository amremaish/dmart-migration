import json
import sys
from abc import ABC, abstractmethod

from pydantic import BaseModel
from pathlib import Path
from typing import Any, List, Type
from pydantic.types import UUID4 as UUID
from uuid import uuid4
from pydantic import Field
from datetime import datetime

from dmart.enums import ContentType, ResourceType, StrEnum, Language, UserType, RequestType
from dmart.helper import SHORTNAME, default_branch, SUBPATH, camel_case


class Resource(BaseModel):
    class Config:
        use_enum_values = True


class Payload(Resource):
    content_type: ContentType
    content_sub_type: str | None = (
        None  # FIXME change to proper content type static hashmap
    )
    schema_shortname: str | None = None
    checksum: str | None = None
    body: str | dict[str, Any] | Path


class Record(BaseModel):
    resource_type: ResourceType
    uuid: UUID | None = None
    shortname: str = Field(regex=SHORTNAME)
    branch_name: str | None = Field(
        default=default_branch, regex=SHORTNAME
    )
    subpath: str = Field(regex=SUBPATH)
    attributes: dict[str, Any]
    attachments: dict[ResourceType, list[Any]] | None = None
    permissions: dict[str, Any] | None = None
    roles: List[str] | None = None
    groups: List[str] | None = None

    def to_dict(self):
        return json.loads(self.json())


class Meta(Resource):
    uuid: UUID = Field(default_factory=uuid4)
    shortname: str
    is_active: bool = False
    displayname: str | None = None
    description: str | None = None
    tags: list[str] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    owner_shortname: str
    payload: Payload | None = None

    @staticmethod
    def from_record(record: Record, owner_shortname: str):
        meta_class = getattr(
            sys.modules["models.core"], camel_case(record.resource_type)
        )


        meta_obj = meta_class(
            owner_shortname=owner_shortname,
            shortname=record.shortname,
            **record.attributes,
        )
        return meta_obj

    def update_from_record(self, record: Record):
        restricted_fields = [
            "uuid",
            "shortname",
            "created_at",
            "updated_at",
            "owner_shortname",
            "payload",
        ]
        for field_name, field_value in self.__dict__.items():
            if field_name in record.attributes and field_name not in restricted_fields:
                if isinstance(self, User) and field_name == "password":
                    continue
                self.__setattr__(field_name, record.attributes[field_name])

    def to_record(
        self,
        subpath: str,
        shortname: str,
        include: list[str],
        branch_name: str | None = None,
    ):
        # Sanity check
        assert self.shortname == shortname
        record_fields = {
            "resource_type": type(self).__name__.lower(),
            "uuid": self.uuid,
            "shortname": self.shortname,
            "subpath": subpath,
        }
        if branch_name:
            record_fields["branch_name"] = branch_name

        attributes = {}
        for key, value in self.__dict__.items():
            if (not include or key in include) and key not in record_fields:
                attributes[key] = value

        record_fields["attributes"] = attributes

        return Record(**record_fields)


class Locator(Resource):
    uuid: UUID | None = None
    type: ResourceType
    space_name: str
    branch_name: str
    subpath: str
    shortname: str
    displayname: str | None = None
    description: str | None = None
    tags: list[str] | None = None


class Space(Meta):
    root_registration_signature: str = ""
    primary_website: str = ""
    indexing_enabled: bool = False
    capture_misses: bool = False
    check_health: bool = False
    languages: list[Language] = [Language.en]
    icon: str = ""
    mirrors: list[str] = []
    active_plugins: list[str] = []
    branches: list[str] = []


class Actor(Meta):
    pass


class User(Actor):
    password: str
    email: str | None = None
    msisdn: str | None = None
    is_email_verified: bool = False
    is_msisdn_verified: bool = False
    force_password_change: bool = False
    type: UserType = UserType.web
    roles: list[str] = []


class Group(Actor):
    members: list[str] = []  # list of actor_shortnames


class Attachment(Meta):
    pass


class Json(Attachment):
    pass


class Comment(Attachment):
    body: str


class Media(Attachment):
    pass


class Relationship(Attachment):
    related_to: Locator
    attributes: dict[str, Any]


class Action(Resource):
    resource: Locator
    user_shortname: str
    request: RequestType
    timestamp: datetime
    attributes: dict[str, Any] | None


class History(Meta):
    timestamp: datetime
    diff: dict[str, Any]


class Schema(Meta):
    pass

    # USE meta_schema TO VALIDATE ANY SCHEMA
    def __init__(self, **data):
        Meta.__init__(self, **data)
        if self.payload != None and self.shortname != "meta_schema":
            self.payload.schema_shortname = "meta_schema"


class Content(Meta):
    pass


class Folder(Meta):
    pass


class Branch(Folder):
    pass


class ActionType(StrEnum):
    query = "query"
    view = "view"
    update = "update"
    create = "create"
    delete = "delete"
    attach = "attach"
    move = "move"


class ConditionType(StrEnum):
    is_active = "is_active"
    own = "own"


class Permission(Meta):
    subpaths: dict[str, set[str]]  # {"space_name": ["subpath_one", "subpath_two"]}
    resource_types: set[ResourceType]
    actions: set[ActionType]
    conditions: set[ConditionType] = set()


class Role(Meta):
    permissions: set[str]  # list of permissions_shortnames
    entitled_users: set[str]  # list of user_shortnames
    entitled_groups: set[str]  # list of group_shortnames


class Collabolator(Resource):
    role: str | None = ""  # a free-text role-name e.g. developer, qa, admin, ...
    shortname: str


class Ticket(Meta):
    state: str
    workflow_shortname: str
    collaborators: list[Collabolator] | None = None
    resolution_reason: str | None = None


class PluginBase(ABC):
    @abstractmethod
    def hook(self):
        pass


class EventFilter(BaseModel):
    subpaths: list
    resource_types: list
    schema_shortnames: list
    actions: list[ActionType]


class PluginType(StrEnum):
    hook = "hook"


class EventListenTime(StrEnum):
    before = "before"
    after = "after"


class PluginWrapper(Meta):
    filters: EventFilter
    listen_time: EventListenTime
    type: PluginType
    object: Type[PluginBase] | None


class Event(BaseModel):
    space_name: str
    branch_name: str | None = Field(
        default=default_branch, regex=SHORTNAME
    )
    subpath: str = Field(regex=SUBPATH)
    shortname: str | None = Field(default=None, regex=SHORTNAME)
    action_type: ActionType
    resource_type: ResourceType | None = None
    schema_shortname: str | None = None
    attributes: dict | None = None
    user_shortname: str


def transite(states, current_state: str, action: str, user_roles):
    for state in states:
        if state["state"] == current_state:
            for next_state in state["next"]:
                if next_state["action"] == action:
                    for role in next_state["roles"]:
                        if role in user_roles:
                            return {"status": True, "message": next_state["state"]}
            return {
                "status": False,
                "message": f"You don't have the permission to progress this ticket with action {action}",
            }

    return {
        "status": False,
        "message": f"You can't progress from {current_state} using {action}",
    }


def post_transite(states, next_state: str, resolution: str):
    for state in states:
        if state["state"] == next_state:
            if "resolutions" in state:
                available_resolutions = [one["key"] for one in state["resolutions"]]
                if resolution in available_resolutions:
                    return {"status": True, "message": resolution}
                else:
                    return {
                        "status": False,
                        "message": f"The resolution {resolution} provided is not acceptable in state {next_state}",
                    }
    return {
        "status": False,
        "message": f"Cannot fetch the next state {next_state} with resolution {resolution}",
    }
