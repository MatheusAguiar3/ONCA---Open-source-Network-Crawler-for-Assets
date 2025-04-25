#ONÇA - Open-source Network Crawler for Assets
#            ██████╗  ███╗   ██╗ ██████╗  █████╗            
#            ██╔══██╗ ████╗  ██║██╔════╝ ██╔══██╗           
#            ██║  ██║ ██╔██╗ ██║██║      ███████║           
#            ██║  ██║ ██║╚██╗██║██║      ██╔══██║           
#            ██████╔╝ ██║ ╚████║╚██████╗ ██║  ██║           
#            ╚═════╝  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝           
#        [Open-source Network Crawler for Assets]
#
#!/usr/bin/env python3

import argparse
import requests
import time
from bs4 import BeautifulSoup
import logging
import json
from urllib.parse import urlparse, quote
import re
from random import choice
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
]
DELAY = 3  # Delay base entre requisições (segundos)
DELAY_DOMAINTOOLS = 30  # Delay específico para DomainTools

# Configuração de sessão com retry
def setup_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Funções auxiliares
def get_random_headers():
    return {
        'User-Agent': choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/'
    }

def sanitize_url(url):
    try:
        parsed = urlparse(url)
        if all([parsed.scheme, parsed.netloc]):
            return url.encode('utf-8').decode('utf-8', 'ignore')
        return None
    except:
        return None

# Funções de busca
def buscar_wayback(domain):
    try:
        session = setup_session()
        url = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json"
        response = session.get(
            url,
            headers=get_random_headers(),
            timeout=20
        )
        urls = set()
        for item in response.json()[1:]:
            url = sanitize_url(item[2])
            if url:
                urls.add(url)
        return urls
    except Exception as e:
        logger.error(f"Wayback Machine error: {str(e)}")
        return set()

def buscar_google(domain, keyword=None):
    try:
        query = f"site:{domain}"
        if keyword:
            query += f" {keyword}"
        
        session = setup_session()
        url = "https://www.google.com/search"
        params = {'q': query, 'num': 50}
        
        response = session.get(
            url,
            params=params,
            headers=get_random_headers(),
            timeout=15
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        
        urls = set()
        for link in soup.select('a[href^="/url?q="]'):
            href = link['href'].split('&')[0].replace('/url?q=', '')
            url = sanitize_url(href)
            if url and domain in url:
                urls.add(url)
        return urls
    except Exception as e:
        logger.error(f"Google search error: {str(e)}")
        return set()

def buscar_domaintools(domain):
    try:
        session = setup_session()
        url = f"https://whois.domaintools.com/{quote(domain)}"
        
        # Primeira requisição para estabelecer sessão
        response = session.get(
            url,
            headers=get_random_headers(),
            timeout=20
        )
        
        if response.status_code == 429:
            logger.error("DomainTools: Rate limit exceeded")
            return set()
            
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = set()
        
        # Extrai informações da seção de histórico
        history_div = soup.find('div', id='whois-history')
        if history_div:
            for link in history_div.find_all('a', href=True):
                href = link['href']
                if href.startswith('http') and domain in href:
                    clean_url = sanitize_url(href)
                    if clean_url:
                        urls.add(clean_url)
        
        # Extrai servidores DNS
        dns_table = soup.find('table', id='servers-table')
        if dns_table:
            for row in dns_table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    server = cols[1].get_text(strip=True)
                    if server and domain in server:
                        urls.add(f"https://{server}")
        
        # Extrai registros MX
        mx_section = soup.find('h4', text=re.compile('MX Records'))
        if mx_section:
            mx_table = mx_section.find_next('table')
            if mx_table:
                for row in mx_table.find_all('tr')[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        mx = cols[1].get_text(strip=True)
                        if mx.endswith('.'):
                            mx = mx[:-1]
                        if mx and domain in mx:
                            urls.add(f"mx://{mx}")
        
        logger.info(f"DomainTools: Found {len(urls)} records")
        return urls
        
    except Exception as e:
        logger.error(f"DomainTools error: {str(e)}")
        return set()

# Dicionário de fontes
FONTES_FUNCOES = {
    'wayback': buscar_wayback,
    'google': buscar_google,
    'domaintools': buscar_domaintools
}

def main():
    parser = argparse.ArgumentParser(
        description="ONCA - Open-source Network Crawler for Assets",
        epilog="Exemplo: python onca.py -o exemplo.com -c google domaintools -v"
    )
    parser.add_argument('-o', '--domain', required=True, help='Domínio alvo')
    parser.add_argument('-n', '--keyword', help='Palavra-chave para busca refinada')
    parser.add_argument('-c', '--sources', nargs='+', choices=FONTES_FUNCOES.keys(),
                      help='Fontes para busca (padrão: todas)', default=FONTES_FUNCOES.keys())
    parser.add_argument('-a', '--output', help='Arquivo de saída')
    parser.add_argument('--strict', action='store_true', help='Filtrar apenas domínio exato')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo detalhado')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    urls = set()
    
    for source in args.sources:
        logger.info(f"Searching in {source}...")
        
        # Delay especial para DomainTools
        if source == 'domaintools':
            time.sleep(DELAY_DOMAINTOOLS)
        else:
            time.sleep(DELAY)
        
        try:
            if source == 'google':
                new_urls = FONTES_FUNCOES[source](args.domain, args.keyword)
            else:
                new_urls = FONTES_FUNCOES[source](args.domain)
            
            urls.update(url for url in new_urls if url)
            
        except Exception as e:
            logger.error(f"Error in {source}: {str(e)}")
            continue
    
    # Filtro de domínio estrito
    if args.strict:
        urls = {url for url in urls if args.domain in urlparse(url).netloc}
    
    # Saída dos resultados
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                if args.output.endswith('.json'):
                    json.dump(sorted(urls), f, indent=2)
                else:
                    f.write('\n'.join(sorted(urls)))
            logger.info(f"Results saved to {args.output} ({len(urls)} items)")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
    else:
        for url in sorted(urls):
            print(url)

if __name__ == '__main__':
    main()