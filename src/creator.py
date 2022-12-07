import copy
import json
import os
import sys
from pathlib import Path
from typing import Type, TypeVar

import jsonschema

from dmart import core
from dmart.helper import branch_path, default_branch, snake_case, camel_case
from utils.db import db_manager
from utils.mappers import mappers

MetaChild = TypeVar("MetaChild", bound=core.Meta)


class SpaceCreator:
    spaces_path: Path = None

    def scan(self):
        # init spaces
        self.spaces_path = Path(str(mappers.dir_path) + '/spaces')
        if not self.spaces_path.is_dir():
            os.mkdir(self.spaces_path)

    def shortname_fixer(self, shortname: str):
        if not shortname:
            return ''
        return shortname.strip().lower().replace(' ', '')

    def shortname_deep_fixer(self, body: dict):
        if not body:
            return {}
        for k, v in body.items():
            if isinstance(v, dict):
                self.shortname_deep_fixer(body.get(k, {}))
            elif isinstance(v, list) and 'shortname' in k:
                for i in range(len(v)):
                    if v[i]:
                        v[i] = self.shortname_fixer(v[i])
                    else:
                        v.pop(i)
            elif isinstance(v, str) and 'shortname' in k:
                body[k] = self.shortname_fixer(v)

    def save(
            self,
            *,
            space_name: str,
            subpath: str,
            meta: dict,
            body: dict,
            class_type: str,
            schema_shortname: str,
            only_matched_schema: bool,
            appended_list: list = None
    ):
        resource_class = getattr(sys.modules["dmart.core"], camel_case(class_type))
        path, filename = self.metapath(space_name=space_name,
                                       subpath=subpath,
                                       shortname=meta.get("shortname"),
                                       class_type=resource_class,
                                       schema_shortname=schema_shortname)

        body_path = self.payload_path(space_name=space_name,
                                      subpath=subpath,
                                      class_type=resource_class,
                                      schema_shortname=schema_shortname)

        matched_schema = True
        try:
            # validate payload
            mappers.validate_body_entry(body, schema_shortname)
        except jsonschema.exceptions.ValidationError as e:
            print(
                f"waring: this shortname body {meta.get('shortname')} doesn't match schema `{schema_shortname}` [{e.message}]")
            matched_schema = False
        except Exception as e:
            print(str(e))
            matched_schema = False

        if not matched_schema and only_matched_schema:
            return

        if path and not path.is_dir():
            os.makedirs(path)

        body_path = body_path / (meta.get("shortname") + '.json')
        mata_path = path / filename

        if appended_list:
            if body_path.is_file():
                with open(body_path, "r") as json_file:
                    new_body = json.load(json_file)
            if mata_path.is_file():
                with open(body_path, "r") as json_file:
                    new_meta = json.load(json_file)

            self.apply_appended_list(
                old_meta=meta,
                new_meta=new_meta,
                old_body=body,
                new_body=new_body,
                appended_list=appended_list)
        if meta:
            meta_obj = core.Meta(**meta)
            meta_obj.payload = core.Payload(
                content_type='json',
                schema_shortname=schema_shortname,
                body=f'{meta_obj.shortname}.json'
            )
            # save meta
            with open(mata_path, "w") as f:
                f.write(meta_obj.json(exclude_none=True))
        if body:
            # save payload
            with open(body_path, "w") as f:
                f.write(json.dumps(body))

    def apply_appended_list(
            self,
            old_meta: dict,
            new_meta: dict,
            old_body: dict,
            new_body: dict,
            appended_list: list[str] = None
    ):
        for one_list in appended_list:
            path = one_list.split('.', 1)[1]
            if one_list.startswith("body"):
                appended_list = self.find_list_in_dict(path, new_body)
                self.append_list_in_dict(old_body, appended_list, "", path)
            if one_list.startswith("meta"):
                appended_list = self.find_list_in_dict(path, new_meta)
                self.append_list_in_dict(old_meta, appended_list, "", path)

    def find_list_in_dict(self, path: str, obj: dict):
        path = path.split('.')
        itr = 0
        for loc in path:
            # loop into lost expect the first and the last item
            if itr == len(path) - 1:
                break
            obj = obj[loc]
            itr = itr + 1
        return obj[path[-1]]

    def append_list_in_dict(self, body: dict, appended_list: list[str], created_path: str = "", appended_path=""):
        for k, v in body.items():
            if isinstance(v, dict):
                created_path = created_path + f"{k}."
                self.append_list_in_dict(body.get(k, {}), appended_list, created_path, appended_path)
            elif isinstance(v, list) and created_path + k == appended_path:
                v += appended_list

        return body

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

    def convert_db_to_meta(self, row_data: dict, mapper: dict, remove_null_field: bool = False):
        meta = mapper.get('columns_mapper').get('meta')
        body = mapper.get('columns_mapper').get('body')
        meta_data: dict = self.deep_update(copy.deepcopy(meta), row_data)
        body_data: dict = self.deep_update(copy.deepcopy(body), row_data)
        if remove_null_field:
            # loop it for remove empty dict
            for i in range(3):
                self.delete_none(meta_data)
                self.delete_none(body_data)

        return meta_data, body_data

    def deep_update(self, body: dict, row_data):
        if not body:
            return {}
        for k, v in body.items():
            if isinstance(v, dict):
                self.deep_update(body.get(k, {}), row_data)
            elif isinstance(v, str):
                aliased_val = db_manager.create_alias(v)
                if aliased_val and aliased_val in row_data:
                    body[k] = row_data[aliased_val]
            elif isinstance(v, list):
                for i in range(len(v)):
                    aliased_val = db_manager.create_alias(v[i])
                    if aliased_val and aliased_val in row_data:
                        v[i] = row_data[aliased_val]

        return body

    def delete_none(self, _dict):
        if not _dict:
            return {}
        """Delete None values recursively from all of the dictionaries"""
        for key, value in list(_dict.items()):
            if isinstance(value, dict):
                if len(value) != 0:
                    self.delete_none(value)
                else:
                    del _dict[key]
            elif value is None:
                del _dict[key]
            elif isinstance(value, list):
                for v_i in value:
                    if isinstance(v_i, dict):
                        self.delete_none(v_i)

        return _dict


creator = SpaceCreator()
