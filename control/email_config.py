import os
from dotenv import load_dotenv

load_dotenv()

mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
mail_port = int(os.getenv('MAIL_PORT', 587))
mail_use_tls = os.getenv('MAIL_USE_TLS', 'True') == 'True'
mail_use_ssl = os.getenv('MAIL_USE_SSL', 'False') == 'True'
login = os.getenv('EMAIL_LOGIN') or os.getenv('MAIL_USERNAME')
senha = os.getenv('EMAIL_PASSWORD') or os.getenv('MAIL_PASSWORD')
email_receiver = os.getenv('EMAIL_RECEIVER')

# Aviso simples para facilitar depuração em produção (Render: Config Vars)
missing = []
if not login:
	missing.append('EMAIL_LOGIN')
if not senha:
	missing.append('EMAIL_PASSWORD')
if not email_receiver:
	missing.append('EMAIL_RECEIVER')

if missing:
	print(f"[WARN] Variáveis de email ausentes: {', '.join(missing)}. Defina-as nas Config Vars do Render ou no .env.")

if mail_use_tls and mail_use_ssl:
	print('[WARN] MAIL_USE_TLS e MAIL_USE_SSL estao ativos ao mesmo tempo. Usando SSL e ignorando STARTTLS.')
