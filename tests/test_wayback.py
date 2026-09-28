"""Testes para onca.sources.wayback."""

import responses

from onca.sources import buscar_wayback

URL_WAYBACK = "https://web.archive.org/cdx/search/cdx?url=example.com/*&output=json"


def _adicionar_resposta(json_data, status=200):
    """Registra uma resposta do Wayback para a URL exata."""
    responses.add(
        responses.GET,
        URL_WAYBACK,
        json=json_data,
        status=status,
    )


@responses.activate
def test_buscar_wayback_sucesso():
    _adicionar_resposta([
        ["timestamp", "original", "mimetype", "statuscode", "digest", "length"],
        ["20200101000000", "http://example.com/", "text/html", "200", "abc", "123"],
        ["20200102000000", "https://example.com/sobre", "text/html", "200", "def", "456"],
    ])

    resultado = buscar_wayback("example.com")

    assert resultado == {
        "http://example.com/",
        "https://example.com/sobre",
    }


@responses.activate
def test_buscar_wayback_erro_http():
    _adicionar_resposta([], status=500)

    resultado = buscar_wayback("example.com")

    assert resultado == set()


@responses.activate
def test_buscar_wayback_resposta_vazia():
    _adicionar_resposta([
        ["timestamp", "original", "mimetype", "statuscode", "digest", "length"],
    ])

    resultado = buscar_wayback("example.com")

    assert resultado == set()


@responses.activate
def test_buscar_wayback_ignora_urls_invalidas():
    _adicionar_resposta([
        ["timestamp", "original", "mimetype", "statuscode", "digest", "length"],
        ["20200101000000", "nao-e-url", "text/html", "200", "abc", "123"],
        ["20200102000000", "https://example.com/ok", "text/html", "200", "def", "456"],
    ])

    resultado = buscar_wayback("example.com")

    assert resultado == {"https://example.com/ok"}
