import os
from pathlib import Path
from typing import Type, TypeVar

from dmart import core
from dmart.helper import branch_path, default_branch, snake_case
from utils.mappers import mappers

MetaChild = TypeVar("MetaChild", bound=core.Meta)


class SpaceCreator:
    spaces_path: Path = None

    def load(self):
        # init spaces
        self.spaces_path = Path(str(mappers.dir_path) + '/spaces')
        if not self.spaces_path.is_dir():
            os.mkdir(self.spaces_path)

    def save(
            self,
            *,
            space_name: str,
            subpath: str,
            entry: core.Meta,
            class_type: Type[MetaChild]):

        meta_path = self.metapath(space_name=space_name,
                                  subpath=subpath,
                                  shortname=entry.shortname,
                                  class_type=class_type,
                                  schema_shortname=entry.payload.schema_shortname)

        payload_path = self.payload_path(space_name=space_name,
                                         subpath=subpath,
                                         class_type=class_type,
                                         schema_shortname=entry.payload.schema_shortname)

        print(meta_path)
        print(payload_path)

    def metapath(
            self,
            *,
            space_name: str,
            subpath: str,
            shortname: str,
            class_type: Type[MetaChild],
            branch_name: str | None = default_branch,
            schema_shortname: str | None = None,
    ) -> tuple[Path, str]:

        """Construct the full path of the meta file"""
        path = self.spaces_path / space_name / branch_path(branch_name)
        filename = ""
        if subpath[0] == "/":
            subpath = f".{subpath}"
        if issubclass(class_type, core.Folder):
            path = path / subpath / shortname / ".dm"
            filename = f"meta.{class_type.__name__.lower()}.json"
        elif issubclass(class_type, core.Space):
            path = self.spaces_path / space_name / ".dm" / shortname
            filename = "meta.space.json"
        elif issubclass(class_type, core.Attachment):
            [parent_subpath, parent_name] = subpath.rsplit("/", 1)
            schema_shortname = "." + schema_shortname if schema_shortname else ""
            attachment_folder = (
                f"{parent_name}/attachments{schema_shortname}.{class_type.__name__.lower()}"
            )
            path = path / parent_subpath / ".dm" / attachment_folder
            filename = f"meta.{shortname}.json"
        elif issubclass(class_type, core.History):
            [parent_subpath, parent_name] = subpath.rsplit("/", 1)
            path = path / parent_subpath / ".dm" / f"{parent_name}/history"
            filename = f"{shortname}.json"
        elif issubclass(class_type, core.Branch):
            path = self.spaces_path / space_name / shortname / ".dm"
            filename = f"meta.branch.json"
        else:
            path = path / subpath / ".dm" / shortname
            filename = f"meta.{snake_case(class_type.__name__)}.json"
        return path, filename

    def payload_path(
            self,
            *,
            space_name: str,
            subpath: str,
            class_type: Type[MetaChild],
            branch_name: str | None = default_branch,
            schema_shortname: str | None = None,
    ) -> Path:
        """Construct the full path of the meta file"""
        path = self.spaces_path / space_name / branch_path(branch_name)

        if subpath[0] == "/":
            subpath = f".{subpath}"
        if issubclass(class_type, core.Attachment):
            [parent_subpath, parent_name] = subpath.rsplit("/", 1)
            schema_shortname = "." + schema_shortname if schema_shortname else ""
            attachment_folder = (
                f"{parent_name}/attachments{schema_shortname}.{class_type.__name__.lower()}"
            )
            path = path / parent_subpath / ".dm" / attachment_folder
        else:
            path = path / subpath
        return path

spaces_creator = SpaceCreator()
