"""Configuracao central de seguranca HTTP da aplicacao."""

import os

from flask import request
from werkzeug.middleware.proxy_fix import ProxyFix


def _env_flag(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def _build_content_security_policy():
    directives = {
        'default-src': ["'self'"],
        'base-uri': ["'self'"],
        'object-src': ["'none'"],
        'frame-ancestors': ["'self'"],
        'form-action': ["'self'"],
        'script-src': [
            "'self'",
            "'unsafe-inline'",
            'https://cdn.tailwindcss.com',
            'https://cdn.jsdelivr.net',
            'https://unpkg.com',
            'https://www.google.com/recaptcha/',
            'https://www.gstatic.com/recaptcha/',
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",
            'https://fonts.googleapis.com',
            'https://cdn.jsdelivr.net',
            'https://unpkg.com',
        ],
        'img-src': ["'self'", 'data:', 'https:'],
        'font-src': ["'self'", 'data:', 'https://fonts.gstatic.com', 'https://cdn.jsdelivr.net'],
        'connect-src': [
            "'self'",
            'https://www.google.com/recaptcha/',
            'https://www.gstatic.com/recaptcha/',
            'https://ipinfo.io',
        ],
        'frame-src': ['https://www.google.com/recaptcha/'],
    }
    return '; '.join(f"{directive} {' '.join(sources)}" for directive, sources in directives.items())


def configure_proxy(app):
    """Confia apenas na quantidade configurada de proxies reversos."""
    trusted_proxy_hops = int(os.getenv('TRUSTED_PROXY_HOPS', '1'))
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=trusted_proxy_hops,
        x_proto=trusted_proxy_hops,
        x_host=trusted_proxy_hops,
        x_port=trusted_proxy_hops,
    )


def configure_security(app):
    """Aplica configuracoes de sessao e headers de seguranca."""
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config['SESSION_COOKIE_SECURE'] = _env_flag('SESSION_COOKIE_SECURE', default=False)
    app.config['ENABLE_HSTS'] = _env_flag('ENABLE_HSTS', default=False)

    csp_value = _build_content_security_policy()
    csp_report_only = _env_flag('CONTENT_SECURITY_POLICY_REPORT_ONLY', default=False)

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
        response.headers.setdefault('X-XSS-Protection', '1; mode=block')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault(
            'Permissions-Policy',
            'accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()'
        )
        response.headers.setdefault('Cross-Origin-Opener-Policy', 'same-origin')
        response.headers.setdefault('X-Permitted-Cross-Domain-Policies', 'none')

        csp_header = 'Content-Security-Policy-Report-Only' if csp_report_only else 'Content-Security-Policy'
        response.headers.setdefault(csp_header, csp_value)

        should_send_hsts = (
            app.config.get('ENABLE_HSTS')
            or (app.config.get('SESSION_COOKIE_SECURE') and request.is_secure and not app.debug)
        )
        if should_send_hsts:
            response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')

        return response
