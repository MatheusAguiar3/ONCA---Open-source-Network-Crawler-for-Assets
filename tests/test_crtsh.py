"""Testes para onca.sources.crtsh."""

import responses

from onca.sources import buscar_crtsh

URL_CRTSH = "https://crt.sh/?q=%25.example.com&output=json"


def _adicionar_resposta(json_data, status=200):
    responses.add(responses.GET, URL_CRTSH, json=json_data, status=status)


@responses.activate
def test_buscar_crtsh_sucesso():
    _adicionar_resposta([
        {"name_value": "www.example.com"},
        {"name_value": "api.example.com"},
        {"name_value": "mail.example.com"},
    ])

    resultado = buscar_crtsh("example.com")

    assert resultado == {"www.example.com", "api.example.com", "mail.example.com"}


@responses.activate
def test_buscar_crtsh_remove_wildcard_e_ignora_dominio_raiz():
    """*.example.com vira example.com, mas example.com é filtrado
    (a função só retorna subdomínios, não o domínio raiz)."""
    _adicionar_resposta([
        {"name_value": "*.example.com"},
        {"name_value": "www.example.com"},
    ])

    resultado = buscar_crtsh("example.com")

    assert resultado == {"www.example.com"}


@responses.activate
def test_buscar_crtsh_multiplos_nomes_por_certificado():
    _adicionar_resposta([
        {"name_value": "www.example.com\napi.example.com"},
    ])

    resultado = buscar_crtsh("example.com")

    assert resultado == {"www.example.com", "api.example.com"}


@responses.activate
def test_buscar_crtsh_erro_http():
    _adicionar_resposta([], status=500)

    resultado = buscar_crtsh("example.com")

    assert resultado == set()


@responses.activate
def test_buscar_crtsh_ignora_dominios_diferentes():
    _adicionar_resposta([
        {"name_value": "www.example.com"},
        {"name_value": "www.outro.com"},
    ])

    resultado = buscar_crtsh("example.com")

    assert resultado == {"www.example.com"}


@responses.activate
def test_buscar_crtsh_resposta_vazia():
    _adicionar_resposta([])

    resultado = buscar_crtsh("example.com")

    assert resultado == set()
