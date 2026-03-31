"""
blueprints/contato.py - Sistema de Contato com envio de email
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import requests
import os


# =====================================================
# CLASSE CONTATO
# =====================================================
class Contato:
    """Classe para armazenar os dados do formulário de contato"""
    def __init__(self, nome, email, mensagem):
        self.nome = nome
        self.email = email
        self.mensagem = mensagem
# =====================================================


contato_bp = Blueprint('contato', __name__, url_prefix='/contato')


@contato_bp.route('/', methods=['GET', 'POST'])
def contato():
    """
    Página de contato com formulário
    GET: exibe o formulário
    POST: envia email e salva no banco (opcional)
    """
    
    if request.method == 'POST':
        # 1. Coleta dados
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        mensagem = request.form.get('mensagem', '').strip()
        
        # 2. Validação básica
        erros = []
        
        if not nome:
            erros.append('Nome é obrigatório')
        elif len(nome) > 100:
            erros.append('Nome muito longo')
        
        if not email:
            erros.append('Email é obrigatório')
        
        if not mensagem:
            erros.append('Mensagem é obrigatória')
        elif len(mensagem) > 5000:
            erros.append('Mensagem muito longa (máximo 5000 caracteres)')
        
        # 3. Valida reCAPTCHA (se configurado)
        recaptcha_response = request.form.get('g-recaptcha-response')
        secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY')
        
        if secret_key and recaptcha_response:
            verify_url = 'https://www.google.com/recaptcha/api/siteverify'
            payload = {
                'secret': secret_key,
                'response': recaptcha_response,
                'remoteip': request.remote_addr
            }
            
            try:
                r = requests.post(verify_url, data=payload, timeout=10)
                result = r.json()
                if not result.get('success'):
                    erros.append('Verificação reCAPTCHA falhou. Tente novamente.')
            except:
                erros.append('Erro na verificação de segurança.')
        elif secret_key and not recaptcha_response:
            erros.append('Por favor, complete a verificação reCAPTCHA.')
        
        # 4. Se houver erros
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('contato.html', nome=nome, email=email, mensagem=mensagem, config=current_app.config)
        
        # 5. Envia email usando SendGrid
        try:
            from control.sendgrid_email import send_email
            contato = Contato(nome, email, mensagem)  # ← usa a classe definida acima
            send_email(contato)
            flash('Mensagem enviada com sucesso! Entrarei em contato em breve.', 'success')
            return redirect(url_for('contato.contato'))
            
        except Exception as e:
            current_app.logger.error(f'Erro ao enviar email: {str(e)}')
            flash('Erro ao enviar mensagem. Tente novamente mais tarde.', 'danger')
            return render_template('contato.html', nome=nome, email=email, mensagem=mensagem, config=current_app.config)
    
    # GET: exibe formulário
    return render_template('contato.html', config=current_app.config)