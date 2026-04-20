"""Protecao CSRF simples baseada em sessao para formularios HTML."""

import secrets
from functools import wraps
from hmac import compare_digest

from flask import abort, request, session


CSRF_SESSION_KEY = '_csrf_token'


def generate_csrf_token():
    """Gera ou reutiliza o token CSRF da sessao atual."""
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def validate_csrf_token(submitted_token):
    """Valida o token enviado no formulario ou cabecalho."""
    session_token = session.get(CSRF_SESSION_KEY)
    if not submitted_token or not session_token:
        return False
    return compare_digest(submitted_token, session_token)


def csrf_protect(view_func):
    """Decorator para exigir token CSRF em requisicoes mutaveis."""
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        submitted_token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
        if not validate_csrf_token(submitted_token):
            abort(400, description='Token CSRF invalido ou ausente.')
        return view_func(*args, **kwargs)

    return wrapped_view


def init_csrf(app):
    """Expõe o helper de token no ambiente Jinja."""
    app.jinja_env.globals['csrf_token'] = generate_csrf_token
