"""
blueprints/contato.py - Sistema de Contato com envio de email
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from control.recaptcha import verify_recaptcha


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
        secret_key = current_app.config.get('CONTACT_RECAPTCHA_SECRET_KEY')
        
        if secret_key:
            recaptcha_ok, recaptcha_error = verify_recaptcha(
                secret_key=secret_key,
                response_token=recaptcha_response,
                remote_ip=request.remote_addr,
                logger=current_app.logger,
                form_name='contato'
            )
            if not recaptcha_ok:
                erros.append(recaptcha_error)
        
        # 4. Se houver erros
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template(
                'contato.html',
                nome=nome,
                email=email,
                mensagem=mensagem,
                contact_recaptcha_site_key=current_app.config.get('CONTACT_RECAPTCHA_SITE_KEY')
            )
        
        # 5. Envia email usando SMTP
        try:
            from control.email_function import EmailDeliveryError, EmailNetworkError, send_email
            contato = Contato(nome, email, mensagem)  # ← usa a classe definida acima
            send_email(contato)
            flash('Mensagem enviada com sucesso! Entrarei em contato em breve.', 'success')
            return redirect(url_for('contato.contato'))
        except EmailNetworkError:
            current_app.logger.warning('SMTP indisponivel ou sem rota de rede para o provedor configurado')
            flash('O formulario foi recebido, mas o servico de email esta temporariamente indisponivel. Tente novamente mais tarde.', 'warning')
            return render_template(
                'contato.html',
                nome=nome,
                email=email,
                mensagem=mensagem,
                contact_recaptcha_site_key=current_app.config.get('CONTACT_RECAPTCHA_SITE_KEY')
            )
        except EmailDeliveryError:
            current_app.logger.exception('Falha de entrega de email')
            flash('Nao foi possivel enviar sua mensagem por email no momento. Tente novamente mais tarde.', 'danger')
            return render_template(
                'contato.html',
                nome=nome,
                email=email,
                mensagem=mensagem,
                contact_recaptcha_site_key=current_app.config.get('CONTACT_RECAPTCHA_SITE_KEY')
            )
        except Exception:
            current_app.logger.exception('Erro ao enviar email')
            flash('Erro ao enviar mensagem. Tente novamente mais tarde.', 'danger')
            return render_template(
                'contato.html',
                nome=nome,
                email=email,
                mensagem=mensagem,
                contact_recaptcha_site_key=current_app.config.get('CONTACT_RECAPTCHA_SITE_KEY')
            )
    
    # GET: exibe formulário
    return render_template(
        'contato.html',
        contact_recaptcha_site_key=current_app.config.get('CONTACT_RECAPTCHA_SITE_KEY')
    )