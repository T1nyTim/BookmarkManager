from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from bookmark_manager.domain.models import Bookmark, Tag

type BookmarkSortKey = tuple[int, int, str, int]


def bookmark_sort_key(bookmark: Bookmark) -> BookmarkSortKey:
    return (-bookmark.times_copied, -bookmark.initial_weight, bookmark.display_name_normalized, bookmark.bookmark_id)


def compare_tags(tag_a: Tag, tag_b: Tag, sorted_bookmarks_by_tag_id: dict[int, Sequence[Bookmark]]) -> int:
    bookmarks_a = sorted_bookmarks_by_tag_id.get(tag_a.tag_id, ())
    bookmarks_b = sorted_bookmarks_by_tag_id.get(tag_b.tag_id, ())
    for a, b in zip(bookmarks_a, bookmarks_b, strict=False):
        key_a = bookmark_sort_key(a)
        key_b = bookmark_sort_key(b)
        if key_a < key_b:
            return -1
        if key_a > key_b:
            return 1
    if tag_a.name_normalized < tag_b.name_normalized:
        return -1
    if tag_a.name_normalized > tag_b.name_normalized:
        return 1
    return 0


def sort_bookmarks(bookmarks: Sequence[Bookmark]) -> list[Bookmark]:
    return sorted(bookmarks, key=bookmark_sort_key)
