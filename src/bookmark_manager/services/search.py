from dataclasses import dataclass
from typing import TYPE_CHECKING

from bookmark_manager.domain.search import rank_bookmarks

if TYPE_CHECKING:
    from bookmark_manager.domain.models import Bookmark
    from bookmark_manager.repositories.bookmark import BookmarkRepository
    from bookmark_manager.repositories.bookmark_tag import BookmarkTagRepository


@dataclass(slots=True)
class SearchResult:
    bookmarks: tuple[Bookmark, ...]
    bookmark_id_to_tag_names: dict[int, tuple[str, ...]]


class SearchService:
    def __init__(self, bookmark_repo: BookmarkRepository, bookmark_tag_repo: BookmarkTagRepository) -> None:
        self._bookmark_repo = bookmark_repo
        self._bookmark_tag_repo = bookmark_tag_repo

    def search(self, query: str) -> SearchResult:
        bookmarks = self._bookmark_repo.list_all()
        bookmark_id_to_tag_names = {}
        for bookmark in bookmarks:
            tags = self._bookmark_tag_repo.get_tags_for_bookmark(bookmark.bookmark_id)
            bookmark_id_to_tag_names[bookmark.bookmark_id] = tuple(tag.name_display for tag in tags)
        ranked_bookmarks = tuple(rank_bookmarks(bookmarks, bookmark_id_to_tag_names, query))
        return SearchResult(ranked_bookmarks, bookmark_id_to_tag_names)
