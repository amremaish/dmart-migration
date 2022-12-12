import glob
import json
import jsonschema
from pathlib import Path

from jsonschema import validators
from jsonschema.validators import Draft4Validator


class Mappers:
    mappers_path: str = 'mappers'
    mappers: list
    mappers_abs_path = None
    dir_path: Path = None

    def load_paths(self) -> int:
        if Path(self.mappers_path).absolute().exists():
            self.mappers_abs_path = Path(self.mappers_path).absolute()
            self.dir_path = Path('').absolute()
        elif Path('../' + self.mappers_path).absolute():
            self.mappers_abs_path = Path('../' + self.mappers_path).absolute()
            self.dir_path = Path('').absolute()
        else:
            return -1

        self.mappers = glob.glob(str(self.mappers_abs_path) + "/*.json")
        return len(self.mappers)

    def extend_with_default(self, validator_class):
        validate_properties = validator_class.VALIDATORS["properties"]

        def set_defaults(validator, properties, instance, schema):
            for property_, subschema in properties.items():
                if "default" in subschema and not isinstance(instance, list):
                    instance.setdefault(property_, subschema["default"])
                    if instance.get(property_) is None:
                        instance[property_] = subschema["default"]

            for error in validate_properties(
                    validator, properties, instance, schema,
            ):
                yield error

        return validators.extend(
            validator_class, {"properties": set_defaults},
        )

    def validate_file_entry(self, json_filename, schema_shortname):
        schema_path = self.mappers_abs_path / "schema" / f'{schema_shortname}.json'
        json_path = self.mappers_abs_path / f'{json_filename}.json'
        if not schema_path.is_file():
            raise Exception("Schema is not found in this path " + str(schema_path))
        if not json_path.is_file():
            raise Exception("Json file is not found in this path " + str(json_path))
        jsonschema.validate(instance=json.loads(json_path.read_bytes()), schema=json.loads(schema_path.read_bytes()))

    def validate_body_entry(self, json_body, schema_shortname):
        if not schema_shortname:
            return
        schema_path = self.mappers_abs_path / "schema" / f'{schema_shortname}.json'
        if not schema_path.is_file():
            raise Exception("Schema is not found in this path " + str(schema_path))
        validator = self.extend_with_default(Draft4Validator)
        validator(json.loads(schema_path.read_bytes())).validate(json_body)

    def load(self, mapper_name):
        path = self.mappers_abs_path / f'{mapper_name}.json'
        return json.loads(path.read_bytes())


mappers = Mappers()
