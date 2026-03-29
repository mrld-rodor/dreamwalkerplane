"""
blueprints/main.py - Rotas principais do DreamWalker Plane
Início, Contos, Sonhar, Políticas e Termos
"""

from flask import Blueprint, render_template, request, current_app, session, redirect, url_for, flash
from control.contador import atualizar_contadores, obter_contadores
from functools import wraps
import os

# Cria o Blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página inicial"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    atualizar_contadores(visitas=1, ip=ip)
    return render_template('index.html')


@main_bp.route('/contos')
def contos():
    """Página com lista de contos e links Hotmart"""
    # Pega os links do Hotmart das variáveis de ambiente
    hotmart_links = {
        'conto_000': current_app.config.get('HOTMART_CONTO_000', '#'),
        'conto_001': current_app.config.get('HOTMART_CONTO_001', '#'),
        'conto_002': current_app.config.get('HOTMART_CONTO_002', '#'),
    }
    
    # Lista dos contos com seus dados
    contos_lista = [
        {
            'id': '002',
            'titulo': 'O Carnaval',
            'data': '21/Dec/2024',
            'descricao': '"O Carnaval" - O conto que nasceu de uma série de intensos sonhos lúcidos...',
            'arquivo': 'conto_002.pdf',
            'hotmart_link': hotmart_links['conto_002']
        },
        {
            'id': '001',
            'titulo': 'O Trem',
            'data': '21/Dec/2024',
            'descricao': '"O Trem" – Um conto surreal e enigmático, no qual um grupo de jovens presencia um trem misterioso...',
            'arquivo': 'conto_001.pdf',
            'hotmart_link': hotmart_links['conto_001']
        },
        {
            'id': '000',
            'titulo': 'O Grande Livro',
            'data': '21/Dec/2024',
            'descricao': '"O Grande Livro" – Um conto com uma atmosfera de mistério, suspense e um toque filosófico...',
            'arquivo': 'conto_000.pdf',
            'hotmart_link': hotmart_links['conto_000']
        }
    ]
    
    return render_template('contos.html', contos=contos_lista)


@main_bp.route('/sonhar')
def sonhar():
    """Página O Sonhar (em manutenção)"""
    return render_template('sonhar.html')


@main_bp.route('/termosuso')
def termosuso():
    """Termos de Uso"""
    return render_template('useterms.html')


@main_bp.route('/politica')
def politica():
    """Política de Privacidade"""
    return render_template('p_privacy.html')


# @main_bp.route('/download/<filename>')
# def download_file(filename):
#     """Download dos contos (atualiza contador)"""
#     ip = request.headers.get('X-Forwarded-For', request.remote_addr)
#     from control.contador import atualizar_contadores
#     atualizar_contadores(downloads=1, ip=ip)
#     return send_from_directory('static/download', filename)


# ==================== PROTEÇÃO DE ROTAS ADMIN ====================

def login_required(f):
    """Decorator para proteger rotas admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged'):
            flash('Acesso negado! Faça login primeiro.', 'danger')
            return redirect(url_for('main.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# Rota de login do admin
@main_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Login administrativo"""
    # Se já estiver logado, redireciona para status
    if session.get('admin_logged'):
        return redirect(url_for('main.status'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        admin_user = os.getenv('ADMIN_USERNAME')
        admin_pass = os.getenv('ADMIN_PASSWORD')
        
        if username == admin_user and password == admin_pass:
            session['admin_logged'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.status'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
    
    return render_template('admin_login.html')


# Rota de logout
@main_bp.route('/admin-logout')
def admin_logout():
    """Logout administrativo"""
    session.pop('admin_logged', None)
    flash('Logout realizado!', 'info')
    return redirect(url_for('main.index'))


# Rota do status (protegida)
@main_bp.route('/status')
@login_required
def status():
    """Página de status com estatísticas"""
    visitantes, downloads, visitas = obter_contadores()
    return render_template('status.html', visitantes=visitantes, downloads=downloads, visitas=visitas)


@main_bp.route('/admin-dashboard')
@login_required
def admin_dashboard():
    """Dashboard administrativo com estatísticas"""
    visitantes, downloads, visitas = obter_contadores()
    return render_template('admin_dashboard.html', 
                          visitantes=visitantes, 
                          downloads=downloads, 
                          visitas=visitas)





