def normalize_display_name(value: str) -> str:
    return _normalize_basic(value)


def normalize_search_token(value: str) -> str:
    return _normalize_basic(value)


def normalize_tag(value: str) -> str:
    value = _normalize_basic(value)
    if any(char.isspace() for char in value):
        raise ValueError
    return value


def _normalize_basic(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError
    return value.lower()
