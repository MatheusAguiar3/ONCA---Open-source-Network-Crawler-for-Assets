"""Testes para onca.sources.hackertarget."""

import responses

from onca.sources import buscar_hackertarget

URL_HACKERTARGET = (
    "https://api.hackertarget.com/hostsearch/?q=example.com"
)


def _adicionar_resposta(texto, status=200):
    responses.add(
        responses.GET,
        URL_HACKERTARGET,
        body=texto,
        status=status,
        content_type="text/plain",
    )


@responses.activate
def test_buscar_hackertarget_sucesso():
    _adicionar_resposta(
        "www.example.com,1.2.3.4\n"
        "api.example.com,5.6.7.8\n"
        "mail.example.com,9.10.11.12\n"
    )

    resultado = buscar_hackertarget("example.com")

    assert resultado == {
        "www.example.com",
        "api.example.com",
        "mail.example.com",
    }


@responses.activate
def test_buscar_hackertarget_erro_http():
    _adicionar_resposta("", status=500)

    resultado = buscar_hackertarget("example.com")

    assert resultado == set()


@responses.activate
def test_buscar_hackertarget_ignora_dominios_diferentes():
    _adicionar_resposta(
        "www.example.com,1.2.3.4\n"
        "www.outro.com,5.6.7.8\n"
    )

    resultado = buscar_hackertarget("example.com")

    assert resultado == {"www.example.com"}


@responses.activate
def test_buscar_hackertarget_ignora_dominio_raiz():
    _adicionar_resposta(
        "example.com,1.2.3.4\n"
        "www.example.com,5.6.7.8\n"
    )

    resultado = buscar_hackertarget("example.com")

    assert resultado == {"www.example.com"}


@responses.activate
def test_buscar_hackertarget_resposta_vazia():
    _adicionar_resposta("")

    resultado = buscar_hackertarget("example.com")

    assert resultado == set()


@responses.activate
def test_buscar_hackertarget_linhas_sem_virgula_sao_ignoradas():
    _adicionar_resposta(
        "linha sem virgula\n"
        "www.example.com,1.2.3.4\n"
        "outra linha invalida\n"
    )

    resultado = buscar_hackertarget("example.com")

    assert resultado == {"www.example.com"}


@responses.activate
def test_buscar_hackertarget_aceita_resposta_de_erro_textual():
    """HackerTarget às vezes retorna 'error check your search parameter'
    com status 200. Nesse caso, não deve adicionar nada."""
    _adicionar_resposta("error check your search parameter")

    resultado = buscar_hackertarget("example.com")

    assert resultado == set()
