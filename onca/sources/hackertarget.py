"""Fonte: HackerTarget (fallback de subdomínios)."""

import logging
from urllib.parse import quote

from onca.core import get_random_headers, setup_session

logger = logging.getLogger(__name__)


def buscar_hackertarget(domain: str) -> set[str]:
    """Fallback de subdomínios via API pública do HackerTarget.

    Limite: ~50 req/dia sem API key.
    """
    try:
        session = setup_session()
        url = f"https://api.hackertarget.com/hostsearch/?q={quote(domain)}"
        response = session.get(url, headers=get_random_headers(), timeout=20)

        if response.status_code != 200:
            logger.error(f"HackerTarget: HTTP {response.status_code}")
            return set()

        subdomains: set[str] = set()
        for line in response.text.splitlines():
            if "," in line:
                sub = line.split(",")[0].strip().lower()
                if sub and sub.endswith(domain) and sub != domain:
                    subdomains.add(sub)
        return subdomains
    except Exception as e:
        logger.error(f"HackerTarget error: {e}")
        return set()
