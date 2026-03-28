"""
blueprints/relatos.py - Sistema de Relatos dos Usuários
Usuário envia relato → status 'pendente' → admin valida → aparece no mural
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import db, Relato
from datetime import datetime
import bleach

# Cria o Blueprint com prefixo /relatos
relatos_bp = Blueprint('relatos', __name__, url_prefix='/relatos')


@relatos_bp.route('/mural')
def mural():
    """
    Mural público - mostra apenas relatos APROVADOS
    Ordenados do mais recente para o mais antigo
    """
    # Busca todos os relatos aprovados
    relatos_aprovados = Relato.query.filter_by(status='aprovado')\
        .order_by(Relato.data_aprovacao.desc())\
        .all()
    
    return render_template('mural.html', relatos=relatos_aprovados)


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
        
        # 3. Sanitização do conteúdo (remove XSS)
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'blockquote']
        conteudo_sanitizado = bleach.clean(conteudo, tags=allowed_tags, strip=True)
        
        # 4. Se houver erros, volta com as mensagens
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('enviar_relato.html', 
                                  autor=autor, 
                                  titulo=titulo, 
                                  conteudo=conteudo)
        
        # 5. Salva no banco de dados
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
                                  conteudo=conteudo)
    
    # GET: exibe formulário vazio
    return render_template('enviar_relato.html')


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
    
    return render_template('admin_relatos.html', relatos=relatos_pendentes, status_filtro='pendente')


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


@relatos_bp.route('/admin/logout')
def admin_logout():
    """Logout do admin"""
    session.pop('admin_logged', None)
    flash('Logout realizado!', 'info')
    return redirect(url_for('relatos.mural'))