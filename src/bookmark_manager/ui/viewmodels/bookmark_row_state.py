from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from bookmark_manager.domain.models import Bookmark
    from bookmark_manager.utils.models import Selection


@dataclass(slots=True)
class BookmarkRowState:
    bookmark_id: int
    display_name: str
    url: str
    shortened_url: str
    tag_names: tuple[str, ...]
    is_selected: bool

    @classmethod
    def from_domain(cls, bookmark: Bookmark, shorten_url: Callable[[str], str], tag_names: tuple[str, ...], selected: Selection) -> BookmarkRowState:
        return cls(bookmark.bookmark_id, bookmark.display_name, bookmark.url, shorten_url(bookmark.url), tag_names, bool(selected))
