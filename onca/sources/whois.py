"""Fonte: WHOIS via python-whois, com fallback para RDAP."""

import logging
from urllib.parse import quote

from onca.core import get_random_headers, setup_session

logger = logging.getLogger(__name__)


def buscar_whois(domain: str) -> set[str]:
    """Consulta WHOIS via python-whois.

    python-whois consulta o servidor WHOIS diretamente, sem intermediários.
    Retorna nameservers como strings.
    """
    try:
        import whois

        w = whois.whois(domain)
        urls: set[str] = set()

        if w.name_servers:
            ns_list = (
                w.name_servers
                if isinstance(w.name_servers, list)
                else [w.name_servers]
            )
            for ns in ns_list:
                ns = ns.lower().strip(".").strip()
                if ns and domain in ns:
                    urls.add(ns)

        logger.info(f"WHOIS: {len(urls)} nameservers")
        return urls
    except ImportError:
        logger.warning("python-whois não instalado, pulando WHOIS")
        return set()
    except Exception as e:
        logger.error(f"WHOIS error: {e}")
        return set()


def buscar_rdap(domain: str) -> set[str]:
    """Consulta RDAP via rdap.org (JSON estruturado, fallback do WHOIS)."""
    try:
        session = setup_session()
        url = f"https://rdap.org/domain/{quote(domain)}"
        response = session.get(url, headers=get_random_headers(), timeout=20)

        if response.status_code != 200:
            logger.error(f"RDAP: HTTP {response.status_code}")
            return set()

        data = response.json()
        urls: set[str] = set()

        for ns in data.get("nameservers", []):
            name = ns.get("ldhName", "").lower()
            if name and domain in name:
                urls.add(name)

        logger.info(f"RDAP: {len(urls)} nameservers")
        return urls
    except Exception as e:
        logger.error(f"RDAP error: {e}")
        return set()
