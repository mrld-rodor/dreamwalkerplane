"""
blueprints/main.py - Rotas principais do DreamWalker Plane
Início, Contos, Sonhar, Políticas e Termos
"""

from flask import Blueprint, render_template, request, current_app, session, redirect, url_for, flash
from control.contador import atualizar_contadores, obter_contadores
from functools import wraps
import os
from datetime import datetime
from collections import defaultdict
from models import Relato, Comentario, db

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
            'descricao': (
                '"O carnaval" é uma história sombria e perturbadora que mergulha nas \n'
                'profundezas do medo e da busca por salvação. Onofre, um jovem\n'
                'atormentado por um pesadelo crescente, vê seu bairro transformado em\n'
                'um cenário de carnaval macabro, onde monstros grotescos e entidades\n'
                'sobrenaturais desafiam a realidade. Depois de ser marcado por uma força\n'
                'misteriosa, ele se refugia em um esconderijo, apenas para ser arrastado\n'
                'em uma jornada pela estrada do desconhecido. Acompanhado por duas\n'
                'gêmeas enigmáticas e envolto em uma atmosfera de horror e surrealismo,\n'
                'Onofre tenta escapar para o único lugar que parece oferecer alguma\n'
                'esperança: o cemitério. Porém, o que ele encontrará no final de sua fuga\n'
                'será mais aterrador e revelador do que ele jamais imaginou. Um conto\n'
                'sobre os limites da realidade, a coragem de enfrentar o desconhecido e a\n'
                'eterna dúvida sobre o que é a verdadeira salvação.'
            ),
            'arquivo': 'conto_002.pdf',
            'hotmart_link': hotmart_links['conto_002']
        },
        {
            'id': '001',
            'titulo': 'O Trem',
            'data': '21/Dec/2024',
            'descricao': (
                'No pacato bairro Pindorama, um grupo de amigos revive\n'
                'momentos de infância em uma noite aparentemente tranquila.\n'
                'Porém, o som de uma voz vinda das profundezas do cosmos\n'
                'quebra a harmonia, anunciando a chegada de um trem negro e\n'
                'místico. Em meio ao caos que se segue, o protagonista enfrenta\n'
                'uma corrida contra o tempo, cercado por visões apocalípticas e\n'
                'homens de terno que flutuam sobre a lava, eliminando sem\n'
                'piedade os que cruzam seu caminho. A revelação final, de que ele\n'
                'pode ser um dos "nossos", coloca sua própria identidade em xeque,\n'
                'deixando-o à beira de um abismo de mistério e incerteza. Um\n'
                'conto de suspense, filosofia e mistério, "O Trem" é uma exploração\n'
                'profunda do desconhecido, onde realidade e sonho se entrelaçam\n'
                'de maneira perturbadora.'
            ),
            'arquivo': 'conto_001.pdf',
            'hotmart_link': hotmart_links['conto_001']
        },
        {
            'id': '000',
            'titulo': 'O Grande Livro',
            'data': '21/Dec/2024',
            'descricao': (
                'O Grande Livro não é apenas uma história de suspense e guerra,\n'
                ' mas uma profunda reflexão filosófica sobre o poder da coletividade e os \n'
                'mistérios do ser humano. Se você busca uma narrativa intrigante e que desafia \n'
                'as convenções da mente humana, este conto é para você. Prepare-se para ser \n'
                'envolvido em uma trama de mistério, tensão e revelações inesperadas.'
            ),
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
        
        admin_user = current_app.config.get('ADMIN_USERNAME')
        admin_pass = current_app.config.get('ADMIN_PASSWORD')
        
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



@main_bp.route('/mural')
def mural():
    # Buscar posts aprovados
    query = Relato.query.filter_by(status='aprovado')
    
    # Filtro de busca
    busca = request.args.get('q', '')
    if busca:
        query = query.filter(
            Relato.titulo.contains(busca) | Relato.conteudo.contains(busca)
        )
    
    # Filtro por ano/mês
    ano = request.args.get('ano')
    mes = request.args.get('mes')
    if ano:
        query = query.filter(db.extract('year', Relato.data_aprovacao) == int(ano))
    if mes:
        query = query.filter(db.extract('month', Relato.data_aprovacao) == int(mes))
    
    # Paginação (10 posts por página)
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Relato.data_aprovacao.desc()).paginate(page=page, per_page=10, error_out=False)
    posts = pagination.items
    
    # Organizar posts por ano/mês para o sidebar
    posts_por_ano = defaultdict(lambda: defaultdict(list))
    for post in posts:
        ano_post = post.data_aprovacao.year
        mes_post = post.data_aprovacao.strftime('%B')
        posts_por_ano[ano_post][mes_post].append(post)
    
    # Arquivo por ano/mês (sidebar)
    arquivo_anos = []
    for ano in sorted(set(db.session.query(db.extract('year', Relato.data_aprovacao)).filter_by(status='aprovado').all()), reverse=True):
        ano_val = ano[0]
        if ano_val:
            meses_ano = {}
            for post in Relato.query.filter_by(status='aprovado').filter(db.extract('year', Relato.data_aprovacao) == ano_val).all():
                mes_num = post.data_aprovacao.month
                mes_nome = post.data_aprovacao.strftime('%B')
                if mes_num not in meses_ano:
                    meses_ano[mes_num] = {'numero': mes_num, 'nome': mes_nome, 'total': 0}
                meses_ano[mes_num]['total'] += 1
            
            arquivo_anos.append({
                'ano': ano_val,
                'total': Relato.query.filter_by(status='aprovado').filter(db.extract('year', Relato.data_aprovacao) == ano_val).count(),
                'meses': list(meses_ano.values())
            })
    
    # Posts populares (mais visualizados)
    posts_populares = Relato.query.filter_by(status='aprovado').order_by(Relato.visualizacoes.desc()).limit(5).all()
    
    return render_template('mural.html',
                          posts_por_ano=dict(posts_por_ano),
                          arquivo_anos=arquivo_anos,
                          posts_populares=posts_populares,
                          paginacao=pagination,
                          busca=busca)


@main_bp.route('/post/<int:post_id>')
def ver_post(post_id):
    post = Relato.query.get_or_404(post_id)
    
    # Incrementar visualizações
    post.visualizacoes += 1
    db.session.commit()
    
    comentarios_aprovados = Comentario.query.filter_by(relato_id=post_id, status='aprovado').order_by(Comentario.data_envio.desc()).all()
    
    return render_template('post.html', post=post, comentarios_aprovados=comentarios_aprovados)


@main_bp.route('/post/<int:post_id>/comentar', methods=['POST'])
def comentar(post_id):
    autor = request.form.get('autor', '').strip()
    email = request.form.get('email', '').strip()
    conteudo = request.form.get('conteudo', '').strip()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    if not autor or not conteudo:
        flash('Nome e comentário são obrigatórios!', 'danger')
        return redirect(url_for('ver_post', post_id=post_id))
    
    comentario = Comentario(
        relato_id=post_id,
        autor=autor,
        email=email if email else None,
        conteudo=conteudo,
        status='pendente',
        ip_remetente=ip
    )
    
    db.session.add(comentario)
    db.session.commit()
    
    flash('Comentário enviado! Aguarde aprovação.', 'success')
    return redirect(url_for('ver_post', post_id=post_id))