from dataclasses import dataclass
from typing import TYPE_CHECKING

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
        sections = []
        for tag in self._tag_repository.list_all():
            bookmarks = self._bookmark_tag_repository.get_bookmarks_for_tag(tag.tag_id)
            sections.append(TagSectionDomain(tag.tag_id, tag.name_display, tuple(bookmarks)))
        return tuple(sections)
