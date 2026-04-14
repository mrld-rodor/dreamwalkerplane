"""
Notificação de novos relatos para o admin.

O nome do módulo foi mantido como sendgrid_email.py por compatibilidade com o
fluxo solicitado, mas o envio usa o provedor HTTP configurado em email_config.
"""

import traceback
from html import escape

import requests
from flask import request, url_for

from control.email_config import (
    email_api_key,
    email_api_timeout,
    email_api_url,
    email_receiver,
    email_sender,
)
from control.email_function import EmailDeliveryError, EmailNetworkError


def _truncate_text(text, max_length=900):
    if len(text) <= max_length:
        return text
    return f"{text[:max_length].rstrip()}..."


def _send_email_payload(recipient, subject, html_body, text_body):
    if not email_api_key or not email_sender or not recipient:
        missing = []
        if not email_api_key:
            missing.append('RESEND_API_KEY')
        if not email_sender:
            missing.append('EMAIL_SENDER')
        if not recipient:
            missing.append('RECIPIENT_EMAIL')
        raise EmailDeliveryError(
            f"Configuracao de email incompleta: {', '.join(missing)}"
        )

    response = requests.post(
        email_api_url,
        headers={
            'Authorization': f'Bearer {email_api_key}',
            'Content-Type': 'application/json',
        },
        json={
            'from': email_sender,
            'to': [recipient],
            'subject': subject,
            'html': html_body,
            'text': text_body,
        },
        timeout=email_api_timeout,
    )
    response.raise_for_status()
    return 202


def _build_admin_links():
    base_url = request.url_root.rstrip('/')
    return {
        'login': url_for('relatos.admin_login', _external=True),
        'pendentes': url_for('relatos.admin_pendentes', _external=True),
        'dashboard': url_for('main.admin_dashboard', _external=True),
        'logo': url_for('static', filename='images/amiraldo_logo_transparent_white.png', _external=True),
        'site': base_url,
    }


def _build_plain_text(relato):
    links = _build_admin_links()
    return f"""
Novo relato pendente no DreamWalker Plane!

ID: {relato.id}
Autor: {relato.autor}
Titulo: {relato.titulo}
Status: {relato.status}
Data de envio: {relato.data_envio.strftime('%d/%m/%Y %H:%M') if relato.data_envio else 'Desconhecida'}
IP: {relato.ip_remetente or 'Desconhecido'}

Conteudo:
{_truncate_text(relato.conteudo)}

Links rapidos:
Login admin: {links['login']}
Fila de pendentes: {links['pendentes']}
Dashboard: {links['dashboard']}
Site: {links['site']}
""".strip()


