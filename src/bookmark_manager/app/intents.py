from dataclasses import dataclass

type Intent = (
    RequestAddBookmark
    | RequestCancelBookmarkEditor
    | RequestConfirmBookmarkEditor
    | RequestCopyBookmark
    | RequestCopySelectedBookmark
    | RequestEditBookmark
    | RequestSearchChanged
    | RequestToggleSelection
    | RequestToggleTagExpansion
)


@dataclass(slots=True, frozen=True)
class RequestAddBookmark:
    pass


@dataclass(slots=True, frozen=True)
class RequestCancelBookmarkEditor:
    pass


@dataclass(slots=True, frozen=True)
class RequestConfirmBookmarkEditor:
    url: str
    display_name: str
    tag_names: tuple[str, ...]
    initial_weight: int


@dataclass(slots=True, frozen=True)
class RequestCopyBookmark:
    bookmark_id: int
    url: str


@dataclass(slots=True, frozen=True)
class RequestCopySelectedBookmark:
    pass


@dataclass(slots=True, frozen=True)
class RequestEditBookmark:
    bookmark_id: int


@dataclass(slots=True, frozen=True)
class RequestSearchChanged:
    query_text: str


@dataclass(slots=True, frozen=True)
class RequestToggleSelection:
    bookmark_id: int


@dataclass(slots=True, frozen=True)
class RequestToggleTagExpansion:
    tag_id: int
