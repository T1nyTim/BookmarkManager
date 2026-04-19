from dataclasses import dataclass
from functools import cmp_to_key
from typing import TYPE_CHECKING

from bookmark_manager.domain.sorting import compare_tags, sort_bookmarks

if TYPE_CHECKING:
    from bookmark_manager.domain.models import Bookmark
    from bookmark_manager.repositories.bookmark import BookmarkRepository
    from bookmark_manager.repositories.bookmark_tag import BookmarkTagRepository
    from bookmark_manager.repositories.tag import TagRepository


@dataclass(slots=True)
class TagSectionDomain:
    tag_id: int
    tag_name: str
    bookmarks: tuple[Bookmark, ...]


class TagViewService:
    def __init__(
        self,
        tag_repository: TagRepository,
        bookmark_tag_repository: BookmarkTagRepository,
        bookmark_repository: BookmarkRepository,
    ) -> None:
        self._tag_repository = tag_repository
        self._bookmark_tag_repository = bookmark_tag_repository
        self._bookmark_repository = bookmark_repository

    def get_tag_sections(self) -> tuple[TagSectionDomain, ...]:
        tags = self._tag_repository.list_all()
        sorted_bookmarks_by_tag_id = {}
        for tag in tags:
            bookmarks = self._bookmark_tag_repository.get_bookmarks_for_tag(tag.tag_id)
            sorted_bookmarks_by_tag_id[tag.tag_id] = tuple(sort_bookmarks(bookmarks))
        sorted_tags = sorted(tags, key=cmp_to_key(lambda left, right: compare_tags(left, right, sorted_bookmarks_by_tag_id)))
        return tuple(TagSectionDomain(tag.tag_id, tag.name_display, sorted_bookmarks_by_tag_id[tag.tag_id]) for tag in sorted_tags)
