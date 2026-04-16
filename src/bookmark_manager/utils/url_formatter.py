from urllib.parse import urlsplit


def shorten_url(url: str, max_length: int = 60) -> str:
    if len(url) <= max_length:
        return url
    parts = urlsplit(url)
    domain = parts.netloc or parts.path
    path = parts.path if parts.netloc else ""
    if not path:
        shortened = domain
        if parts.query:
            shortened = f"{shortened}/...?"
        return shortened if len(shortened) <= max_length else f"{shortened[: max_length - 3]}..."
    path_parts = [part for part in path.split("/") if part]
    last_part = path_parts[-1] if path_parts else ""
    shortened = f"{domain}/.../{last_part}" if last_part else f"{domain}/..."
    if parts.query:
        shortened = f"{shortened}?"
    if len(shortened) <= max_length:
        return shortened
    if len(domain) + 4 <= max_length:
        return f"{domain}/..."
    return f"{url[: max_length - 3]}..."
