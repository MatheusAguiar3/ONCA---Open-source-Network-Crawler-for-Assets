"""Fonte: crt.sh (Certificate Transparency)."""

import logging
from urllib.parse import quote

from onca.core import get_random_headers, setup_session

logger = logging.getLogger(__name__)


def buscar_crtsh(domain: str) -> set[str]:
    """Subdomínios via Certificate Transparency (crt.sh).

    Sem API key, sem rate limit agressivo. Só encontra subdomínios que
    já tiveram certificado SSL emitido.
    """
    try:
        session = setup_session()
        url = f"https://crt.sh/?q=%25.{quote(domain)}&output=json"
        response = session.get(url, headers=get_random_headers(), timeout=30)

        if response.status_code != 200:
            logger.error(f"crt.sh: HTTP {response.status_code}")
            return set()

        subdomains: set[str] = set()
        for entry in response.json():
            name = entry.get("name_value", "")
            for sub in name.split("\n"):
                sub = sub.strip().lower().lstrip("*.")
                if sub and sub.endswith(domain) and sub != domain:
                    subdomains.add(sub)
        return subdomains
    except Exception as e:
        logger.error(f"crt.sh error: {e}")
        return set()
