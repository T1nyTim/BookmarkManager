from enum import Enum, IntEnum, auto


class EditorMode(Enum):
    EDIT = auto()
    ADD = auto()


class Selection(IntEnum):
    SELECTED = True
    NOT_SELECTED = False
