"""
control/sendgrid_email.py
Envio de emails usando SendGrid
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(contato):
    """
    Envia email usando SendGrid
    
    Args:
        contato: Objeto com nome, email e mensagem
    """
    # Pega as configurações do ambiente
    api_key = os.environ.get('SENDGRID_API_KEY')
    from_email = os.environ.get('EMAIL_FROM')
    to_email = os.environ.get('EMAIL_RECEIVER')
    
    if not api_key:
        print("[ERROR] SENDGRID_API_KEY não configurada!")
        raise Exception("SendGrid não configurado")
    
    if not from_email:
        print("[ERROR] EMAIL_FROM não configurada!")
        raise Exception("Email remetente não configurado")
    
    # Cria o email
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=f'📝 Novo contato no DreamWalker Plane - {contato.nome}',
        html_content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #6c5ce7; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f5f5f5; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #6c5ce7; }}
                .message {{ background: white; padding: 15px; border-left: 4px solid #6c5ce7; margin-top: 10px; }}
                .footer {{ text-align: center; font-size: 12px; color: #888; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>✨ DreamWalker Plane ✨</h2>
                    <p>Novo contato recebido</p>
                </div>
                <div class="content">
                    <div class="field">
                        <span class="label">👤 Nome:</span>
                        <p>{contato.nome}</p>
                    </div>
                    <div class="field">
                        <span class="label">📧 Email:</span>
                        <p>{contato.email}</p>
                    </div>
                    <div class="field">
                        <span class="label">💬 Mensagem:</span>
                        <div class="message">
                            {contato.mensagem.replace(chr(10), '<br>')}
                        </div>
                    </div>
                </div>
                <div class="footer">
                    <p>Enviado automaticamente pelo DreamWalker Plane</p>
                </div>
            </div>
        </body>
        </html>
        """,
        plain_content=f"""
Novo contato no DreamWalker Plane!

Nome: {contato.nome}
Email: {contato.email}
Mensagem:
{contato.mensagem}

---
Enviado automaticamente pelo DreamWalker Plane
        """
    )
    
    try:
        # Envia o email
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        print(f"[INFO] Email enviado com sucesso! Status: {response.status_code}")
        
        if response.status_code not in [200, 202]:
            print(f"[WARN] Resposta inesperada: {response.body}")
        
        return response.status_code
        
    except Exception as e:
        print(f"[ERROR] Falha ao enviar email: {e}")
        raise