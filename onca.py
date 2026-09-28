#!/usr/bin/env python3
"""
ONÇA - Open-source Network Crawler for Assets

"""

#            ██████╗  ███╗   ██╗ ██████╗  █████╗
#            ██╔══██╗ ████╗  ██║██╔════╝ ██╔══██╗
#            ██║  ██║ ██╔██╗ ██║██║      ███████║
#            ██║  ██║ ██║╚██╗██║██║      ██╔══██║
#            ██████╔╝ ██║ ╚████║╚██████╗ ██║  ██║
#            ╚═════╝  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝

import argparse
import json
import logging
import re
import time
from random import choice
from urllib.parse import quote, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

#Logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#Constantes

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
]

DELAY = 3               #Delay padrão entre fontes (segundos)

#Sessão_HTTP

def setup_session():
    """Cria uma sessão requests com retry automático em erros 5xx."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_random_headers():
    """Headers rotativos para reduzir chance de bloqueio."""
    return {
        'User-Agent': choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
    }


def sanitize_url(url):
    """Retorna a URL se ela tiver scheme e host válidos; senão, None."""
    if not url or not isinstance(url, str):
        return None
    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            return url.strip()
        return None
    except (ValueError, AttributeError):
        return None


#Fontes_URL

def buscar_wayback(domain):
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
        logger.error(f"Wayback error: {str(e)}")
        return set()


def buscar_google(domain, keyword=None):
    """URLs indexadas via scraping do Google.

    Atenção: scraping do Google viola ToS e costuma ser bloqueado.
    O filtro final por keyword é aplicado no main(), não aqui.
    """
    try:
        query = f"site:{domain}"
        if keyword:
            query += f" {keyword}"

        session = setup_session()
        url = "https://www.google.com/search"
        params = {'q': query, 'num': 50}

        response = session.get(url, params=params, headers=get_random_headers(), timeout=15)
        if response.status_code != 200:
            logger.error(f"Google: HTTP {response.status_code}")
            return set()

        soup = BeautifulSoup(response.text, 'html.parser')
        urls = set()
        for link in soup.select('a[href^="/url?q="]'):
            href = link['href'].split('&')[0].replace('/url?q=', '')
            u = sanitize_url(href)
            if u and domain in u:
                urls.add(u)
        return urls
    except Exception as e:
        logger.error(f"Google error: {str(e)}")
        return set()


def buscar_whois(domain):
    """Consulta WHOIS via python-whois (dados tradicionais de registro).

    python-whois consulta o servidor WHOIS diretamente, sem intermediários.
    Retorna atributos parseados como name_servers e expiration_date.
    """
    try:
        import whois
        w = whois.whois(domain)
        urls = set()

        #Nameservers — a lib retorna uma lista ou uma string única
        if w.name_servers:
            ns_list = w.name_servers if isinstance(w.name_servers, list) else [w.name_servers]
            for ns in ns_list:
                ns = ns.lower().strip('.').strip()
                if ns and domain in ns:
                    urls.add(ns)

        logger.info(f"WHOIS: {len(urls)} nameservers")
        return urls
    except ImportError:
        logger.warning("python-whois não instalado, pulando WHOIS")
        return set()
    except Exception as e:
        logger.error(f"WHOIS error: {str(e)}")
        return set()


def buscar_rdap(domain):
    """Consulta RDAP via rdap.org (JSON estruturado, fallback do WHOIS)."""
    try:
        session = setup_session()
        url = f"https://rdap.org/domain/{quote(domain)}"
        response = session.get(url, headers=get_random_headers(), timeout=20)

        if response.status_code != 200:
            logger.error(f"RDAP: HTTP {response.status_code}")
            return set()

        data = response.json()
        urls = set()

        #Nameservers ficam em data['nameservers'] com ldhName.
        for ns in data.get('nameservers', []):
            name = ns.get('ldhName', '').lower()
            if name and domain in name:
                urls.add(name)

        logger.info(f"RDAP: {len(urls)} nameservers")
        return urls
    except Exception as e:
        logger.error(f"RDAP error: {str(e)}")
        return set()


#Fontes_subdomínio

def buscar_crtsh(domain):
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

        subdomains = set()
        for entry in response.json():
            name = entry.get('name_value', '')
            for sub in name.split('\n'):
                sub = sub.strip().lower().lstrip('*.')
                if sub and sub.endswith(domain) and sub != domain:
                    subdomains.add(sub)
        return subdomains
    except Exception as e:
        logger.error(f"crt.sh error: {str(e)}")
        return set()


def buscar_hackertarget(domain):
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

        subdomains = set()
        for line in response.text.splitlines():
            if ',' in line:
                sub = line.split(',')[0].strip().lower()
                if sub and sub.endswith(domain) and sub != domain:
                    subdomains.add(sub)
        return subdomains
    except Exception as e:
        logger.error(f"HackerTarget error: {str(e)}")
        return set()


#Registro_de_fontes

FONTES_URL = {
    'wayback': buscar_wayback,
    'google': buscar_google,
    'whois': buscar_whois,
}

FONTES_SUBDOMINIO = {
    'crtsh': buscar_crtsh,
}

FONTES_FUNCOES = {**FONTES_URL, **FONTES_SUBDOMINIO}


#CLI

def main():
    parser = argparse.ArgumentParser(
        prog='onca',
        description=(
            "ONÇA - Open-source Network Crawler for Assets.\n"

            "  -o  domínio alvo (Obrigatório)\n"
            "  -n  palavra-chave (Nome/filtro)\n"
            "  -c  fontes de busca (Choice)\n"
            "  -a  arquivo de saída (Arquivo)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exemplo: python onca.py -o exemplo.com -n admin -c google crtsh -a saida.json -v",
    )
    parser.add_argument('-o', '--domain', required=True, help='Domínio alvo')
    parser.add_argument('-n', '--keyword', help='Palavra-chave (substring) para filtrar resultados')
    parser.add_argument(
        '-c', '--sources',
        nargs='+',
        choices=list(FONTES_FUNCOES.keys()),
        default=list(FONTES_FUNCOES.keys()),
        help='Fontes para busca (padrão: todas)',
    )
    parser.add_argument('-a', '--output', help='Arquivo de saída (.json ou .txt)')
    parser.add_argument('--strict', action='store_true',
                        help='Filtrar apenas URLs do domínio exato')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo detalhado')
    parser.add_argument('--delay', type=int, default=DELAY,
                        help=f'Delay entre fontes em segundos (padrão: {DELAY})')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    resultados = {'urls': set(), 'subdomains': set()}

    sources_list = list(args.sources)
    for i, source in enumerate(sources_list):
        if i > 0:
            time.sleep(args.delay)

        logger.info(f"Buscando em {source}...")

        try:
            if source == 'crtsh':
                new_subs = buscar_crtsh(args.domain)
                if not new_subs:
                    logger.info("crt.sh vazio ou falhou, tentando HackerTarget...")
                    new_subs = buscar_hackertarget(args.domain)
                resultados['subdomains'].update(new_subs)

            elif source == 'whois':
                new_urls = buscar_whois(args.domain)
                if not new_urls:
                    logger.info("WHOIS vazio ou falhou, tentando RDAP...")
                    new_urls = buscar_rdap(args.domain)
                resultados['urls'].update(new_urls)

            elif source == 'google':
                new_urls = buscar_google(args.domain, args.keyword)
                resultados['urls'].update(u for u in new_urls if u)

            else:
                new_urls = FONTES_URL[source](args.domain)
                resultados['urls'].update(u for u in new_urls if u)

        except Exception as e:
            logger.error(f"Erro em {source}: {str(e)}")
            continue

    #Filtro por palavra-chave: vale para TODAS as fontes
    if args.keyword:
        kw = args.keyword.lower()
        resultados['urls'] = {u for u in resultados['urls'] if kw in u.lower()}
        resultados['subdomains'] = {s for s in resultados['subdomains'] if kw in s.lower()}

    #Filtro estrito de domínio
    if args.strict:
        resultados['urls'] = {
            u for u in resultados['urls']
            if args.domain in urlparse(u).netloc
        }
        resultados['subdomains'] = {
            s for s in resultados['subdomains']
            if s == args.domain or s.endswith('.' + args.domain)
        }

    #Saída
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                if args.output.endswith('.json'):
                    json.dump({
                        'urls': sorted(resultados['urls']),
                        'subdomains': sorted(resultados['subdomains']),
                    }, f, indent=2, ensure_ascii=False)
                else:
                    if resultados['subdomains']:
                        f.write("=== SUBDOMAINS ===\n")
                        f.write('\n'.join(sorted(resultados['subdomains'])))
                        f.write("\n\n")
                    f.write("=== URLS ===\n")
                    f.write('\n'.join(sorted(resultados['urls'])))
            logger.info(
                f"Resultados salvos em {args.output} "
                f"({len(resultados['urls'])} URLs, "
                f"{len(resultados['subdomains'])} subdomínios)"
            )
        except Exception as e:
            logger.error(f"Erro ao salvar: {str(e)}")
    else:
        if resultados['subdomains']:
            print("=== SUBDOMAINS ===")
            for sub in sorted(resultados['subdomains']):
                print(sub)
        if resultados['urls']:
            print("\n=== URLS ===")
            for url in sorted(resultados['urls']):
                print(url)


if __name__ == '__main__':
    main()