"""Fonte: Wayback Machine (CDX API)."""

import logging

from onca.core import get_random_headers, sanitize_url, setup_session

logger = logging.getLogger(__name__)


def buscar_wayback(domain: str) -> set[str]:
    """URLs históricas via Wayback Machine (CDX API)."""
    try:
        session = setup_session()
        url = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json"
        response = session.get(url, headers=get_random_headers(), timeout=20)

        if response.status_code != 200:
            logger.error(f"Wayback: HTTP {response.status_code}")
            return set()

        urls = set()
        for item in response.json()[1:]:  # primeira linha é o header
            u = sanitize_url(item[2])
            if u:
                urls.add(u)
        return urls
    except Exception as e:
        logger.error(f"Wayback error: {e}")
        return set()