def _build_html_email(relato):
    links = _build_admin_links()
    autor = escape(relato.autor)
    titulo = escape(relato.titulo)
    conteudo = escape(_truncate_text(relato.conteudo)).replace('\n', '<br>')
    status = escape(relato.status or 'pendente')
    data_envio = relato.data_envio.strftime('%d/%m/%Y %H:%M') if relato.data_envio else 'Desconhecida'
    ip_remetente = escape(relato.ip_remetente or 'Desconhecido')

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Novo relato pendente</title>
</head>
<body style="margin:0; padding:0; background-color:#050505; color:#f5f5f5; font-family:'Roboto Mono', 'Courier New', monospace;">
    <div style="background: radial-gradient(circle at top, #151515 0%, #050505 62%); padding: 32px 16px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 680px; margin: 0 auto; border-collapse: collapse;">
            <tr>
                <td style="padding: 0;">
                    <div style="border:2px solid #0603b4; background: rgba(7,7,7,0.96); box-shadow: 0 22px 60px rgba(0,0,0,0.45), 0 0 26px rgba(6,3,180,0.45), inset 0 0 0.35rem rgba(6,3,180,0.65);">
                        <div style="padding: 26px 28px 18px; border-bottom: 1px solid rgba(6,3,180,0.45); text-align:center; box-shadow: inset 0 -10px 30px rgba(6,3,180,0.08);">
                            <div style="display:inline-block; padding: 7px 12px; border:1px solid rgba(6,3,180,0.65); box-shadow: 0 0 12px rgba(6,3,180,0.28); color:#d9dcff; font-size:11px; letter-spacing:0.28em; text-transform:uppercase;">
                                Novo relato pendente
                            </div>
                            <div style="margin: 0 0 14px; text-align:center;">
                                <img src="{links['logo']}" alt="DreamWalker Plane" style="width: 96px; max-width: 96px; height: auto; display: inline-block; filter: drop-shadow(0 0 10px rgba(6,3,180,0.28));">
                            </div>
                            <h1 style="margin: 18px 0 0; color:#ffffff; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:32px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; text-shadow: 0 0 14px rgba(6,3,180,0.38);">
                                DreamWalker Plane
                            </h1>
                        </div>

                        <div style="padding: 30px 28px 8px;">
                            <div style="background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); border:1px solid rgba(6,3,180,0.42); box-shadow: 0 0 18px rgba(6,3,180,0.14); padding: 22px; margin-bottom: 18px;">
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.28em; font-size:10px; margin-bottom:8px;">Relato recebido</div>
                                <div style="font-size:24px; color:#ffffff; font-family:'Orbitron', 'Arial Black', sans-serif; letter-spacing:0.08em; margin-bottom:6px; text-shadow: 0 0 10px rgba(6,3,180,0.22);">{titulo}</div>
                                <div style="font-size:13px; color:#cfd6ff; letter-spacing:0.08em; text-transform:uppercase;">Por {autor}</div>
                            </div>

                            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 20px;">
                                <div style="background:#0d0d0d; border:1px solid rgba(6,3,180,0.32); box-shadow: 0 0 14px rgba(6,3,180,0.1); padding: 16px;">
                                    <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.24em; font-size:10px; margin-bottom:6px;">ID</div>
                                    <div style="color:#ffffff; font-size:18px; font-family:'Orbitron', 'Arial Black', sans-serif; letter-spacing:0.08em;">{relato.id}</div>
                                </div>
                                <div style="background:#0d0d0d; border:1px solid rgba(6,3,180,0.32); box-shadow: 0 0 14px rgba(6,3,180,0.1); padding: 16px;">
                                    <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.24em; font-size:10px; margin-bottom:6px;">Data</div>
                                    <div style="color:#ffffff; font-size:18px; font-family:'Orbitron', 'Arial Black', sans-serif; letter-spacing:0.04em;">{data_envio}</div>
                                </div>
                                <div style="background:#0d0d0d; border:1px solid rgba(6,3,180,0.32); box-shadow: 0 0 14px rgba(6,3,180,0.1); padding: 16px;">
                                    <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.24em; font-size:10px; margin-bottom:6px;">IP</div>
                                    <div style="color:#ffffff; font-size:16px; font-family:'Orbitron', 'Arial Black', sans-serif; letter-spacing:0.04em;">{ip_remetente}</div>
                                </div>
                                <div style="background:#0d0d0d; border:1px solid rgba(6,3,180,0.32); box-shadow: 0 0 14px rgba(6,3,180,0.1); padding: 16px;">
                                    <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.24em; font-size:10px; margin-bottom:6px;">Status</div>
                                    <div style="color:#ffffff; font-size:18px; font-family:'Orbitron', 'Arial Black', sans-serif; letter-spacing:0.08em; text-transform:uppercase;">{status}</div>
                                </div>
                            </div>

                            <div style="margin-bottom: 24px;">
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.28em; font-size:10px; margin-bottom:10px;">Resumo do relato</div>
                                <div style="background:#0d0d0d; border-left:4px solid #0603b4; border-top:1px solid rgba(6,3,180,0.32); border-right:1px solid rgba(6,3,180,0.32); border-bottom:1px solid rgba(6,3,180,0.32); box-shadow: 0 0 16px rgba(6,3,180,0.12); padding: 20px 22px; color:#efefef; font-size:15px; line-height:1.9; letter-spacing:0.03em;">
                                    {conteudo}
                                </div>
                            </div>

                            <div style="background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.015) 100%); border:1px solid rgba(6,3,180,0.35); box-shadow: 0 0 18px rgba(6,3,180,0.12); padding: 18px; margin-bottom: 22px;">
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.28em; font-size:10px; margin-bottom:12px;">Acoes rapidas</div>
                                <div style="text-align:center; margin: 0 0 12px;">
                                    <a href="{links['pendentes']}" style="display:inline-block; margin: 6px; padding:14px 24px; background:#0603b4; color:#ffffff; text-decoration:none; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:12px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; border:1px solid #0603b4; box-shadow: 0 0 22px rgba(6,3,180,0.45);">
                                        Abrir pendentes
                                    </a>
                                    <a href="{links['dashboard']}" style="display:inline-block; margin: 6px; padding:14px 24px; background:transparent; color:#dfe3ff; text-decoration:none; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:12px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; border:1px solid rgba(6,3,180,0.65); box-shadow: 0 0 18px rgba(6,3,180,0.18);">
                                        Ver dashboard
                                    </a>
                                </div>
                                <div style="text-align:center; margin: 0;">
                                    <a href="{links['login']}" style="color:#b8c1ff; text-decoration:none; font-size:13px;">Entrar no login administrativo</a>
                                </div>
                            </div>
                        </div>

                        <div style="padding: 18px 28px 26px; text-align:center; border-top:1px solid rgba(6,3,180,0.45); color:#8a90d6; font-size:11px; letter-spacing:0.24em; text-transform:uppercase; box-shadow: inset 0 12px 30px rgba(6,3,180,0.05);">
                            Enviado automaticamente apos submissao de relato no site DreamWalker Plane
                        </div>
                    </div>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
