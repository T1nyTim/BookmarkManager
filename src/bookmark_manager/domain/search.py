from typing import TYPE_CHECKING

from bookmark_manager.domain.normalization import normalize_search_token

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
) -> BookmarkSearchKey:
    matched_tokens = set()
    name_match_count = 0
    url_match_count = 0
    tag_match_count = 0
    has_matching_tag_token = False
    for tag_token in tag_tokens:
        if match_tags(tag_names, tag_token):
            has_matching_tag_token = True
            matched_tokens.add(f"tag:{tag_token}")
            tag_match_count += 1
    for general_token in general_tokens:
        matched_this_token = False
        if match_display_name(bookmark, general_token):
            name_match_count += 1
            matched_this_token = True
        if match_url(bookmark, general_token):
            url_match_count += 1
            matched_this_token = True
        if match_tags(tag_names, general_token):
            tag_match_count += 1
            matched_this_token = True
        if matched_this_token:
            matched_tokens.add(f"general:{general_token}")
    tag_match_group = 0
    if tag_tokens and not has_matching_tag_token:
        tag_match_group = 1
    return (
        tag_match_group,
        -len(matched_tokens),
        -name_match_count,
        -url_match_count,
        -tag_match_count,
        -bookmark.times_copied,
        -bookmark.initial_weight,
        bookmark.display_name_normalized,
        bookmark.bookmark_id,
    )


def match_display_name(bookmark: Bookmark, token: str) -> bool:
    return token in bookmark.display_name_normalized


def match_tags(tag_names: Sequence[str], token: str) -> bool:
    return any(token in tag_name for tag_name in tag_names)


def match_url(bookmark: Bookmark, token: str) -> bool:
    return token in bookmark.url.lower()


def parse_tokens(query: str) -> SearchTokens:
    tag_tokens = []
    general_tokens = []
    for raw_token in query.split():
        if raw_token.startswith("#"):
            if raw_token == "#":  # noqa: S105
                continue
            tag_tokens.append(normalize_search_token(raw_token[1:]))
            continue
        general_tokens.append(normalize_search_token(raw_token))
    return tag_tokens, general_tokens


def rank_bookmarks(
    bookmarks: Sequence[Bookmark],
    bookmark_id_to_tags: dict[int, Sequence[str]],
    query: str,
) -> list[Bookmark]:
    tag_tokens, general_tokens = parse_tokens(query)
    if not tag_tokens and not general_tokens:
        return sorted(
            bookmarks,
            key=lambda bookmark: (-bookmark.times_copied, -bookmark.initial_weight, bookmark.display_name_normalized, bookmark.bookmark_id),
        )
    ranked_bookmarks = []
    for bookmark in bookmarks:
        tag_names = bookmark_id_to_tags.get(bookmark.bookmark_id, ())
        search_key = build_search_key(bookmark, tag_names, tag_tokens, general_tokens)
        if search_key[1] == 0:
            continue
        ranked_bookmarks.append((search_key, bookmark))
    ranked_bookmarks.sort(key=lambda item: item[0])
    return [bookmark for _, bookmark in ranked_bookmarks]
