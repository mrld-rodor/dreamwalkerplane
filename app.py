"""
app.py - DreamWalker Plane
Arquivo principal que inicializa a aplicação Flask
"""

import os
from flask import Flask, flash, redirect, request, url_for
from dotenv import load_dotenv
from sqlalchemy import text

# Carrega variáveis de ambiente
load_dotenv()

# Importa as extensões
from models import db
from control.contador import inicializar_contador, obter_contadores  
from control.csrf import init_csrf
from control.limiter import limiter
from control.security import configure_proxy, configure_security

# Importa os Blueprints
from blueprints.main import main_bp
from blueprints.relatos import relatos_bp
from blueprints.contatos import contato_bp
from blueprints.doacoes import doacoes_bp


def create_app():
    """Factory da aplicação Flask"""
    
    app = Flask(__name__)
    configure_proxy(app)
    init_csrf(app)

    # ========== CONFIGURAÇÕES ==========
    # Segurança
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise ValueError("SECRET_KEY não configurada! Defina no .env")
    configure_security(app)
    
    # Banco de dados (postgresql com SSL)
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL não configurada! Defina no .env")

    # 🔧 CORREÇÃO DO SSL PARA POSTGRESQL NO RENDER
    # Adiciona sslmode=require se não estiver na URL
    if 'sslmode' not in database_url:
        if '?' in database_url:
            database_url += '&sslmode=require'
        else:
            database_url += '?sslmode=require'
    
    # Configuração SSL para psycopg2
    connect_args = {
        'connect_timeout': 30,
        'sslmode': 'require'  # ← CORREÇÃO: Adiciona SSL explicitamente
    }

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 5,
        'max_overflow': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': connect_args
    }

    # Email via API HTTP (ex.: Resend)
    app.config['EMAIL_API_URL'] = os.getenv('EMAIL_API_URL', 'https://api.resend.com/emails')
    app.config['EMAIL_API_TIMEOUT'] = float(os.getenv('EMAIL_API_TIMEOUT', '10'))
    app.config['EMAIL_SENDER'] = os.getenv('EMAIL_SENDER')
    app.config['EMAIL_RECEIVER'] = os.getenv('EMAIL_RECEIVER')
    
    # reCAPTCHA
    app.config['RECAPTCHA_SITE_KEY'] = os.getenv('RECAPTCHA_SITE_KEY')
    app.config['RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY')

    # Formulario de contato
    app.config['CONTACT_RECAPTCHA_SITE_KEY'] = os.getenv('RECAPTCHA_SITE_KEY')
    app.config['CONTACT_RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY')

    # Formulario de comentarios
    app.config['COMMENT_RECAPTCHA_SITE_KEY'] = os.getenv('RECAPTCHA_SITE_KEY2')
    app.config['COMMENT_RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY2')

    # Formulario de relatos
    app.config['RELATO_RECAPTCHA_SITE_KEY'] = os.getenv('RECAPTCHA_SITE_KEY3')
    app.config['RELATO_RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY3')
    
    # Hotmart Links
    app.config['HOTMART_CONTO_000'] = os.getenv('HOTMART_CONTO_000')
    app.config['HOTMART_CONTO_001'] = os.getenv('HOTMART_CONTO_001')
    app.config['HOTMART_CONTO_002'] = os.getenv('HOTMART_CONTO_002')
    
    # PayPal
    app.config['PAYPAL_LINK'] = os.getenv('PAYPAL_LINK')
    
    # Admin
    app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD')
    app.config['ADMIN_PASSWORD_HASH'] = os.getenv('ADMIN_PASSWORD_HASH')
    app.config['ADMIN_USERNAME'] = os.getenv('ADMIN_USERNAME')


    
    # ========== INICIALIZA EXTENSÕES ==========
    db.init_app(app)
    limiter.init_app(app)

    @app.errorhandler(429)
    def ratelimit_handler(error):
        if request.method == 'POST':
            flash('Voce atingiu o limite de 5 envios por hora para este IP. Tente novamente mais tarde.', 'warning')
            return redirect(request.referrer or url_for('main.index'))
        return 'Muitas requisicoes. Tente novamente mais tarde.', 429
    
    # ========== CRIA TABELAS SE NÃO EXISTIREM (lazy - na primeira requisição) ==========
    app.db_initialized = False
    
    @app.before_request
    def initialize_db_on_first_request():
        if not app.db_initialized:
            try:
                db.create_all()
                db.session.execute(
                    text('ALTER TABLE relatos ADD COLUMN IF NOT EXISTS email VARCHAR(100)')
                )
                db.session.commit()
                inicializar_contador()
                print("[INFO] Banco de dados verificado/criado com sucesso!")
                app.db_initialized = True
            except Exception as e:
                db.session.rollback()
                print(f"[WARN] Banco de dados não disponível: {e}")
                # Continua mesmo assim - a aplicação pode funcionar com algumas features limitadas
    
    # ========== REGISTRA OS BLUEPRINTS ==========
    app.register_blueprint(main_bp)
    app.register_blueprint(relatos_bp)
    app.register_blueprint(contato_bp)
    app.register_blueprint(doacoes_bp)
    
    return app



# Cria a aplicação para o servidor
app = create_app()


if __name__ == '__main__':
    # Em desenvolvimento: PORT vem do .env ou padrão 5000
    port = int(os.getenv('PORT', 5000))
    debug_enabled = os.getenv('FLASK_DEBUG', 'false').strip().lower() in {'1', 'true', 'yes', 'on'}
    app.run(host='0.0.0.0', port=port, debug=debug_enabled)