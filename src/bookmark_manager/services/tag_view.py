from dataclasses import dataclass
from functools import cmp_to_key
from typing import TYPE_CHECKING

from bookmark_manager.domain.sorting import compare_tags, sort_bookmarks

if TYPE_CHECKING:
    from bookmark_manager.domain.models import Bookmark
    from bookmark_manager.repositories.bookmark_tag import BookmarkTagRepository
    from bookmark_manager.repositories.tag import TagRepository


@dataclass(slots=True)
class TagSectionDomain:
    tag_id: int
    tag_name: str
    bookmarks: tuple[Bookmark, ...]


@dataclass(slots=True)
class TagViewResult:
    sections: tuple[TagSectionDomain, ...]
    bookmark_id_to_tag_names: dict[int, tuple[str, ...]]


class TagViewService:
    def __init__(
        self,
        tag_repository: TagRepository,
        bookmark_tag_repository: BookmarkTagRepository,
    ) -> None:
        self._tag_repository = tag_repository
        self._bookmark_tag_repository = bookmark_tag_repository

    def get_tag_sections(self) -> tuple[TagSectionDomain, ...]:
        tags = self._tag_repository.list_all()
        sorted_bookmarks_by_tag_id = {}
        for tag in tags:
            bookmarks = self._bookmark_tag_repository.get_bookmarks_for_tag(tag.tag_id)
            sorted_bookmarks_by_tag_id[tag.tag_id] = tuple(sort_bookmarks(bookmarks))
        sorted_tags = sorted(tags, key=cmp_to_key(lambda left, right: compare_tags(left, right, sorted_bookmarks_by_tag_id)))
        return tuple(TagSectionDomain(tag.tag_id, tag.name_display, sorted_bookmarks_by_tag_id[tag.tag_id]) for tag in sorted_tags)

    def get_tag_view(self) -> TagViewResult:
        sections = self.get_tag_sections()
        bookmark_ids = tuple(dict.fromkeys(bookmark.bookmark_id for section in sections for bookmark in section.bookmarks))
        tags_by_bookmark_id = self._bookmark_tag_repository.get_tags_for_bookmarks(bookmark_ids)
        bookmark_id_to_tag_names = {bookmark_id: tuple(tag.name_display for tag in tags) for bookmark_id, tags in tags_by_bookmark_id.items()}
        return TagViewResult(sections, bookmark_id_to_tag_names)
