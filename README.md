![[ONCA Logo](assets/ONCA_Logo.jpg)](https://github.com/MatheusAguiar3/ONCA---Open-source-Network-Crawler-for-Assets/blob/main/assets/ONCA_logo.jpg)


# ONÇA - [Open-source Network Crawler for Assets]

    ██████╗  ███╗   ██╗ ██████╗  █████╗
    ██╔══██╗ ████╗  ██║██╔════╝ ██╔══██╗
    ██║  ██║ ██╔██╗ ██║██║      ███████║
    ██║  ██║ ██║╚██╗██║██║      ██╔══██║
    ██████╔╝ ██║ ╚████║╚██████╗ ██║  ██║
    ╚═════╝  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝
        [Open-source Network Crawler for Assets]

## O que é

ONÇA é uma ferramenta Python para descoberta de ativos web a partir de um
domínio. Ela é útil para:

- Pentesters e equipes de segurança mapeando superfície de ataque
- Bug bounty hunters
- Administradores de sistemas
- Estudantes de cibersegurança

**O que a ONÇA faz:**

- Consulta Wayback Machine, Google e WHOIS/RDAP para encontrar URLs
- Consulta crt.sh (e HackerTarget como fallback) para encontrar subdomínios
- Filtra por palavra-chave
- Salva resultados em texto ou JSON
- Aplica filtro estrito de domínio

**O que a ONÇA NÃO faz:**

- Não faz varredura de portas
- Não faz brute force de subdomínios
- Não usa API oficial de nenhuma fonte (é scraping ou API pública)
- Não garante cobertura completa

## O acrônimo ONÇA

Os argumentos principais formam o nome da ferramenta:

| Letra | Flag | O que faz |
|---|---|---|
| **O** | `-o` | Domínio alvo (**O**brigatório) |
| **N** | `-n` | Palavra-chave (**N**ome/filtro) |
| **Ç** | `-c` | Fontes de busca (**C**hoice) |
| **A** | `-a` | Arquivo de saída (**A**rquivo) |

`--strict`, `-v` e `--delay` são complementares e não entram no acrônimo.

## Instalação

### Requisitos

- Python 3.10+
- Git (opcional)

### Passos

    git clone https://github.com/MatheusAguiar3/ONCA---Open-source-Network-Crawler-for-Assets.git
    cd ONCA---Open-source-Network-Crawler-for-Assets

    python3 -m venv venv
    source venv/bin/activate   # Linux/Mac
    # venv\Scripts\activate    # Windows

    pip install -e .

## Uso

### Busca básica

    python onca.py -o exemplo.com

### Busca por palavra-chave

    python onca.py -o exemplo.com -n admin -v

### Fontes específicas

    python onca.py -o exemplo.com -c google whois
    python onca.py -o exemplo.com -c crtsh

### Salvar resultados

    python onca.py -o exemplo.com -c crtsh -a resultados.json
    python onca.py -o exemplo.com -c crtsh -a resultados.txt

### Filtro estrito de domínio

    python onca.py -o exemplo.com --strict

### Ajustar o delay entre fontes

    python onca.py -o exemplo.com -c wayback google --delay 5

### Comando instalado

Se você instalou com `pip install -e .`, pode usar o comando `onca` direto:

    onca -o exemplo.com -c crtsh

## Argumentos

| Argumento | Descrição | Padrão | Obrigatório |
|---|---|---|---|
| `-o, --domain` | Domínio alvo | — | Sim |
| `-n, --keyword` | Palavra-chave (substring) para filtrar | — | Não |
| `-c, --sources` | Fontes: `wayback`, `google`, `whois`, `crtsh` | todas | Não |
| `-a, --output` | Arquivo de saída (`.json` ou `.txt`) | stdout | Não |
| `--strict` | Filtra apenas URLs do domínio exato | desligado | Não |
| `-v, --verbose` | Log detalhado | desligado | Não |
| `--delay` | Delay entre fontes em segundos | 3 | Não |

## Fontes

### Fontes de URL

| Fonte | O que faz | Requer API key? | Observações |
|---|---|---|---|
| `wayback` | URLs históricas via Wayback Machine | Não | API pública (CDX) |
| `google` | URLs indexadas via scraping | Não | Pode ser bloqueado; sujeito a ToS |
| `whois` | Nameservers via WHOIS/RDAP | Não | `python-whois` + fallback `rdap.org` |

### Fontes de subdomínio

| Fonte | O que faz | Requer API key? | Observações |
|---|---|---|---|
| `crtsh` | Subdomínios via Certificate Transparency | Não | `crt.sh` + fallback HackerTarget |

> **Atenção:** a fonte `google` faz scraping de HTML. Isso pode violar
> os Termos de Serviço e ser bloqueado. Use com moderação.

> **Sobre subdomínios:** o `crtsh` só encontra subdomínios que já tiveram
> certificado SSL emitido. Subdomínios cobertos por certificado wildcard
> (`*.exemplo.com`) não aparecem.

## Testes

    pip install -e ".[dev]"
    pytest tests/ -v

**69 testes**, cobrindo:

- `core/` — sanitize, session
- `sources/` — cada fonte com mock de HTTP
- `output/` — JSON e TXT com arquivos temporários
- `cli/` — argumentos, filtros, fallback entre fontes

## Limitações conhecidas

- `google` faz scraping e pode ser bloqueado
- `crtsh` pode retornar 502 ocasionalmente (o banco dele atualiza devagar)
- Subdomínios cobertos por wildcard não aparecem
- Sem CI ainda (planejado)
- Sem cobertura de código (planejado)

## Aviso legal

ONÇA é destinada a **fins educacionais e de teste autorizado**.
**Não use** em sistemas sem permissão explícita. O uso indevido é de
inteira responsabilidade do usuário.

## Licença

MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contato

- LinkedIn: https://www.linkedin.com/in/matheus-aguiar3/
- X: https://x.com/_yaguarete

projeto criado por **yaguarete** para auxiliar no mapeamento de superfície de aplicações web e estudos em cibersegurança.
