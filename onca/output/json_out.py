"""Saída em JSON."""

import json
import logging

logger = logging.getLogger(__name__)


def salvar_json(
    caminho: str,
    urls: set[str],
    subdomains: set[str],
) -> None:
    """Salva os resultados em JSON, com URLs e subdomínios separados."""
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(
            {
                "urls": sorted(urls),
                "subdomains": sorted(subdomains),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    logger.info(
        f"Salvo em {caminho} "
        f"({len(urls)} URLs, {len(subdomains)} subdomínios)"
    )
