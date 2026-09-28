"""Testes para onca.sources.google."""

import responses

from onca.sources import buscar_google

URL_GOOGLE = "https://www.google.com/search"


def _html_com_links(*urls):
    """Monta um HTML fake com links no formato que o Google usa."""
    links = "".join(
        f'<a href="/url?q={url}&amp;sa=U&amp;ved=abc">link</a>'
        for url in urls
    )
    return f"<html><body>{links}</body></html>"


def _adicionar_resposta(html, status=200):
    responses.add(
        responses.GET,
        URL_GOOGLE,
        body=html,
        status=status,
        content_type="text/html",
    )


@responses.activate
def test_buscar_google_sucesso():
    _adicionar_resposta(_html_com_links(
        "https://example.com/",
        "https://example.com/sobre",
    ))

    resultado = buscar_google("example.com")

    assert resultado == {
        "https://example.com/",
        "https://example.com/sobre",
    }


@responses.activate
def test_buscar_google_ignora_links_de_outro_dominio():
    _adicionar_resposta(_html_com_links(
        "https://example.com/",
        "https://outro.com/",
    ))

    resultado = buscar_google("example.com")

    assert resultado == {"https://example.com/"}


@responses.activate
def test_buscar_google_erro_http():
    _adicionar_resposta("", status=429)

    resultado = buscar_google("example.com")

    assert resultado == set()


@responses.activate
def test_buscar_google_sem_links():
    _adicionar_resposta("<html><body>Nada aqui</body></html>")

    resultado = buscar_google("example.com")

    assert resultado == set()


@responses.activate
def test_buscar_google_ignora_links_malformados():
    _adicionar_resposta(
        '<html><body>'
        '<a href="/url?q=nao-e-url&amp;sa=U">x</a>'
        '<a href="/url?q=https://example.com/ok&amp;sa=U">y</a>'
        '</body></html>'
    )

    resultado = buscar_google("example.com")

    assert resultado == {"https://example.com/ok"}


@responses.activate
def test_buscar_google_com_keyword():
    """O keyword é passado para a query, mas o filtro final não é aplicado aqui."""
    _adicionar_resposta(_html_com_links(
        "https://example.com/admin",
        "https://example.com/login",
    ))

    resultado = buscar_google("example.com", keyword="admin")

    # O buscar_google não filtra por keyword (isso é feito no cli.py)
    assert resultado == {
        "https://example.com/admin",
        "https://example.com/login",
    }
