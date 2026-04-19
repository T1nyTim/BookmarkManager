from dataclasses import dataclass
from typing import TYPE_CHECKING

from bookmark_manager.domain.models import Bookmark
from bookmark_manager.domain.normalization import normalize_display_name, normalize_tag

if TYPE_CHECKING:
    from collections.abc import Sequence

    from bookmark_manager.repositories.bookmark import BookmarkRepository
    from bookmark_manager.repositories.bookmark_tag import BookmarkTagRepository
    from bookmark_manager.repositories.tag import TagRepository


class DuplicateBookmarkError(ValueError):
    def __init__(self, candidate: DuplicateCandidate) -> None:
        super().__init__("Bookmark already exists")
        self.candidate = candidate


@dataclass(slots=True, frozen=True)
class DuplicateCandidate:
    bookmark_id: int
    url: str
    existing_display_name: str
    existing_tag_names: tuple[str, ...]
    existing_initial_weight: int
    incoming_display_name: str
    incoming_tag_names: tuple[str, ...]
    incoming_initial_weight: int

    def is_exact_duplicate(self) -> bool:
        return (
            self.existing_display_name == self.incoming_display_name
            and self.existing_initial_weight == self.incoming_initial_weight
            and self._normalized_existing_tags() == self._normalized_incoming_tags()
        )

    def _normalized_existing_tags(self) -> tuple[str, ...]:
        return tuple(sorted(normalize_tag(tag) for tag in self.existing_tag_names))

    def _normalized_incoming_tags(self) -> tuple[str, ...]:
        return tuple(sorted(normalize_tag(tag) for tag in self.incoming_tag_names))


class BookmarkService:
    def __init__(self, bookmark_repo: BookmarkRepository, tag_repo: TagRepository, bookmark_tag_repo: BookmarkTagRepository) -> None:
        self._bookmark_repo = bookmark_repo
        self._tag_repo = tag_repo
        self._bookmark_tag_repo = bookmark_tag_repo

    def add_bookmark(self, url: str, display_name: str, tags: Sequence[str], initial_weight: int) -> int:
        existing = self._bookmark_repo.get_by_url(url)
        if existing is not None:
            existing_tags = self._bookmark_tag_repo.get_tags_for_bookmark(existing.bookmark_id)
            raise DuplicateBookmarkError(
                DuplicateCandidate(
                    existing.bookmark_id,
                    url,
                    existing.display_name,
                    tuple(tag.name_display for tag in existing_tags),
                    existing.initial_weight,
                    display_name,
                    tuple(tags),
                    initial_weight,
                ),
            )
        display_name_normalized = normalize_display_name(display_name)
        bookmark = Bookmark(0, url, display_name, display_name_normalized, initial_weight, 0)
        bookmark_id = self._bookmark_repo.add(bookmark)
        self._assign_tags(bookmark_id, tags)
        return bookmark_id

    def copy_bookmark(self, bookmark_id: int) -> None:
        self._bookmark_repo.increment_copy_count(bookmark_id)

    def edit_bookmark(self, bookmark_id: int, display_name: str, tags: Sequence[str], initial_weight: int) -> None:
        bookmark = self._bookmark_repo.get_by_id(bookmark_id)
        if bookmark is None:
            msg = "Bookmark not found"
            raise ValueError(msg)
        bookmark.display_name = display_name
        bookmark.display_name_normalized = normalize_display_name(display_name)
        bookmark.initial_weight = initial_weight
        self._bookmark_repo.update(bookmark)
        self._bookmark_tag_repo.unlink_all(bookmark_id)
        self._assign_tags(bookmark_id, tags)

    def _assign_tags(self, bookmark_id: int, tags: Sequence[str]) -> None:
        for tag in tags:
            tag_normalized = normalize_tag(tag)
            tag_obj = self._tag_repo.get_or_create(tag, tag_normalized)
            self._bookmark_tag_repo.link(bookmark_id, tag_obj.tag_id)
