import traceback
from html import escape

import requests

from control.email_config import (
    email_api_key,
    email_api_timeout,
    email_api_url,
    email_receiver,
    email_sender,
)


class EmailDeliveryError(Exception):
    """Erro base para falhas no envio de email."""


class EmailNetworkError(EmailDeliveryError):
    """Falha de conectividade com o servidor SMTP."""


class Contato:
    def __init__(self, nome, email, mensagem):
        self.nome = nome
        self.email = email
        self.mensagem = mensagem


def _build_plain_text(contato):
    return f"""
Novo contato no DreamWalker Plane!

Nome: {contato.nome}
Email: {contato.email}

Mensagem:
{contato.mensagem}
""".strip()


def _build_html_email(contato):
    nome = escape(contato.nome)
    email = escape(contato.email)
    mensagem = escape(contato.mensagem).replace('\n', '<br>')

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Novo contato - DreamWalker Plane</title>
</head>
<body style="margin:0; padding:0; background-color:#050505; color:#f5f5f5; font-family:'Roboto Mono', 'Courier New', monospace;">
    <div style="background: radial-gradient(circle at top, #151515 0%, #050505 62%); padding: 32px 16px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 680px; margin: 0 auto; border-collapse: collapse;">
            <tr>
                <td style="padding: 0;">
                    <div style="border:1px solid #2a2a2a; background: rgba(7,7,7,0.96); box-shadow: 0 22px 60px rgba(0,0,0,0.45);">
                        <div style="padding: 26px 28px 18px; border-bottom: 1px solid #1d1d1d; text-align:center;">
                            <div style="display:inline-block; padding: 7px 12px; border:1px solid #3a3a3a; color:#d1d1d1; font-size:11px; letter-spacing:0.28em; text-transform:uppercase;">
                                Novo contato recebido
                            </div>
                            <h1 style="margin: 18px 0 0; color:#ffffff; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:32px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase;">
                                DreamWalker Plane
                            </h1>
                        </div>

                        <div style="padding: 30px 28px 8px;">
                            <div style="background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); border:1px solid #2c2c2c; padding: 22px; margin-bottom: 18px;">
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.22em; font-size:11px; margin-bottom:8px;">Remetente</div>
                                <div style="font-size:24px; color:#ffffff; font-family:'Orbitron', 'Arial Black', sans-serif; margin-bottom:6px;">{nome}</div>
                                <div style="font-size:14px; color:#d5d5d5;">{email}</div>
                            </div>

                            <div style="margin-bottom: 24px;">
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.22em; font-size:11px; margin-bottom:10px;">Mensagem</div>
                                <div style="background:#0d0d0d; border-left:4px solid #ffffff; border-top:1px solid #232323; border-right:1px solid #232323; border-bottom:1px solid #232323; padding: 20px 22px; color:#efefef; font-size:15px; line-height:1.8;">
                                    {mensagem}
                                </div>
                            </div>

                            <div style="text-align:center; margin: 28px 0 10px;">
                                <a href="mailto:{email}" style="display:inline-block; padding:14px 24px; background:#ffffff; color:#050505; text-decoration:none; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:12px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; border:1px solid #ffffff;">
                                    Responder contato
                                </a>
                            </div>
                        </div>

                        <div style="padding: 18px 28px 26px; text-align:center; border-top:1px solid #1d1d1d; color:#7d7d7d; font-size:11px; letter-spacing:0.1em; text-transform:uppercase;">
                            Enviado automaticamente pelo formulario de contato
                        </div>
                    </div>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
""".strip()


def send_email(contato):
    html_body = _build_html_email(contato)
    text_body = _build_plain_text(contato)

    if not email_api_key or not email_sender or not email_receiver:
        missing = []
        if not email_api_key:
            missing.append('RESEND_API_KEY')
        if not email_sender:
            missing.append('EMAIL_SENDER')
        if not email_receiver:
            missing.append('EMAIL_RECEIVER')
        raise EmailDeliveryError(
            f"Configuracao de email incompleta: {', '.join(missing)}"
        )

    try:
        payload = {
            'from': email_sender,
            'to': [email_receiver],
            'subject': f'Visitante do DreamWalker Plane - {contato.nome}',
            'reply_to': contato.email,
            'html': html_body,
            'text': text_body,
        }

        response = requests.post(
            email_api_url,
            headers={
                'Authorization': f'Bearer {email_api_key}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=email_api_timeout,
        )
        response.raise_for_status()
        print('[INFO] Email enviado com sucesso via API HTTP.')
        return 202
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] Timeout ao enviar email via API HTTP: {e}")
        print(traceback.format_exc())
        raise EmailNetworkError('Timeout na comunicacao com o provedor de email') from e
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Falha de conexao com a API de email: {e}")
        print(traceback.format_exc())
        raise EmailNetworkError('Provedor de email indisponivel ou inacessivel') from e
    except requests.exceptions.HTTPError as e:
        response_body = ''
        if e.response is not None:
            response_body = e.response.text
        print(f"[ERROR] API de email retornou erro HTTP: {response_body}")
        print(traceback.format_exc())
        raise EmailDeliveryError('Provedor de email rejeitou a solicitacao') from e
    except Exception as e:
        print(f"[ERROR] Erro ao enviar e-mail: {e}")
        print(traceback.format_exc())
        raise EmailDeliveryError("Erro inesperado ao enviar email") from e
