from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from bookmark_manager.domain.models import Bookmark

type BookmarkSearchKey = tuple[int, int, int, int, int, int, int, str, int]
type GeneralToken = str
type TagToken = str

type SearchTokens = tuple[list[TagToken], list[GeneralToken]]


def build_search_key(
    bookmark: Bookmark,
    tag_names: Sequence[str],
    tag_tokens: Sequence[TagToken],
    general_tokens: Sequence[GeneralToken],
) -> BookmarkSearchKey: ...
def match_display_name(bookmark: Bookmark, token: str) -> bool: ...
def match_tags(tag_name: Sequence[str], token: str) -> bool: ...
def match_url(bookmark: Bookmark, token: str) -> bool: ...
def parse_tokens(query: str) -> SearchTokens: ...
def rank_bookmarks(
    bookmarks: Sequence[Bookmark],
    bookmark_id_to_tags: dict[int, Sequence[str]],
    query: str,
) -> list[Bookmark]: ...
