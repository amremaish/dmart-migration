from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class JoinType(StrEnum):
    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    FULL = "full"
