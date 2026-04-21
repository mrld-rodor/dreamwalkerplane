"""Helpers compartilhados para autenticacao administrativa."""

from functools import wraps
from hmac import compare_digest

from flask import current_app, flash, redirect, request, session, url_for
from werkzeug.security import check_password_hash


def get_admin_identity():
    """Retorna usuario e IP atual do admin para auditoria."""
    return (
        session.get('admin_username') or current_app.config.get('ADMIN_USERNAME') or 'admin',
        request.remote_addr,
    )


def is_admin_logged_in():
    """Indica se ha uma sessao administrativa ativa."""
    return bool(session.get('admin_logged'))


def verify_admin_credentials(username, password):
    """Valida credenciais admin com suporte preferencial a senha em hash."""
    configured_username = current_app.config.get('ADMIN_USERNAME') or ''
    configured_password_hash = current_app.config.get('ADMIN_PASSWORD_HASH') or ''
    configured_password = current_app.config.get('ADMIN_PASSWORD') or ''

    if not compare_digest((username or '').strip(), configured_username):
        return False

    if configured_password_hash:
        try:
            return check_password_hash(configured_password_hash, password or '')
        except ValueError:
            current_app.logger.error('ADMIN_PASSWORD_HASH invalido ou malformado.')
            return False

    return bool(configured_password) and compare_digest(password or '', configured_password)


def admin_login_required(view_func):
    """Protege rotas administrativas com a sessao centralizada."""
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not is_admin_logged_in():
            flash('Acesso negado! Faça login primeiro.', 'danger')
            return redirect(url_for('main.admin_login', next=request.path))
        return view_func(*args, **kwargs)

    return wrapped_view


def establish_admin_session(username=None):
    """Registra a sessao administrativa padrao."""
    session['admin_logged'] = True
    session['admin_username'] = username or current_app.config.get('ADMIN_USERNAME') or 'admin'


def clear_admin_session():
    """Limpa dados da sessao administrativa."""
    session.pop('admin_logged', None)
    session.pop('admin_username', None)
