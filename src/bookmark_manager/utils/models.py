from enum import Enum, IntEnum, auto


class EditorMode(Enum):
    EDIT = auto()
    ADD = auto()


class Mergeability(IntEnum):
    MERGEABLE = True
    UNMERGEABLE = False


class Selection(IntEnum):
    SELECTED = True
    NOT_SELECTED = False
