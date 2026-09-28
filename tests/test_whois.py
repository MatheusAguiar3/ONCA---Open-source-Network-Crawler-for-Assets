"""Testes para onca.sources.whois."""

from unittest.mock import MagicMock, patch

import responses

from onca.sources import buscar_rdap, buscar_whois


# ---------- buscar_whois (mock da lib python-whois) ----------


def test_buscar_whois_sucesso_com_lista():
    fake_whois = MagicMock()
    fake_whois.name_servers = ["ns1.example.com", "ns2.example.com"]

    with patch("whois.whois", return_value=fake_whois):
        resultado = buscar_whois("example.com")

    assert resultado == {"ns1.example.com", "ns2.example.com"}


def test_buscar_whois_sucesso_com_string_unica():
    fake_whois = MagicMock()
    fake_whois.name_servers = "ns1.example.com"

    with patch("whois.whois", return_value=fake_whois):
        resultado = buscar_whois("example.com")

    assert resultado == {"ns1.example.com"}


def test_buscar_whois_ignora_nameservers_de_outro_dominio():
    fake_whois = MagicMock()
    fake_whois.name_servers = ["ns1.example.com", "ns1.outro.com"]

    with patch("whois.whois", return_value=fake_whois):
        resultado = buscar_whois("example.com")

    assert resultado == {"ns1.example.com"}


def test_buscar_whois_sem_nameservers():
    fake_whois = MagicMock()
    fake_whois.name_servers = None

    with patch("whois.whois", return_value=fake_whois):
        resultado = buscar_whois("example.com")

    assert resultado == set()


def test_buscar_whois_erro_na_lib():
    with patch("whois.whois", side_effect=Exception("boom")):
        resultado = buscar_whois("example.com")

    assert resultado == set()


def test_buscar_whois_remove_ponto_final():
    fake_whois = MagicMock()
    fake_whois.name_servers = ["ns1.example.com.", "ns2.example.com."]

    with patch("whois.whois", return_value=fake_whois):
        resultado = buscar_whois("example.com")

    assert resultado == {"ns1.example.com", "ns2.example.com"}


# ---------- buscar_rdap (mock HTTP) ----------

URL_RDAP = "https://rdap.org/domain/example.com"


def _adicionar_resposta(json_data, status=200):
    responses.add(responses.GET, URL_RDAP, json=json_data, status=status)


@responses.activate
def test_buscar_rdap_sucesso():
    _adicionar_resposta({
        "nameservers": [
            {"ldhName": "NS1.EXAMPLE.COM"},
            {"ldhName": "NS2.EXAMPLE.COM"},
        ]
    })

    resultado = buscar_rdap("example.com")

    assert resultado == {"ns1.example.com", "ns2.example.com"}


@responses.activate
def test_buscar_rdap_ignora_nameservers_de_outro_dominio():
    _adicionar_resposta({
        "nameservers": [
            {"ldhName": "NS1.EXAMPLE.COM"},
            {"ldhName": "NS1.OUTRO.COM"},
        ]
    })

    resultado = buscar_rdap("example.com")

    assert resultado == {"ns1.example.com"}


@responses.activate
def test_buscar_rdap_erro_http():
    _adicionar_resposta({}, status=500)

    resultado = buscar_rdap("example.com")

    assert resultado == set()


@responses.activate
def test_buscar_rdap_sem_nameservers():
    _adicionar_resposta({})

    resultado = buscar_rdap("example.com")

    assert resultado == set()
