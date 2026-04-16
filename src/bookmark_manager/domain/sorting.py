from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bookmark_manager.domain.models import Bookmark


def sort_bookmarks(bookmarks: list[Bookmark]) -> list[Bookmark]: ...
def compare_tags() -> int: ...
