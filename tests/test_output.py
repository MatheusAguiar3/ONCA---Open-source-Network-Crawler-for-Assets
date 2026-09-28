"""Testes para onca.output."""

import json

from onca.output import salvar_json, salvar_txt


# ---------- salvar_json ----------


def test_salvar_json_cria_arquivo(tmp_path):
    arquivo = tmp_path / "saida.json"
    salvar_json(str(arquivo), {"https://example.com"}, {"www.example.com"})
    assert arquivo.exists()


def test_salvar_json_estrutura_correta(tmp_path):
    arquivo = tmp_path / "saida.json"
    salvar_json(
        str(arquivo),
        {"https://example.com", "https://example.com/sobre"},
        {"www.example.com", "api.example.com"},
    )

    with open(arquivo, encoding="utf-8") as f:
        data = json.load(f)

    assert data["urls"] == ["https://example.com", "https://example.com/sobre"]
    assert data["subdomains"] == ["api.example.com", "www.example.com"]


def test_salvar_json_urls_ordenadas(tmp_path):
    arquivo = tmp_path / "saida.json"
    salvar_json(
        str(arquivo),
        {"https://z.com", "https://a.com", "https://m.com"},
        set(),
    )

    with open(arquivo, encoding="utf-8") as f:
        data = json.load(f)

    assert data["urls"] == ["https://a.com", "https://m.com", "https://z.com"]


def test_salvar_json_vazio(tmp_path):
    arquivo = tmp_path / "saida.json"
    salvar_json(str(arquivo), set(), set())

    with open(arquivo, encoding="utf-8") as f:
        data = json.load(f)

    assert data == {"urls": [], "subdomains": []}


# ---------- salvar_txt ----------


def test_salvar_txt_cria_arquivo(tmp_path):
    arquivo = tmp_path / "saida.txt"
    salvar_txt(str(arquivo), {"https://example.com"}, {"www.example.com"})
    assert arquivo.exists()


def test_salvar_txt_estrutura_correta(tmp_path):
    arquivo = tmp_path / "saida.txt"
    salvar_txt(
        str(arquivo),
        {"https://example.com"},
        {"www.example.com"},
    )

    conteudo = arquivo.read_text(encoding="utf-8")

    assert "=== SUBDOMAINS ===" in conteudo
    assert "www.example.com" in conteudo
    assert "=== URLS ===" in conteudo
    assert "https://example.com" in conteudo


def test_salvar_txt_sem_subdominios_nao_imprime_secao(tmp_path):
    arquivo = tmp_path / "saida.txt"
    salvar_txt(str(arquivo), {"https://example.com"}, set())

    conteudo = arquivo.read_text(encoding="utf-8")

    assert "=== SUBDOMAINS ===" not in conteudo
    assert "=== URLS ===" in conteudo


def test_salvar_txt_ordenado(tmp_path):
    arquivo = tmp_path / "saida.txt"
    salvar_txt(
        str(arquivo),
        {"https://z.com", "https://a.com", "https://m.com"},
        set(),
    )

    conteudo = arquivo.read_text(encoding="utf-8")
    linhas = [
        linha for linha in conteudo.splitlines()
        if linha.startswith("https://")
    ]

    assert linhas == ["https://a.com", "https://m.com", "https://z.com"]


def test_salvar_txt_vazio(tmp_path):
    arquivo = tmp_path / "saida.txt"
    salvar_txt(str(arquivo), set(), set())

    conteudo = arquivo.read_text(encoding="utf-8")

    assert "=== SUBDOMAINS ===" not in conteudo
    assert "=== URLS ===" in conteudo