""".strip()


def send_notification_email(relato):
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
        response = requests.post(
            email_api_url,
            headers={
                'Authorization': f'Bearer {email_api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'from': email_sender,
                'to': [email_receiver],
                'subject': f'Novo relato pendente: {relato.titulo}',
                'html': _build_html_email(relato),
                'text': _build_plain_text(relato),
            },
            timeout=email_api_timeout,
        )
        response.raise_for_status()
        print('[INFO] Notificacao de novo relato enviada ao admin.')
        return 202
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] Timeout ao enviar notificacao de relato: {e}")
        print(traceback.format_exc())
        raise EmailNetworkError('Timeout na comunicacao com o provedor de email') from e
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Falha de conexao ao enviar notificacao de relato: {e}")
        print(traceback.format_exc())
        raise EmailNetworkError('Provedor de email indisponivel ou inacessivel') from e
    except requests.exceptions.HTTPError as e:
        response_body = ''
        if e.response is not None:
            response_body = e.response.text
        print(f"[ERROR] API de email retornou erro HTTP na notificacao de relato: {response_body}")
        print(traceback.format_exc())
        raise EmailDeliveryError('Provedor de email rejeitou a solicitacao') from e
    except Exception as e:
        print(f"[ERROR] Erro inesperado ao notificar admin sobre relato: {e}")
        print(traceback.format_exc())
        raise EmailDeliveryError('Erro inesperado ao enviar notificacao de relato') from e


def _build_comment_plain_text(comentario):
    links = _build_admin_links()
    titulo_relato = comentario.relato.titulo if comentario.relato else f'Relato #{comentario.relato_id}'

    return f"""
Novo comentario pendente no DreamWalker Plane!

ID: {comentario.id}
Relato: {titulo_relato}
Autor: {comentario.autor}
Email: {comentario.email or 'Nao informado'}
Status: {comentario.status}
Data de envio: {comentario.data_envio.strftime('%d/%m/%Y %H:%M') if comentario.data_envio else 'Desconhecida'}
IP: {comentario.ip_remetente or 'Desconhecido'}

Conteudo:
{_truncate_text(comentario.conteudo)}

