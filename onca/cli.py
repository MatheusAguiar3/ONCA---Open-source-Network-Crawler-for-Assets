"""Interface de linha de comando da ONÇA.

Os argumentos formam o acrônimo ONÇA:
  -o  domínio alvo (Obrigatório)
  -n  palavra-chave (Nome/filtro)
  -c  fontes de busca (Choice)
  -a  arquivo de saída (Arquivo)
"""

import argparse
import logging
import time
from urllib.parse import urlparse

from onca.output import salvar_json, salvar_txt
from onca.sources import FONTES_FUNCOES, FONTES_SUBDOMINIO, FONTES_URL
from onca.sources import buscar_hackertarget, buscar_rdap, buscar_whois

logger = logging.getLogger(__name__)

DELAY = 3  # Delay padrão entre fontes (segundos)


def _configurar_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def _buscar_em_fonte(
    source: str,
    domain: str,
    keyword: str | None,
    resultados: dict[str, set[str]],
) -> None:
    """Executa uma fonte e atualiza `resultados` in-place."""
    if source == "crtsh":
        new_subs = FONTES_FUNCOES[source](domain)
        if not new_subs:
            logger.info("crt.sh vazio ou falhou, tentando HackerTarget...")
            new_subs = buscar_hackertarget(domain)
        resultados["subdomains"].update(new_subs)

    elif source == "whois":
        new_urls = buscar_whois(domain)
        if not new_urls:
            logger.info("WHOIS vazio ou falhou, tentando RDAP...")
            new_urls = buscar_rdap(domain)
        resultados["urls"].update(new_urls)

    elif source == "google":
        new_urls = FONTES_FUNCOES[source](domain, keyword)
        resultados["urls"].update(u for u in new_urls if u)

    else:
        new_urls = FONTES_URL[source](domain)
        resultados["urls"].update(u for u in new_urls if u)


def _aplicar_filtros(
    resultados: dict[str, set[str]],
    keyword: str | None,
    strict: bool,
    domain: str,
) -> None:
    """Aplica os filtros de palavra-chave e de domínio estrito in-place."""
    if keyword:
        kw = keyword.lower()
        resultados["urls"] = {u for u in resultados["urls"] if kw in u.lower()}
        resultados["subdomains"] = {
            s for s in resultados["subdomains"] if kw in s.lower()
        }

    if strict:
        resultados["urls"] = {
            u for u in resultados["urls"] if domain in urlparse(u).netloc
        }
        resultados["subdomains"] = {
            s
            for s in resultados["subdomains"]
            if s == domain or s.endswith("." + domain)
        }


def _salvar(caminho: str, resultados: dict[str, set[str]]) -> None:
    """Escolhe o formato de saída com base na extensão do arquivo."""
    if caminho.endswith(".json"):
        salvar_json(caminho, resultados["urls"], resultados["subdomains"])
    else:
        salvar_txt(caminho, resultados["urls"], resultados["subdomains"])


def _imprimir(resultados: dict[str, set[str]]) -> None:
    """Imprime os resultados no terminal."""
    if resultados["subdomains"]:
        print("=== SUBDOMAINS ===")
        for sub in sorted(resultados["subdomains"]):
            print(sub)
    if resultados["urls"]:
        print("\n=== URLS ===")
        for url in sorted(resultados["urls"]):
            print(url)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="onca",
        description=(
            "ONÇA - Open-source Network Crawler for Assets.\n"
            "Os argumentos formam o acrônimo ONÇA:\n"
            "  -o  domínio alvo (Obrigatório)\n"
            "  -n  palavra-chave (Nome/filtro)\n"
            "  -c  fontes de busca (Choice)\n"
            "  -a  arquivo de saída (Arquivo)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exemplo: python onca.py -o exemplo.com -n admin -c google crtsh -a saida.json -v",
    )
    parser.add_argument("-o", "--domain", required=True, help="Domínio alvo")
    parser.add_argument(
        "-n",
        "--keyword",
        help="Palavra-chave (substring) para filtrar resultados",
    )
    parser.add_argument(
        "-c",
        "--sources",
        nargs="+",
        choices=list(FONTES_FUNCOES.keys()),
        default=list(FONTES_FUNCOES.keys()),
        help="Fontes para busca (padrão: todas)",
    )
    parser.add_argument("-a", "--output", help="Arquivo de saída (.json ou .txt)")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Filtrar apenas URLs do domínio exato",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo detalhado")
    parser.add_argument(
        "--delay",
        type=int,
        default=DELAY,
        help=f"Delay entre fontes em segundos (padrão: {DELAY})",
    )

    args = parser.parse_args()

    _configurar_logging(args.verbose)

    resultados: dict[str, set[str]] = {"urls": set(), "subdomains": set()}

    sources_list = list(args.sources)
    for i, source in enumerate(sources_list):
        # Só dorme entre fontes, não antes da primeira
        if i > 0:
            time.sleep(args.delay)

        logger.info(f"Buscando em {source}...")
        try:
            _buscar_em_fonte(source, args.domain, args.keyword, resultados)
        except Exception as e:
            logger.error(f"Erro em {source}: {e}")
            continue

    _aplicar_filtros(resultados, args.keyword, args.strict, args.domain)

    if args.output:
        try:
            _salvar(args.output, resultados)
        except Exception as e:
            logger.error(f"Erro ao salvar: {e}")
    else:
        _imprimir(resultados)


if __name__ == "__main__":
    main()
