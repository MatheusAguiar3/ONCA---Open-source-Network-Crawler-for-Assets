"""Testes para onca.cli."""

import json
import sys

import pytest

from onca import cli


# ---------- Helpers ----------


def _rodar_cli(monkeypatch, *args):
    """Roda a CLI com argumentos simulados."""
    monkeypatch.setattr(sys, "argv", ["onca", *args])
    cli.main()


# ---------- Ajuda ----------


def test_help(capsys, monkeypatch):
    with pytest.raises(SystemExit):
        _rodar_cli(monkeypatch, "--help")
    captured = capsys.readouterr()
    assert "ONÇA" in captured.out or "ONCA" in captured.out
    assert "-o" in captured.out


def test_domain_obrigatorio(capsys, monkeypatch):
    with pytest.raises(SystemExit):
        _rodar_cli(monkeypatch)
    captured = capsys.readouterr()
    assert "required" in captured.err.lower() or "obrigat" in captured.err.lower()


# ---------- Sem -a (imprime no stdout) ----------


def test_imprime_urls_e_subdominios(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "_buscar_em_fonte",
        lambda source, domain, keyword, resultados: (
            resultados["urls"].add("https://example.com/"),
            resultados["subdomains"].add("www.example.com"),
        ),
    )
    _rodar_cli(monkeypatch, "-o", "example.com", "-c", "wayback", "--delay", "0")
    captured = capsys.readouterr()
    assert "https://example.com/" in captured.out
    assert "www.example.com" in captured.out


# ---------- Com -a (salva arquivo) ----------


def test_salva_json(tmp_path, monkeypatch):
    arquivo = tmp_path / "saida.json"
    monkeypatch.setattr(
        cli,
        "_buscar_em_fonte",
        lambda source, domain, keyword, resultados: (
            resultados["urls"].add("https://example.com/"),
            resultados["subdomains"].add("www.example.com"),
        ),
    )
    _rodar_cli(monkeypatch, "-o", "example.com", "-c", "wayback", "-a", str(arquivo), "--delay", "0")
    assert arquivo.exists()
    with open(arquivo, encoding="utf-8") as f:
        data = json.load(f)
    assert data["urls"] == ["https://example.com/"]
    assert data["subdomains"] == ["www.example.com"]


def test_salva_txt(tmp_path, monkeypatch):
    arquivo = tmp_path / "saida.txt"
    monkeypatch.setattr(
        cli,
        "_buscar_em_fonte",
        lambda source, domain, keyword, resultados: (
            resultados["urls"].add("https://example.com/"),
        ),
    )
    _rodar_cli(monkeypatch, "-o", "example.com", "-c", "wayback", "-a", str(arquivo), "--delay", "0")
    assert arquivo.exists()
    conteudo = arquivo.read_text(encoding="utf-8")
    assert "https://example.com/" in conteudo


# ---------- Filtro -n ----------


def test_filtro_keyword(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "_buscar_em_fonte",
        lambda source, domain, keyword, resultados: (
            resultados["urls"].update({"https://example.com/admin", "https://example.com/sobre"}),
            resultados["subdomains"].add("admin.example.com"),
        ),
    )
    _rodar_cli(monkeypatch, "-o", "example.com", "-c", "wayback", "-n", "admin", "--delay", "0")
    captured = capsys.readouterr()
    assert "https://example.com/admin" in captured.out
    assert "admin.example.com" in captured.out
    assert "https://example.com/sobre" not in captured.out


# ---------- Filtro --strict ----------


def test_filtro_strict(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "_buscar_em_fonte",
        lambda source, domain, keyword, resultados: (
            resultados["urls"].update({"https://example.com/", "https://outro.com/"}),
        ),
    )
    _rodar_cli(monkeypatch, "-o", "example.com", "-c", "wayback", "--strict", "--delay", "0")
    captured = capsys.readouterr()
    assert "https://example.com/" in captured.out
    assert "https://outro.com/" not in captured.out


# ---------- Fontes ----------


def test_crtsh_fallback_para_hackertarget(monkeypatch):
    chamadas = {"crtsh": 0, "hackertarget": 0}

    def fake_crtsh(domain):
        chamadas["crtsh"] += 1
        return set()

    def fake_hackertarget(domain):
        chamadas["hackertarget"] += 1
        return {"www.example.com"}

    monkeypatch.setattr(cli, "FONTES_FUNCOES", {"crtsh": fake_crtsh})
    monkeypatch.setattr(cli, "buscar_hackertarget", fake_hackertarget)

    resultados = {"urls": set(), "subdomains": set()}
    cli._buscar_em_fonte("crtsh", "example.com", None, resultados)

    assert chamadas["crtsh"] == 1
    assert chamadas["hackertarget"] == 1
    assert resultados["subdomains"] == {"www.example.com"}


def test_whois_fallback_para_rdap(monkeypatch):
    chamadas = {"whois": 0, "rdap": 0}

    def fake_whois(domain):
        chamadas["whois"] += 1
        return set()

    def fake_rdap(domain):
        chamadas["rdap"] += 1
        return {"ns1.example.com"}

    monkeypatch.setattr(cli, "buscar_whois", fake_whois)
    monkeypatch.setattr(cli, "buscar_rdap", fake_rdap)

    resultados = {"urls": set(), "subdomains": set()}
    cli._buscar_em_fonte("whois", "example.com", None, resultados)

    assert chamadas["whois"] == 1
    assert chamadas["rdap"] == 1
    assert resultados["urls"] == {"ns1.example.com"}
