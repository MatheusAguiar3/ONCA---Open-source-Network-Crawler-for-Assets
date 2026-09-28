"""Configuração de sessão HTTP reutilizável.

Centraliza a criação da sessão `requests` com retry automático e os
headers rotativos, para que todas as fontes usem a mesma configuração.
"""

from random import choice

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]


def setup_session() -> requests.Session:
    """Cria uma sessão requests com retry automático em erros 5xx."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_random_headers() -> dict[str, str]:
    """Headers rotativos para reduzir chance de bloqueio."""
    return {
        "User-Agent": choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
    }