Links rapidos:
Login admin: {links['login']}
Fila de pendentes: {links['pendentes']}
Dashboard: {links['dashboard']}
Post: {url_for('main.ver_post', post_id=comentario.relato_id, _external=True)}
""".strip()


def _build_comment_html_email(comentario):
    links = _build_admin_links()
    autor = escape(comentario.autor)
    email = escape(comentario.email or 'Nao informado')
    titulo_relato = escape(comentario.relato.titulo) if comentario.relato else f'Relato #{comentario.relato_id}'
    conteudo = escape(_truncate_text(comentario.conteudo)).replace('\n', '<br>')
    status = escape(comentario.status or 'pendente')
    data_envio = comentario.data_envio.strftime('%d/%m/%Y %H:%M') if comentario.data_envio else 'Desconhecida'
    ip_remetente = escape(comentario.ip_remetente or 'Desconhecido')
    post_url = url_for('main.ver_post', post_id=comentario.relato_id, _external=True)

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Novo comentario pendente</title>
</head>
<body style="margin:0; padding:0; background-color:#050505; color:#f5f5f5; font-family:'Roboto Mono', 'Courier New', monospace;">
    <div style="background: radial-gradient(circle at top, #151515 0%, #050505 62%); padding: 32px 16px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 680px; margin: 0 auto; border-collapse: collapse;">
            <tr>
                <td style="padding: 0;">
                    <div style="border:2px solid #0603b4; background: rgba(7,7,7,0.96); box-shadow: 0 22px 60px rgba(0,0,0,0.45), 0 0 26px rgba(6,3,180,0.45), inset 0 0 0.35rem rgba(6,3,180,0.65);">
                        <div style="padding: 26px 28px 18px; border-bottom: 1px solid rgba(6,3,180,0.45); text-align:center; box-shadow: inset 0 -10px 30px rgba(6,3,180,0.08);">
                            <div style="display:inline-block; padding: 7px 12px; border:1px solid rgba(6,3,180,0.65); box-shadow: 0 0 12px rgba(6,3,180,0.28); color:#d9dcff; font-size:11px; letter-spacing:0.28em; text-transform:uppercase;">
                                Novo comentario pendente
                            </div>
                            <div style="margin: 0 0 14px; text-align:center;">
                                <img src="{links['logo']}" alt="DreamWalker Plane" style="width: 96px; max-width: 96px; height: auto; display: inline-block; filter: drop-shadow(0 0 10px rgba(6,3,180,0.28));">
                            </div>
                            <h1 style="margin: 18px 0 0; color:#ffffff; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:32px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; text-shadow: 0 0 14px rgba(6,3,180,0.38);">
                                DreamWalker Plane
                            </h1>
                        </div>

                        <div style="padding: 30px 28px 8px;">
                            <div style="background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); border:1px solid rgba(6,3,180,0.42); box-shadow: 0 0 18px rgba(6,3,180,0.14); padding: 22px; margin-bottom: 18px;">
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.28em; font-size:10px; margin-bottom:8px;">Comentario recebido</div>
                                <div style="font-size:24px; color:#ffffff; font-family:'Orbitron', 'Arial Black', sans-serif; letter-spacing:0.08em; margin-bottom:6px; text-shadow: 0 0 10px rgba(6,3,180,0.22);">{titulo_relato}</div>
                                <div style="font-size:13px; color:#cfd6ff; letter-spacing:0.08em; text-transform:uppercase;">Por {autor}</div>
                            </div>

                            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 20px;">
                                <div style="background:#0d0d0d; border:1px solid rgba(6,3,180,0.32); box-shadow: 0 0 14px rgba(6,3,180,0.1); padding: 16px;">
                                    <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.24em; font-size:10px; margin-bottom:6px;">ID</div>
                                    <div style="color:#ffffff; font-size:18px; font-family:'Orbitron', 'Arial Black', sans-serif; letter-spacing:0.08em;">{comentario.id}</div>
                                </div>
                                <div style="background:#0d0d0d; border:1px solid rgba(6,3,180,0.32); box-shadow: 0 0 14px rgba(6,3,180,0.1); padding: 16px;">
                                    <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.24em; font-size:10px; margin-bottom:6px;">Data</div>
                                    <div style="color:#ffffff; font-size:18px; font-family:'Orbitron', 'Arial Black', sans-serif; letter-spacing:0.04em;">{data_envio}</div>
                                </div>
                                <div style="background:#0d0d0d; border:1px solid rgba(6,3,180,0.32); box-shadow: 0 0 14px rgba(6,3,180,0.1); padding: 16px;">
                                    <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.24em; font-size:10px; margin-bottom:6px;">Email</div>
                                    <div style="color:#ffffff; font-size:16px; font-family:'Orbitron', 'Arial Black', sans-serif; letter-spacing:0.04em;">{email}</div>
                                </div>
                                <div style="background:#0d0d0d; border:1px solid rgba(6,3,180,0.32); box-shadow: 0 0 14px rgba(6,3,180,0.1); padding: 16px;">
                                    <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.24em; font-size:10px; margin-bottom:6px;">Status</div>
                                    <div style="color:#ffffff; font-size:18px; font-family:'Orbitron', 'Arial Black', sans-serif; letter-spacing:0.08em; text-transform:uppercase;">{status}</div>
                                </div>
                            </div>

                            <div style="margin-bottom: 16px;">
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.28em; font-size:10px; margin-bottom:10px;">IP</div>
                                <div style="background:#0d0d0d; border-left:4px solid #0603b4; border-top:1px solid rgba(6,3,180,0.32); border-right:1px solid rgba(6,3,180,0.32); border-bottom:1px solid rgba(6,3,180,0.32); box-shadow: 0 0 16px rgba(6,3,180,0.12); padding: 16px 18px; color:#efefef; font-size:15px; line-height:1.6; letter-spacing:0.03em;">
                                    {ip_remetente}
                                </div>
                            </div>

                            <div style="margin-bottom: 24px;">
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.28em; font-size:10px; margin-bottom:10px;">Comentario</div>
                                <div style="background:#0d0d0d; border-left:4px solid #0603b4; border-top:1px solid rgba(6,3,180,0.32); border-right:1px solid rgba(6,3,180,0.32); border-bottom:1px solid rgba(6,3,180,0.32); box-shadow: 0 0 16px rgba(6,3,180,0.12); padding: 20px 22px; color:#efefef; font-size:15px; line-height:1.9; letter-spacing:0.03em;">
                                    {conteudo}
                                </div>
                            </div>

                            <div style="background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.015) 100%); border:1px solid rgba(6,3,180,0.35); box-shadow: 0 0 18px rgba(6,3,180,0.12); padding: 18px; margin-bottom: 22px;">
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.28em; font-size:10px; margin-bottom:12px;">Acoes rapidas</div>
                                <div style="text-align:center; margin: 0 0 12px;">
                                    <a href="{post_url}" style="display:inline-block; margin: 6px; padding:14px 24px; background:#0603b4; color:#ffffff; text-decoration:none; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:12px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; border:1px solid #0603b4; box-shadow: 0 0 22px rgba(6,3,180,0.45);">
                                        Ver post
                                    </a>
                                    <a href="{links['pendentes']}" style="display:inline-block; margin: 6px; padding:14px 24px; background:transparent; color:#dfe3ff; text-decoration:none; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:12px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; border:1px solid rgba(6,3,180,0.65); box-shadow: 0 0 18px rgba(6,3,180,0.18);">
                                        Abrir pendentes
                                    </a>
                                </div>
                                <div style="text-align:center; margin: 0;">
                                    <a href="{links['login']}" style="color:#b8c1ff; text-decoration:none; font-size:13px;">Entrar no login administrativo</a>
                                </div>
                            </div>
                        </div>

                        <div style="padding: 18px 28px 26px; text-align:center; border-top:1px solid rgba(6,3,180,0.45); color:#8a90d6; font-size:11px; letter-spacing:0.24em; text-transform:uppercase; box-shadow: inset 0 12px 30px rgba(6,3,180,0.05);">
                            Enviado automaticamente apos submissao de comentario no site DreamWalker Plane
                        </div>
                    </div>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
""".strip()


