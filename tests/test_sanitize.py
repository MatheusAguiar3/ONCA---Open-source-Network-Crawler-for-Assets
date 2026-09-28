"""Testes para onca.core.sanitize."""

import pytest

from onca.core import sanitize_url


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("https://example.com", "https://example.com"),
        ("http://example.com/path", "http://example.com/path"),
        ("https://sub.example.com/path?q=1", "https://sub.example.com/path?q=1"),
        ("  https://example.com  ", "https://example.com"),
        ("ftp://files.example.com", "ftp://files.example.com"),
    ],
)
def test_sanitize_url_aceita_urls_validas(entrada, esperado):
    assert sanitize_url(entrada) == esperado


@pytest.mark.parametrize(
    "entrada",
    [
        None,
        "",
        "nao-e-url",
        "example.com",          # sem scheme
        "/apenas/caminho",      # sem netloc
        "javascript:alert(1)",  # sem netloc
    ],
)
def test_sanitize_url_rejeita_entradas_invalidas(entrada):
    assert sanitize_url(entrada) is None


def test_sanitize_url_rejeita_tipos_nao_string():
    assert sanitize_url(123) is None
    assert sanitize_url([]) is None
    assert sanitize_url({}) is None
