"""Fontes de coleta da ONÇA.

- FONTES_URL: fontes que retornam URLs (wayback, google, whois)
- FONTES_SUBDOMINIO: fontes que retornam subdomínios (crtsh)
"""

from .crtsh import buscar_crtsh
from .google import buscar_google
from .hackertarget import buscar_hackertarget
from .wayback import buscar_wayback
from .whois import buscar_rdap, buscar_whois

FONTES_URL = {
    "wayback": buscar_wayback,
    "google": buscar_google,
    "whois": buscar_whois,
}

FONTES_SUBDOMINIO = {
    "crtsh": buscar_crtsh,
}

FONTES_FUNCOES = {**FONTES_URL, **FONTES_SUBDOMINIO}

__all__ = [
    "FONTES_FUNCOES",
    "FONTES_SUBDOMINIO",
    "FONTES_URL",
    "buscar_crtsh",
    "buscar_google",
    "buscar_hackertarget",
    "buscar_rdap",
    "buscar_wayback",
    "buscar_whois",
]