def send_comment_notification_email(comentario):
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
        response = requests.post(
            email_api_url,
            headers={
                'Authorization': f'Bearer {email_api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'from': email_sender,
                'to': [email_receiver],
                'subject': f'Novo comentario pendente no relato #{comentario.relato_id}',
                'html': _build_comment_html_email(comentario),
                'text': _build_comment_plain_text(comentario),
            },
            timeout=email_api_timeout,
        )
        response.raise_for_status()
        print('[INFO] Notificacao de novo comentario enviada ao admin.')
        return 202
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] Timeout ao enviar notificacao de comentario: {e}")
        print(traceback.format_exc())
        raise EmailNetworkError('Timeout na comunicacao com o provedor de email') from e
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Falha de conexao ao enviar notificacao de comentario: {e}")
        print(traceback.format_exc())
        raise EmailNetworkError('Provedor de email indisponivel ou inacessivel') from e
    except requests.exceptions.HTTPError as e:
        response_body = ''
        if e.response is not None:
            response_body = e.response.text
        print(f"[ERROR] API de email retornou erro HTTP na notificacao de comentario: {response_body}")
        print(traceback.format_exc())
        raise EmailDeliveryError('Provedor de email rejeitou a solicitacao') from e
    except Exception as e:
        print(f"[ERROR] Erro inesperado ao notificar admin sobre comentario: {e}")
        print(traceback.format_exc())
        raise EmailDeliveryError('Erro inesperado ao enviar notificacao de comentario') from e


