![[ONCA Logo](assets/ONCA_Logo.jpg)](https://github.com/MatheusAguiar3/ONCA---Open-source-Network-Crawler-for-Assets/blob/main/assets/ONCA_logo.jpg)


# 🐾 ONÇA - [Open-source Network Crawler for Assets]

## 📌 **Visão Geral**

ONÇA é uma ferramenta Python para descoberta de ativos web, projetada para ajudar profissionais de segurança e equipes de TI a mapear a superfície de ataque/estudo de seus sistemas. Com capacidade de identificar subdomínios, URLs públicas e recursos expostos, ideal para:

- **Pentesters** e equipes de segurança
    
- **Bug bounty hunters**
    
- Administradores de sistemas

- **estudantes de cibersegurança**


✅ Integração com **DomainTools WHOIS**  
✅ Busca por **palavras-chave específicas** (ex: "admin", "login")  
✅ Suporte a **Wayback Machine, Google e crt.sh**

---

## 🛠 **Instalação Fácil**

### Pré-requisitos:

- Python 3.6+
    
- Git (opcional)    
# Clone o repositório (opcional)
`git clone https://github.com/seu-usuario/ONCA.git`
`cd ONCA`

# Instale as dependências
`pip install -r requirements.txt`

---

## 🚀 **Como Usar (Exemplos Práticos)**

### 1. Busca básica em um domínio:

bash

`python onca.py -o exemplo.com`

### 2. Busca por palavra-chave (ex: "admin"):

bash

`python onca.py -o nubank.com.br -n admin -v`

### 3. Usando fontes específicas (Google + DomainTools):

bash

`python onca.py -o alvo.com -c google domaintools`

### 4. Salvar resultados em CSV:

bash

`python onca.py -o alvo.com -a resultados.csv`

---

## 🔧 **Argumentos Principais**

| Comando      | Descrição                           | Exemplo             |
| ------------ | ----------------------------------- | ------------------- |
| `-o DOMÍNIO` | Domínio alvo (obrigatório)          | `-o site.com.br`    |
| `-n PALAVRA` | Busca por palavra-chave             | `-n "painel admin"` |
| `-c FONTES`  | Escolha fontes de busca             | `-c google wayback` |
| `-a ARQUIVO` | Salva resultados em arquivo         | `-a resultados.txt` |
| `--strict`   | Filtra apenas URLs do domínio exato | `--strict`          |
| `-v`         | Modo detalhado (verbose)            | `-v`                |

---

## 🌐 **Fontes de Busca Disponíveis**

| Fonte           | O que encontra?                  | Exemplo de uso   |
| --------------- | -------------------------------- | ---------------- |
| **Google**      | URLs indexadas                   | `-c google`      |
| **Wayback**     | Histórico de páginas             | `-c wayback`     |
| **DomainTools** | Subdomínios, DNS e WHOIS         | `-c domaintools` |
| **crt.sh**      | Subdomínios via certificados SSL | `-c crtsh`       |

---

## ❓ **FAQ (Perguntas Frequentes)**

### 1. "A ONCA pode ser bloqueada pelo Google?"

Sim. Para evitar:

- Use delays (`DELAY = 5` no código)
    
- Combine fontes (`-c wayback crtsh`)
    

### 2. "Como buscar painéis de administração?"

bash

`python onca.py -o alvo.com -n "admin login" -c google`

### 3. "Não encontrei resultados. O que fazer?"

- Tente variações: `"painel"`, `"sistema"`, `"acesso restrito"`
    
- Verifique se o domínio está indexado:
    
    bash
    
    `python onca.py -o alvo.com -c wayback`

## 📬 **Contato**
linkedin: https://www.linkedin.com/in/matheus-aguiar3/

x(twitter): https://x.com/_yaguarete

Encontrou um bug? Quer sugerir uma melhoria?  
Abra uma **issue** no GitHub  :)

## ⚠️ Aviso Legal

a [onça] é para **fins educacionais e de teste autorizado**.  
**Não use** em sistemas sem permissão. O uso indevido é de inteira responsabilidade do usuário.

## 🐆Sobre

projeto criado por **matheus aguiar** para auxiliar no mapeamento de superfície de aplicações web e estudos em cibersegurança.
