from typing import TYPE_CHECKING

from bookmark_manager.domain.search import rank_bookmarks

if TYPE_CHECKING:
    from bookmark_manager.repositories.bookmark import BookmarkRepository
    from bookmark_manager.repositories.bookmark_tag import BookmarkTagRepository


class SearchService:
    def __init__(self, bookmark_repo: BookmarkRepository, bookmark_tag_repo: BookmarkTagRepository) -> None:
        self._bookmark_repo = bookmark_repo
        self._bookmark_tag_repo = bookmark_tag_repo

    def search(self, query: str) -> list:
        bookmarks = self._bookmark_repo.list_all()
        bookmark_id_to_tags = {}
        for bookmark in bookmarks:
            tags = self._bookmark_tag_repo.get_tags_for_bookmark(bookmark.bookmark_id)
            bookmark_id_to_tags[bookmark.bookmark_id] = [tag.name_normalized for tag in tags]
        return rank_bookmarks(bookmarks, bookmark_id_to_tags, query)
