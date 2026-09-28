"""Testes para onca.core.session."""

import requests

from onca.core import USER_AGENTS, get_random_headers, setup_session


def test_setup_session_retorna_session():
    session = setup_session()
    assert isinstance(session, requests.Session)


def test_setup_session_tem_adapters_montados():
    session = setup_session()
    assert "http://" in session.adapters
    assert "https://" in session.adapters


def test_user_agents_nao_esta_vazio():
    assert len(USER_AGENTS) >= 1
    for ua in USER_AGENTS:
        assert isinstance(ua, str)
        assert ua.startswith("Mozilla/")


def test_get_random_headers_tem_chaves_esperadas():
    headers = get_random_headers()
    for chave in ("User-Agent", "Accept", "Accept-Language", "Referer"):
        assert chave in headers


def test_get_random_headers_usa_um_dos_user_agents():
    headers = get_random_headers()
    assert headers["User-Agent"] in USER_AGENTS


def test_get_random_headers_referer_google():
    headers = get_random_headers()
    assert headers["Referer"] == "https://www.google.com/"
