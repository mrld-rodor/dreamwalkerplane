"""
blueprints/relatos.py - Sistema de Relatos dos Usuários
Usuário envia relato → status 'pendente' → admin valida → aparece no mural
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import db, Relato, Comentario, registrar_log_auditoria
from datetime import datetime
import bleach
import requests
import re
from control.mural_context import build_mural_context
from control.recaptcha import verify_recaptcha
from control.limiter import limiter
from control.csrf import csrf_protect, validate_csrf_token
from control.email_function import EmailDeliveryError, EmailNetworkError
from control.sendgrid_email import (
    send_notification_email,
    send_user_status_notification_email,
)

# Cria o Blueprint com prefixo /relatos
relatos_bp = Blueprint('relatos', __name__, url_prefix='/relatos')

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _admin_identity():
    """Retorna usuario e IP atual do admin para auditoria."""
    return (
        session.get('admin_username') or current_app.config.get('ADMIN_USERNAME') or 'admin',
        request.remote_addr,
    )


@relatos_bp.route('/mural')
def mural():
    """Mural público com busca, arquivo e posts populares."""
    return render_template('mural.html', **build_mural_context(request.args))


@relatos_bp.route('/enviar', methods=['GET', 'POST'])
@limiter.limit('5 per hour', methods=['POST'])
def enviar_relato():
    """
    Formulário para envio de relato
    GET: exibe o formulário
    POST: processa e salva com status 'pendente'
    """
    
    if request.method == 'POST':
        submitted_csrf_token = request.form.get('csrf_token')

        # 1. Coleta os dados do formulário
        autor = request.form.get('autor', '').strip()
        email = request.form.get('email', '').strip()
        titulo = request.form.get('titulo', '').strip()
        conteudo = request.form.get('conteudo', '').strip()

        if not validate_csrf_token(submitted_csrf_token):
            flash('Falha na validacao de seguranca do formulario. Tente novamente.', 'danger')
            return render_template('enviar_relato.html', 
                                  autor=autor, 
                                  email=email,
                                  titulo=titulo, 
                                  conteudo=conteudo,
                                  config=current_app.config,
                                  relato_recaptcha_site_key=current_app.config.get('RELATO_RECAPTCHA_SITE_KEY')), 400
        
        # 2. Validação básica
        erros = []
        
        if not autor:
            erros.append('Nome é obrigatório')
        elif len(autor) > 100:
            erros.append('Nome muito longo (máximo 100 caracteres)')

        if email:
            if len(email) > 100:
                erros.append('Email muito longo (máximo 100 caracteres)')
            elif not EMAIL_REGEX.match(email):
                erros.append('Informe um email válido para receber o aviso de moderação')
        
        if not titulo:
            erros.append('Título é obrigatório')
        elif len(titulo) > 200:
            erros.append('Título muito longo (máximo 200 caracteres)')
        
        if not conteudo:
            erros.append('Conteúdo do relato é obrigatório')
        elif len(conteudo) < 10:
            erros.append('Relato muito curto (mínimo 10 caracteres)')
        elif len(conteudo) > 5000:
            erros.append('Relato muito longo (máximo 5000 caracteres)')
        
        # 3. Valida reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')
        secret_key = current_app.config.get('RELATO_RECAPTCHA_SECRET_KEY')
        
        if secret_key:
            recaptcha_ok, recaptcha_error = verify_recaptcha(
                secret_key=secret_key,
                response_token=recaptcha_response,
                remote_ip=request.remote_addr,
                logger=current_app.logger,
                form_name='relato'
            )
            if not recaptcha_ok:
                erros.append(recaptcha_error)
        
        # 4. Sanitização do conteúdo (remove XSS)
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'blockquote']
        conteudo_sanitizado = bleach.clean(conteudo, tags=allowed_tags, strip=True)
        
        # 5. Se houver erros, volta com as mensagens
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('enviar_relato.html', 
                                  autor=autor, 
                                  email=email,
                                  titulo=titulo, 
                                  conteudo=conteudo,
                                  config=current_app.config,
                                  relato_recaptcha_site_key=current_app.config.get('RELATO_RECAPTCHA_SITE_KEY'))
        
        # 6. Salva no banco de dados
        ip = request.remote_addr
        
        novo_relato = Relato(
            autor=autor,
            email=email if email else None,
            titulo=titulo,
            conteudo=conteudo_sanitizado,
            status='pendente',  # Aguardando aprovação do admin
            ip_remetente=ip
        )
        
        try:
            db.session.add(novo_relato)
            db.session.commit()

            try:
                send_notification_email(novo_relato)
            except (EmailDeliveryError, EmailNetworkError) as notification_error:
                current_app.logger.warning(
                    'Relato salvo, mas a notificacao ao admin falhou: %s',
                    notification_error,
                )
            
            flash('Seu relato foi enviado com sucesso! Aguarde a aprovação para aparecer no mural.', 'success')
            return redirect(url_for('relatos.mural'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erro ao salvar relato: {str(e)}')
            flash('Erro ao enviar relato. Tente novamente mais tarde.', 'danger')
            return render_template('enviar_relato.html', 
                                  autor=autor, 
                                  email=email,
                                  titulo=titulo, 
                                  conteudo=conteudo,
                                  config=current_app.config,
                                  relato_recaptcha_site_key=current_app.config.get('RELATO_RECAPTCHA_SITE_KEY'))
    
    # GET: exibe formulário vazio
    return render_template('enviar_relato.html', config=current_app.config, relato_recaptcha_site_key=current_app.config.get('RELATO_RECAPTCHA_SITE_KEY'))


# ============================================================
# ROTAS ADMINISTRATIVAS (protegidas por senha simples)
# ============================================================

@relatos_bp.route('/admin/pendentes')
def admin_pendentes():
    """
    Lista relatos pendentes de aprovação
    Protegido por senha (via session)
    """
    if not session.get('admin_logged'):
        return redirect(url_for('relatos.admin_login'))
    
    relatos_pendentes = Relato.query.filter_by(status='pendente')\
        .order_by(Relato.data_envio.desc())\
        .all()
    comentarios_pendentes = Comentario.query.filter_by(status='pendente')\
        .order_by(Comentario.data_envio.desc())\
        .all()
    
    return render_template(
        'admin_relatos.html',
        relatos=relatos_pendentes,
        comentarios=comentarios_pendentes,
        status_filtro='pendente'
    )


@relatos_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """
    Login simples para administrador
    """
    if request.method == 'POST':
        submitted_csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(submitted_csrf_token):
            flash('Falha na validacao de seguranca do formulario. Tente novamente.', 'danger')
            return render_template('admin_login.html'), 400

        senha = request.form.get('password', request.form.get('senha', ''))
        senha_correta = current_app.config.get('ADMIN_PASSWORD', 'admin123')
        
        if senha == senha_correta:
            session['admin_logged'] = True
            session['admin_username'] = request.form.get('username', '').strip() or current_app.config.get('ADMIN_USERNAME') or 'admin'
            admin_usuario, ip_admin = _admin_identity()
            registrar_log_auditoria(
                acao='login',
                alvo_tipo='sessao_admin',
                descricao='Login administrativo realizado pela area de relatos.',
                admin_usuario=admin_usuario,
                ip_admin=ip_admin,
            )
            db.session.commit()
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('relatos.admin_pendentes'))
        else:
            flash('Senha incorreta!', 'danger')
    
    return render_template('admin_login.html')


@relatos_bp.route('/admin/aprovar/<int:relato_id>', methods=['POST'])
@csrf_protect
def aprovar_relato(relato_id):
    """
    Aprova um relato pendente
    """
    if not session.get('admin_logged'):
        return redirect(url_for('relatos.admin_login'))
    
    relato = Relato.query.get_or_404(relato_id)
    
    if relato.status == 'pendente':
        admin_usuario, ip_admin = _admin_identity()
        registrar_log_auditoria(
            acao='aprovar_relato',
            alvo_tipo='relato',
            alvo_id=relato.id,
            descricao=f'Relato "{relato.titulo}" aprovado pelo admin.',
            admin_usuario=admin_usuario,
            ip_admin=ip_admin,
        )
        relato.status = 'aprovado'
        relato.data_aprovacao = datetime.utcnow()
        db.session.commit()

        if relato.email:
            try:
                send_user_status_notification_email(relato=relato, status='aprovado')
            except (EmailDeliveryError, EmailNetworkError) as notification_error:
                current_app.logger.warning(
                    'Relato aprovado, mas o email ao usuario falhou: %s',
                    notification_error,
                )

        flash(f'Relato "{relato.titulo}" aprovado com sucesso!', 'success')
    
    return redirect(url_for('relatos.admin_pendentes'))


@relatos_bp.route('/admin/rejeitar/<int:relato_id>', methods=['POST'])
@csrf_protect
def rejeitar_relato(relato_id):
    """
    Rejeita um relato pendente (pode ser excluído ou apenas marcado)
    """
    if not session.get('admin_logged'):
        return redirect(url_for('relatos.admin_login'))
    
    relato = Relato.query.get_or_404(relato_id)
    
    # Opção 1: Marcar como rejeitado e não mostrar
    admin_usuario, ip_admin = _admin_identity()
    registrar_log_auditoria(
        acao='rejeitar_relato',
        alvo_tipo='relato',
        alvo_id=relato.id,
        descricao=f'Relato "{relato.titulo}" rejeitado pelo admin.',
        admin_usuario=admin_usuario,
        ip_admin=ip_admin,
    )
    relato.status = 'rejeitado'
    db.session.commit()

    if relato.email:
        try:
            send_user_status_notification_email(relato=relato, status='rejeitado')
        except (EmailDeliveryError, EmailNetworkError) as notification_error:
            current_app.logger.warning(
                'Relato rejeitado, mas o email ao usuario falhou: %s',
                notification_error,
            )

    flash(f'Relato "{relato.titulo}" rejeitado.', 'warning')
    
    # Opção 2: Excluir permanentemente (descomente se preferir)
    # db.session.delete(relato)
    # db.session.commit()
    
    return redirect(url_for('relatos.admin_pendentes'))


@relatos_bp.route('/admin/comentarios/aprovar/<int:comentario_id>', methods=['POST'])
@csrf_protect
def aprovar_comentario(comentario_id):
    """Aprova um comentário pendente."""
    if not session.get('admin_logged'):
        return redirect(url_for('relatos.admin_login'))

    comentario = Comentario.query.get_or_404(comentario_id)

    if comentario.status == 'pendente':
        admin_usuario, ip_admin = _admin_identity()
        registrar_log_auditoria(
            acao='aprovar_comentario',
            alvo_tipo='comentario',
            alvo_id=comentario.id,
            descricao=f'Comentario de "{comentario.autor}" aprovado pelo admin.',
            admin_usuario=admin_usuario,
            ip_admin=ip_admin,
        )
        comentario.status = 'aprovado'
        db.session.commit()

        if comentario.email:
            try:
                send_user_status_notification_email(comentario=comentario, status='aprovado')
            except (EmailDeliveryError, EmailNetworkError) as notification_error:
                current_app.logger.warning(
                    'Comentario aprovado, mas o email ao usuario falhou: %s',
                    notification_error,
                )

        flash(f'Comentário de "{comentario.autor}" aprovado com sucesso!', 'success')

    return redirect(url_for('relatos.admin_pendentes'))


@relatos_bp.route('/admin/comentarios/rejeitar/<int:comentario_id>', methods=['POST'])
@csrf_protect
def rejeitar_comentario(comentario_id):
    """Rejeita um comentário pendente."""
    if not session.get('admin_logged'):
        return redirect(url_for('relatos.admin_login'))

    comentario = Comentario.query.get_or_404(comentario_id)
    admin_usuario, ip_admin = _admin_identity()
    registrar_log_auditoria(
        acao='rejeitar_comentario',
        alvo_tipo='comentario',
        alvo_id=comentario.id,
        descricao=f'Comentario de "{comentario.autor}" rejeitado pelo admin.',
        admin_usuario=admin_usuario,
        ip_admin=ip_admin,
    )
    comentario.status = 'rejeitado'
    db.session.commit()

    if comentario.email:
        try:
            send_user_status_notification_email(comentario=comentario, status='rejeitado')
        except (EmailDeliveryError, EmailNetworkError) as notification_error:
            current_app.logger.warning(
                'Comentario rejeitado, mas o email ao usuario falhou: %s',
                notification_error,
            )

    flash(f'Comentário de "{comentario.autor}" rejeitado.', 'warning')

    return redirect(url_for('relatos.admin_pendentes'))


@relatos_bp.route('/admin/logout', methods=['POST'])
@csrf_protect
def admin_logout():
    """Logout do admin"""
    if session.get('admin_logged'):
        admin_usuario, ip_admin = _admin_identity()
        registrar_log_auditoria(
            acao='logout',
            alvo_tipo='sessao_admin',
            descricao='Logout administrativo realizado pela area de relatos.',
            admin_usuario=admin_usuario,
            ip_admin=ip_admin,
        )
        db.session.commit()
    session.pop('admin_logged', None)
    session.pop('admin_username', None)
    flash('Logout realizado!', 'info')
    return redirect(url_for('relatos.mural'))