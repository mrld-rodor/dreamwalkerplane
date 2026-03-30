"""
app.py - DreamWalker Plane
Arquivo principal que inicializa a aplicação Flask
"""

import os
from flask import Flask
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa as extensões
from models import db
from control.contador import inicializar_contador, obter_contadores  

# Importa os Blueprints
from blueprints.main import main_bp
from blueprints.relatos import relatos_bp
from blueprints.contatos import contato_bp
from blueprints.doacoes import doacoes_bp


def create_app():
    """Factory da aplicação Flask"""
    
    app = Flask(__name__)
    
    # ========== CONFIGURAÇÕES ==========
    # Segurança
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise ValueError("SECRET_KEY não configurada! Defina no .env")
    
    # Banco de dados (MariaDB/MySQL)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL não configurada! Defina no .env")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 5,
        'max_overflow': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 30,
            'read_timeout': 60,
            'write_timeout': 60,
            'autocommit': True,
        }
    }
    
    # Email
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_LOGIN')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
    
    # reCAPTCHA
    app.config['RECAPTCHA_SITE_KEY'] = os.getenv('RECAPTCHA_SITE_KEY')
    app.config['RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY')
    
    # Hotmart Links
    app.config['HOTMART_CONTO_000'] = os.getenv('HOTMART_CONTO_000')
    app.config['HOTMART_CONTO_001'] = os.getenv('HOTMART_CONTO_001')
    app.config['HOTMART_CONTO_002'] = os.getenv('HOTMART_CONTO_002')
    
    # PayPal
    app.config['PAYPAL_LINK'] = os.getenv('PAYPAL_LINK')
    
    # Admin
    app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD')
    app.config['ADMIN_USERNAME'] = os.getenv('ADMIN_USERNAME')
    
    # ========== INICIALIZA EXTENSÕES ==========
    db.init_app(app)
    
    # ========== CRIA TABELAS SE NÃO EXISTIREM ==========
    with app.app_context():
        db.create_all()
        print("[INFO] Banco de dados verificado/criado com sucesso!")
    
    # ========== INICIALIZA O CONTADOR ==========
    inicializar_contador()
    
    # ========== REGISTRA OS BLUEPRINTS ==========
    app.register_blueprint(main_bp)
    app.register_blueprint(relatos_bp)
    app.register_blueprint(contato_bp)
    app.register_blueprint(doacoes_bp)
    
    return app


# Cria a aplicação para o servidor
app = create_app()


if __name__ == '__main__':
    # Em desenvolvimento
    app.run(host='0.0.0.0', port=5000, debug=True)