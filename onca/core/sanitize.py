"""Validação e limpeza de URLs."""

from urllib.parse import urlparse


def sanitize_url(url: str | None) -> str | None:
    """Retorna a URL se ela tiver scheme e host válidos; senão, None."""
    if not url or not isinstance(url, str):
        return None
    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            return url.strip()
        return None
    except (ValueError, AttributeError):
        return None