def _build_user_relato_status_plain_text(relato, status):
    status_label = 'aprovado' if status == 'aprovado' else 'rejeitado'
    action_text = 'ja esta visivel no mural e na pagina do post.' if status == 'aprovado' else 'nao foi aprovado para publicacao no mural.'
    mural_url = url_for('relatos.mural', _external=True)
    lines = [
        f'Ola, {relato.autor}!',
        '',
        f'Seu relato "{relato.titulo}" foi {status_label}.',
        '',
        'Status:',
        action_text,
        '',
        'Links:',
    ]

    if status == 'aprovado':
        lines.append(f"Post: {url_for('main.ver_post', post_id=relato.id, _external=True)}")
    lines.append(f'Mural: {mural_url}')

    return '\n'.join(lines)


def _build_user_relato_status_html_email(relato, status):
    status_label = 'aprovado' if status == 'aprovado' else 'rejeitado'
    title = escape(relato.titulo)
    author = escape(relato.autor)
    logo_url = url_for('static', filename='images/amiraldo_logo_transparent_white.png', _external=True)
    mural_url = url_for('relatos.mural', _external=True)
    message = (
        'Seu relato foi aprovado e agora esta publicado no DreamWalker Plane.'
        if status == 'aprovado'
        else 'Seu relato foi analisado, mas nao foi aprovado para publicacao no mural.'
    )
    primary_action = (
        f'<a href="{url_for("main.ver_post", post_id=relato.id, _external=True)}" style="display:inline-block; margin: 6px; padding:14px 24px; background:#0603b4; color:#ffffff; text-decoration:none; font-family:\'Orbitron\', \'Arial Black\', sans-serif; font-size:12px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; border:1px solid #0603b4;">Abrir post</a>'
        if status == 'aprovado'
        else ''
    )

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Status do seu relato</title>
</head>
<body style="margin:0; padding:0; background-color:#050505; color:#f5f5f5; font-family:'Roboto Mono', 'Courier New', monospace;">
    <div style="background: radial-gradient(circle at top, #151515 0%, #050505 62%); padding: 32px 16px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 680px; margin: 0 auto; border-collapse: collapse;">
            <tr>
                <td style="padding: 0;">
                    <div style="border:2px solid #0603b4; background: rgba(7,7,7,0.96); box-shadow: 0 22px 60px rgba(0,0,0,0.45), 0 0 26px rgba(6,3,180,0.45), inset 0 0 0.35rem rgba(6,3,180,0.65);">
                        <div style="padding: 26px 28px 18px; border-bottom: 1px solid rgba(6,3,180,0.45); text-align:center;">
                            <img src="{logo_url}" alt="DreamWalker Plane" style="width: 96px; max-width: 96px; height: auto; display: inline-block;">
                            <h1 style="margin: 18px 0 6px; color:#ffffff; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:28px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase;">DreamWalker Plane</h1>
                            <div style="color:#d9dcff; font-size:11px; letter-spacing:0.28em; text-transform:uppercase;">Status do seu relato: {status_label}</div>
                        </div>
                        <div style="padding: 30px 28px 18px;">
                            <p style="color:#efefef; font-size:16px; line-height:1.8; margin:0 0 16px;">Ola, {author}.</p>
                            <p style="color:#efefef; font-size:15px; line-height:1.8; margin:0 0 16px;">{message}</p>
                            <div style="background:#0d0d0d; border-left:4px solid #0603b4; padding: 18px 20px; margin-bottom: 24px;">
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.24em; font-size:10px; margin-bottom:8px;">Relato</div>
                                <div style="color:#ffffff; font-size:22px; font-family:'Orbitron', 'Arial Black', sans-serif;">{title}</div>
                            </div>
                            <div style="text-align:center; margin: 0 0 14px;">
                                {primary_action}
                                <a href="{mural_url}" style="display:inline-block; margin: 6px; padding:14px 24px; background:transparent; color:#dfe3ff; text-decoration:none; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:12px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; border:1px solid rgba(6,3,180,0.65);">Ir ao mural</a>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
