"""Utilitarios para validacao de reCAPTCHA."""

import requests


VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'


def verify_recaptcha(secret_key, response_token, remote_ip=None, logger=None, form_name='formulario'):
    """Valida um token reCAPTCHA e retorna (success, message)."""
    if not secret_key:
        if logger:
            logger.warning('reCAPTCHA nao configurado para %s.', form_name)
        return False, 'reCAPTCHA nao configurado.'

    if not response_token:
        return False, 'Por favor, complete a verificacao reCAPTCHA.'

    payload = {
        'secret': secret_key,
        'response': response_token,
    }
    if remote_ip:
        payload['remoteip'] = remote_ip

    try:
        result = requests.post(VERIFY_URL, data=payload, timeout=10).json()
    except Exception as exc:
        if logger:
            logger.exception('Erro ao validar reCAPTCHA de %s: %s', form_name, exc)
        return False, 'Erro na verificacao de seguranca. Tente novamente.'

    if result.get('success'):
        return True, None

    error_codes = ', '.join(result.get('error-codes', [])) or 'sem-codigo'
    hostname = result.get('hostname', 'desconhecido')
    if logger:
        logger.warning(
            'Falha no reCAPTCHA de %s. hostname=%s error_codes=%s',
            form_name,
            hostname,
            error_codes
        )
    return False, 'Verificacao reCAPTCHA falhou. Confira o dominio configurado e tente novamente.'