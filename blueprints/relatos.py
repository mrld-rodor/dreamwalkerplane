"""
blueprints/relatos.py - Sistema de Relatos dos Usuários
Usuário envia relato → status 'pendente' → admin valida → aparece no mural
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import db, Relato, Comentario
from datetime import datetime
import bleach
import requests
from control.recaptcha import verify_recaptcha

# Cria o Blueprint com prefixo /relatos
relatos_bp = Blueprint('relatos', __name__, url_prefix='/relatos')


@relatos_bp.route('/mural')
def mural():
    """
    Mural público - mostra apenas relatos APROVADOS, agrupados por ano/mês
    """
    relatos_aprovados = Relato.query.filter_by(status='aprovado')\
        .order_by(Relato.data_aprovacao.desc())\
        .all()

    # Agrupa por ano/mês
    from collections import defaultdict
    import calendar
    posts_por_ano = defaultdict(lambda: defaultdict(list))
    for relato in relatos_aprovados:
        ano = relato.data_aprovacao.year if relato.data_aprovacao else relato.data_envio.year
        mes_num = (relato.data_aprovacao.month if relato.data_aprovacao else relato.data_envio.month)
        mes_nome = f"{mes_num:02d} - {calendar.month_name[mes_num]}"
        posts_por_ano[ano][mes_nome].append(relato)

    # Ordena anos e meses
    posts_por_ano = dict(sorted(posts_por_ano.items(), reverse=True))
    for ano in posts_por_ano:
        posts_por_ano[ano] = dict(sorted(posts_por_ano[ano].items(), reverse=True))

    return render_template('mural.html', posts_por_ano=posts_por_ano)


@relatos_bp.route('/enviar', methods=['GET', 'POST'])
def enviar_relato():
    """
    Formulário para envio de relato
    GET: exibe o formulário
    POST: processa e salva com status 'pendente'
    """
    
    if request.method == 'POST':
        # 1. Coleta os dados do formulário
        autor = request.form.get('autor', '').strip()
        titulo = request.form.get('titulo', '').strip()
        conteudo = request.form.get('conteudo', '').strip()
        
        # 2. Validação básica
        erros = []
        
        if not autor:
            erros.append('Nome é obrigatório')
        elif len(autor) > 100:
            erros.append('Nome muito longo (máximo 100 caracteres)')
        
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
                                  titulo=titulo, 
                                  conteudo=conteudo,
                                  config=current_app.config,
                                  relato_recaptcha_site_key=current_app.config.get('RELATO_RECAPTCHA_SITE_KEY'))
        
        # 6. Salva no banco de dados
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        novo_relato = Relato(
            autor=autor,
            titulo=titulo,
            conteudo=conteudo_sanitizado,
            status='pendente',  # Aguardando aprovação do admin
            ip_remetente=ip
        )
        
        try:
            db.session.add(novo_relato)
            db.session.commit()
            
            flash('Seu relato foi enviado com sucesso! Aguarde a aprovação para aparecer no mural.', 'success')
            return redirect(url_for('relatos.mural'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erro ao salvar relato: {str(e)}')
            flash('Erro ao enviar relato. Tente novamente mais tarde.', 'danger')
            return render_template('enviar_relato.html', 
                                  autor=autor, 
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
        senha = request.form.get('senha', '')
        senha_correta = current_app.config.get('ADMIN_PASSWORD', 'admin123')
        
        if senha == senha_correta:
            session['admin_logged'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('relatos.admin_pendentes'))
        else:
            flash('Senha incorreta!', 'danger')
    
    return render_template('admin_login.html')


@relatos_bp.route('/admin/aprovar/<int:relato_id>')
def aprovar_relato(relato_id):
    """
    Aprova um relato pendente
    """
    if not session.get('admin_logged'):
        return redirect(url_for('relatos.admin_login'))
    
    relato = Relato.query.get_or_404(relato_id)
    
    if relato.status == 'pendente':
        relato.status = 'aprovado'
        relato.data_aprovacao = datetime.utcnow()
        db.session.commit()
        flash(f'Relato "{relato.titulo}" aprovado com sucesso!', 'success')
    
    return redirect(url_for('relatos.admin_pendentes'))


@relatos_bp.route('/admin/rejeitar/<int:relato_id>')
def rejeitar_relato(relato_id):
    """
    Rejeita um relato pendente (pode ser excluído ou apenas marcado)
    """
    if not session.get('admin_logged'):
        return redirect(url_for('relatos.admin_login'))
    
    relato = Relato.query.get_or_404(relato_id)
    
    # Opção 1: Marcar como rejeitado e não mostrar
    relato.status = 'rejeitado'
    db.session.commit()
    flash(f'Relato "{relato.titulo}" rejeitado.', 'warning')
    
    # Opção 2: Excluir permanentemente (descomente se preferir)
    # db.session.delete(relato)
    # db.session.commit()
    
    return redirect(url_for('relatos.admin_pendentes'))


@relatos_bp.route('/admin/comentarios/aprovar/<int:comentario_id>')
def aprovar_comentario(comentario_id):
    """Aprova um comentário pendente."""
    if not session.get('admin_logged'):
        return redirect(url_for('relatos.admin_login'))

    comentario = Comentario.query.get_or_404(comentario_id)

    if comentario.status == 'pendente':
        comentario.status = 'aprovado'
        db.session.commit()
        flash(f'Comentário de "{comentario.autor}" aprovado com sucesso!', 'success')

    return redirect(url_for('relatos.admin_pendentes'))


@relatos_bp.route('/admin/comentarios/rejeitar/<int:comentario_id>')
def rejeitar_comentario(comentario_id):
    """Rejeita um comentário pendente."""
    if not session.get('admin_logged'):
        return redirect(url_for('relatos.admin_login'))

    comentario = Comentario.query.get_or_404(comentario_id)
    comentario.status = 'rejeitado'
    db.session.commit()
    flash(f'Comentário de "{comentario.autor}" rejeitado.', 'warning')

    return redirect(url_for('relatos.admin_pendentes'))


@relatos_bp.route('/admin/logout')
def admin_logout():
    """Logout do admin"""
    session.pop('admin_logged', None)
    flash('Logout realizado!', 'info')
    return redirect(url_for('relatos.mural'))