""".strip()


def _build_user_comment_status_plain_text(comentario, status):
    status_label = 'aprovado' if status == 'aprovado' else 'rejeitado'
    titulo_relato = comentario.relato.titulo if comentario.relato else f'Relato #{comentario.relato_id}'
    post_url = url_for('main.ver_post', post_id=comentario.relato_id, _external=True)

    return f"""
Ola, {comentario.autor}!

Seu comentario no relato "{titulo_relato}" foi {status_label}.

Post:
{post_url}

Trecho do comentario:
{_truncate_text(comentario.conteudo, max_length=300)}
""".strip()


def _build_user_comment_status_html_email(comentario, status):
    status_label = 'aprovado' if status == 'aprovado' else 'rejeitado'
    author = escape(comentario.autor)
    titulo_relato = escape(comentario.relato.titulo) if comentario.relato else f'Relato #{comentario.relato_id}'
    excerpt = escape(_truncate_text(comentario.conteudo, max_length=300)).replace('\n', '<br>')
    logo_url = url_for('static', filename='images/amiraldo_logo_transparent_white.png', _external=True)
    post_url = url_for('main.ver_post', post_id=comentario.relato_id, _external=True)
    message = (
        'Seu comentario foi aprovado e agora esta visivel na pagina do relato.'
        if status == 'aprovado'
        else 'Seu comentario foi analisado, mas nao foi aprovado para publicacao.'
    )

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Status do seu comentario</title>
</head>
<body style="margin:0; padding:0; background-color:#050505; color:#f5f5f5; font-family:'Roboto Mono', 'Courier New', monospace;">
    <div style="background: radial-gradient(circle at top, #151515 0%, #050505 62%); padding: 32px 16px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 680px; margin: 0 auto; border-collapse: collapse;">
            <tr>
                <td style="padding: 0;">
                    <div style="border:2px solid #0603b4; background: rgba(7,7,7,0.96); box-shadow: 0 22px 60px rgba(0,0,0,0.45), 0 0 26px rgba(6,3,180,0.45), inset 0 0 0.35rem rgba(6,3,180,0.65);">
                        <div style="padding: 26px 28px 18px; border-bottom: 1px solid rgba(6,3,180,0.45); text-align:center;">
                            <img src="{logo_url}" alt="DreamWalker Plane" style="width: 96px; max-width: 96px; height: auto; display: inline-block;">
                            <h1 style="margin: 18px 0 6px; color:#ffffff; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:28px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase;">DreamWalker Plane</h1>
                            <div style="color:#d9dcff; font-size:11px; letter-spacing:0.28em; text-transform:uppercase;">Status do seu comentario: {status_label}</div>
                        </div>
                        <div style="padding: 30px 28px 18px;">
                            <p style="color:#efefef; font-size:16px; line-height:1.8; margin:0 0 16px;">Ola, {author}.</p>
                            <p style="color:#efefef; font-size:15px; line-height:1.8; margin:0 0 16px;">{message}</p>
                            <div style="background:#0d0d0d; border-left:4px solid #0603b4; padding: 18px 20px; margin-bottom: 18px;">
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.24em; font-size:10px; margin-bottom:8px;">Relato</div>
                                <div style="color:#ffffff; font-size:22px; font-family:'Orbitron', 'Arial Black', sans-serif; margin-bottom: 14px;">{titulo_relato}</div>
                                <div style="color:#8f8f8f; text-transform:uppercase; letter-spacing:0.24em; font-size:10px; margin-bottom:8px;">Comentario</div>
                                <div style="color:#efefef; font-size:15px; line-height:1.8;">{excerpt}</div>
                            </div>
                            <div style="text-align:center; margin: 0 0 14px;">
                                <a href="{post_url}" style="display:inline-block; margin: 6px; padding:14px 24px; background:#0603b4; color:#ffffff; text-decoration:none; font-family:'Orbitron', 'Arial Black', sans-serif; font-size:12px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; border:1px solid #0603b4;">Abrir post</a>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
""".strip()


