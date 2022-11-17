import glob
from pathlib import Path

from jsonschema.validators import validate


class Mappers:
    mappers_path: str = 'mappers'
    mappers: list
    mappers_abs_path: str = None

    def load_paths(self) -> int:
        if Path(self.mappers_path).absolute().exists():
            self.mappers_abs_path = str(Path(self.mappers_path).absolute())
        elif Path('../' + self.mappers_path).absolute():
            self.mappers_abs_path = str(Path('../' + self.mappers_path).absolute())
        else:
            return -1

        self.mappers = glob.glob(str(self.mappers_abs_path) + "/*.json")
        return len(self.mappers)
    #
    # def validate_entry(self):
    #
    #
    # def load_mapper_schema(self):
    #
    #     if not path.is_file():
    #         raise api.Exception(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             error=api.Error(type="db", code=12, message="requested object not found"),
    #         )
    #
    # def load_mapper(self, filename):
    #     validate(instance={"name": "Eggs", "price": 34.99}, schema=schema)
    #

mappers = Mappers()
