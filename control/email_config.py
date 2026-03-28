import os
from dotenv import load_dotenv

load_dotenv()

login = os.getenv('EMAIL_LOGIN')
senha = os.getenv('EMAIL_PASSWORD')
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
