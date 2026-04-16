from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from bookmark_manager.domain.models import Bookmark, Tag

type BookmarkSortKey = tuple[int, int, str, int]


def bookmark_sort_key(bookmark: Bookmark) -> BookmarkSortKey:
    return (-bookmark.times_copied, -bookmark.initial_weight, bookmark.display_name_normalized, bookmark.bookmark_id)


def compare_tags(tag_a: Tag, tag_b: Tag, sorted_bookmarks_by_tag_id: dict[int, Sequence[Bookmark]]) -> int: ...
def sort_bookmarks(bookmarks: Sequence[Bookmark]) -> list[Bookmark]: ...
