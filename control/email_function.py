import smtplib
import socket
import ssl
import traceback
from html import escape
from pathlib import Path
from email.message import EmailMessage

from control.email_config import (
    email_receiver,
    login,
    mail_port,
    mail_server,
    mail_timeout,
    mail_use_ssl,
    mail_use_tls,
    senha,
)


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


def _build_html_email(contato, logo_cid=None):
    nome = escape(contato.nome)
    email = escape(contato.email)
    mensagem = escape(contato.mensagem).replace('\n', '<br>')
    logo_html = ''

    if logo_cid:
        logo_html = f"""
        <div style="text-align:center; margin: 8px 0 24px;">
            <img src="cid:{logo_cid}" alt="DreamWalker Plane" style="width: 110px; max-width: 110px; height: auto; display: inline-block; filter: drop-shadow(0 0 16px rgba(255,255,255,0.18));">
        </div>
        """

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
                            {logo_html}

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


def _attach_logo(message, logo_cid):
    logo_path = Path(__file__).resolve().parent.parent / 'static' / 'images' / 'amiraldo_logo_transparent_white.png'
    if not logo_path.exists():
        return False

    with logo_path.open('rb') as logo_file:
        logo_data = logo_file.read()

    message.get_payload()[-1].add_related(
        logo_data,
        maintype='image',
        subtype='png',
        cid=f'<{logo_cid}>',
        filename='dreamwalker-logo.png'
    )
    return True


def send_email(contato):
    msg = EmailMessage()
    msg['Subject'] = f'Visitante do DreamWalker Plane - {contato.nome}'
    msg['From'] = login
    msg['To'] = email_receiver
    msg['Reply-To'] = contato.email

    logo_cid = 'dreamwalker-logo'
    msg.set_content(_build_plain_text(contato))
    msg.add_alternative(_build_html_email(contato, logo_cid=logo_cid), subtype='html')
    has_logo = _attach_logo(msg, logo_cid)

    if not has_logo:
        msg.clear_content()
        msg.set_content(_build_plain_text(contato))
        msg.add_alternative(_build_html_email(contato, logo_cid=None), subtype='html')

    try:
        context = ssl.create_default_context()
        smtp_class = smtplib.SMTP_SSL if mail_use_ssl else smtplib.SMTP
        smtp_kwargs = {'timeout': mail_timeout}
        if mail_use_ssl:
            smtp_kwargs['context'] = context

        with smtp_class(mail_server, mail_port, **smtp_kwargs) as smtp:
            if mail_use_tls and not mail_use_ssl:
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
            smtp.login(login, senha)
            smtp.send_message(msg)
        print(f"[INFO] Email enviado com sucesso via SMTP ({mail_server}:{mail_port}).")
        return 202
    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERROR] SMTP Authentication Error: {e}")
        print(traceback.format_exc())
        raise
    except smtplib.SMTPException as e:
        print(f"[ERROR] SMTP Error: {e}")
        print(traceback.format_exc())
        raise
    except (TimeoutError, socket.timeout, OSError) as e:
        print(f"[ERROR] Falha de conexao SMTP ({mail_server}:{mail_port}): {e}")
        print(traceback.format_exc())
        raise
    except Exception as e:
        print(f"[ERROR] Erro ao enviar e-mail: {e}")
        print(traceback.format_exc())
        raise
