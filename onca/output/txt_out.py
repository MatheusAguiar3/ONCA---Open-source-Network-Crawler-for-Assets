"""Saída em texto puro."""

import logging

logger = logging.getLogger(__name__)


def salvar_txt(
    caminho: str,
    urls: set[str],
    subdomains: set[str],
) -> None:
    """Salva os resultados em texto, com seções separadas."""
    with open(caminho, "w", encoding="utf-8") as f:
        if subdomains:
            f.write("=== SUBDOMAINS ===\n")
            f.write("\n".join(sorted(subdomains)))
            f.write("\n\n")
        f.write("=== URLS ===\n")
        f.write("\n".join(sorted(urls)))
    logger.info(
        f"Salvo em {caminho} "
        f"({len(urls)} URLs, {len(subdomains)} subdomínios)"
    )
