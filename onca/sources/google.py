"""Fonte: Google (scraping).

Atenção: scraping do Google viola ToS e costuma ser bloqueado.
O filtro final por keyword é aplicado no CLI, não aqui.
"""

import logging

from bs4 import BeautifulSoup

from onca.core import get_random_headers, sanitize_url, setup_session

logger = logging.getLogger(__name__)


def buscar_google(domain: str, keyword: str | None = None) -> set[str]:
    """URLs indexadas via scraping do Google."""
    try:
        query = f"site:{domain}"
        if keyword:
            query += f" {keyword}"

        session = setup_session()
        url = "https://www.google.com/search"
        params = {"q": query, "num": 50}

        response = session.get(
            url, params=params, headers=get_random_headers(), timeout=15
        )
        if response.status_code != 200:
            logger.error(f"Google: HTTP {response.status_code}")
            return set()

        soup = BeautifulSoup(response.text, "html.parser")
        urls = set()
        for link in soup.select('a[href^="/url?q="]'):
            href = link["href"].split("&")[0].replace("/url?q=", "")
            u = sanitize_url(href)
            if u and domain in u:
                urls.add(u)
        return urls
    except Exception as e:
        logger.error(f"Google error: {e}")
        return set()
