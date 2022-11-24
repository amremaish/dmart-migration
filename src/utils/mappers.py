import glob
import json
import jsonschema
from pathlib import Path


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

    def validate_file_entry(self, json_filename, schema_shortname):
        schema_path = self.mappers_abs_path / "schema" / f'{schema_shortname}.json'
        json_path = self.mappers_abs_path / f'{json_filename}.json'
        if not schema_path.is_file():
            raise Exception("Schema is not found in this path " + str(schema_path))
        if not json_path.is_file():
            raise Exception("Json file is not found in this path " + str(json_path))
        jsonschema.validate(instance=json.loads(json_path.read_bytes()), schema=json.loads(schema_path.read_bytes()))

    def validate_body_entry(self, json_body, schema_shortname):
        schema_path = self.mappers_abs_path / "schema" / f'{schema_shortname}.json'
        if not schema_path.is_file():
            raise Exception("Schema is not found in this path " + str(schema_path))
        jsonschema.validate(instance=json_body, schema=json.loads(schema_path.read_bytes()))

    def load(self, mapper_name):
        path = self.mappers_abs_path / f'{mapper_name}.json'
        return json.loads(path.read_bytes())


mappers = Mappers()