def send_user_status_notification_email(relato=None, comentario=None, status='aprovado'):
    if status not in {'aprovado', 'rejeitado'}:
        raise EmailDeliveryError('Status de notificacao invalido')

    try:
        if relato is not None:
            if not relato.email:
                return None
            subject = f'Seu relato foi {status} - DreamWalker Plane'
            html_body = _build_user_relato_status_html_email(relato, status)
            text_body = _build_user_relato_status_plain_text(relato, status)
            recipient = relato.email
        elif comentario is not None:
            if not comentario.email:
                return None
            subject = f'Seu comentario foi {status} - DreamWalker Plane'
            html_body = _build_user_comment_status_html_email(comentario, status)
            text_body = _build_user_comment_status_plain_text(comentario, status)
            recipient = comentario.email
        else:
            raise EmailDeliveryError('Nenhum conteudo informado para notificacao ao usuario')

        _send_email_payload(recipient, subject, html_body, text_body)
        print('[INFO] Notificacao de status enviada ao usuario.')
        return 202
    except requests.exceptions.Timeout as e:
        print(f"[ERROR] Timeout ao enviar notificacao de status ao usuario: {e}")
        print(traceback.format_exc())
        raise EmailNetworkError('Timeout na comunicacao com o provedor de email') from e
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Falha de conexao ao enviar notificacao de status ao usuario: {e}")
        print(traceback.format_exc())
        raise EmailNetworkError('Provedor de email indisponivel ou inacessivel') from e
    except requests.exceptions.HTTPError as e:
        response_body = ''
        if e.response is not None:
            response_body = e.response.text
        print(f"[ERROR] API de email retornou erro HTTP na notificacao de status ao usuario: {response_body}")
        print(traceback.format_exc())
        raise EmailDeliveryError('Provedor de email rejeitou a solicitacao') from e
    except EmailDeliveryError:
        raise
    except Exception as e:
        print(f"[ERROR] Erro inesperado ao notificar usuario sobre status: {e}")
        print(traceback.format_exc())
        raise EmailDeliveryError('Erro inesperado ao enviar notificacao de status ao usuario') from e