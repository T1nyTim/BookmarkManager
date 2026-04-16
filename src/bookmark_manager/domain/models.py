from dataclasses import dataclass
from enum import IntEnum


class Selection(IntEnum):
    SELECTED = True
    NOT_SELECTED = False


@dataclass(slots=True)
class Bookmark:
    bookmark_id: int
    url: str
    display_name: str
    display_name_normalized: str
    initial_weight: int
    times_copied: int


@dataclass(slots=True)
class Tag:
    tag_id: int
    name_display: str
    name_normalized: str
