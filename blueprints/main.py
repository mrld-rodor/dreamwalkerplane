"""
blueprints/main.py - Rotas principais do DreamWalker Plane
Início, Contos, Sonhar, Políticas e Termos
"""

from flask import Blueprint, render_template, request, current_app, session, redirect, url_for, flash
from control.contador import atualizar_contadores, obter_contadores
import random
from models import Relato, Comentario, LogAuditoria, db, registrar_log_auditoria
from control.admin_auth import (
    admin_login_required,
    clear_admin_session,
    establish_admin_session,
    get_admin_identity,
    is_admin_logged_in,
    verify_admin_credentials,
)
from control.recaptcha import verify_recaptcha
from control.limiter import limiter
from control.csrf import csrf_protect, validate_csrf_token
from control.email_function import EmailDeliveryError, EmailNetworkError
from control.sendgrid_email import send_comment_notification_email
from control.analytics import build_dashboard_analytics

# Cria o Blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página inicial"""
    ip = request.remote_addr
    atualizar_contadores(visitas=1, ip=ip)
    return render_template('index.html')


def get_hotmart_links():
    """Retorna o mapeamento centralizado dos links de compra da Hotmart."""
    return {
        '002': current_app.config.get('HOTMART_CONTO_002', '#'),
        '001': current_app.config.get('HOTMART_CONTO_001', '#'),
        '000': current_app.config.get('HOTMART_CONTO_000', '#'),
    }


@main_bp.route('/contos')
def contos():
    """Página com lista de contos e links Hotmart"""
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
            'arquivo': 'conto_002.pdf'
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
            'arquivo': 'conto_001.pdf'
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
            'arquivo': 'conto_000.pdf'
        }
    ]
    
    return render_template('contos.html', contos=contos_lista)


@main_bp.route('/comprar/<conto_id>')
def comprar_conto(conto_id):
    """Conta o clique de compra e redireciona para o link correspondente da Hotmart."""
    hotmart_links = get_hotmart_links()
    hotmart_link = hotmart_links.get(conto_id)

    if not hotmart_link or hotmart_link == '#':
        flash('Link de compra indisponivel no momento.', 'warning')
        return redirect(url_for('main.contos'))

    ip = request.remote_addr
    atualizar_contadores(downloads=1, ip=ip)
    return redirect(hotmart_link)


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


# Rota de login do admin
@main_bp.route('/admin-login', methods=['GET', 'POST'])
@limiter.limit('5 per 15 minutes', methods=['POST'])
def admin_login():
    """Login administrativo"""
    # Se já estiver logado, redireciona para status
    if is_admin_logged_in():
        next_url = request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('main.status'))
    
    if request.method == 'POST':
        submitted_csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(submitted_csrf_token):
            flash('Falha na validacao de seguranca do formulario. Tente novamente.', 'danger')
            return render_template('admin_login.html'), 400

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        admin_user = current_app.config.get('ADMIN_USERNAME')

        if verify_admin_credentials(username, password):
            establish_admin_session(username=username or admin_user)
            admin_usuario, ip_admin = get_admin_identity()
            registrar_log_auditoria(
                acao='login',
                alvo_tipo='sessao_admin',
                descricao='Login administrativo realizado com sucesso.',
                admin_usuario=admin_usuario,
                ip_admin=ip_admin,
            )
            db.session.commit()
            flash('Login realizado com sucesso!', 'success')
            next_url = request.args.get('next') or request.form.get('next')
            return redirect(next_url or url_for('main.status'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
    
    return render_template('admin_login.html', next_url=request.args.get('next', ''))


# Rota de logout
@main_bp.route('/admin-logout', methods=['POST'])
@admin_login_required
@csrf_protect
def admin_logout():
    """Logout administrativo"""
    if is_admin_logged_in():
        admin_usuario, ip_admin = get_admin_identity()
        registrar_log_auditoria(
            acao='logout',
            alvo_tipo='sessao_admin',
            descricao='Logout administrativo realizado.',
            admin_usuario=admin_usuario,
            ip_admin=ip_admin,
        )
        db.session.commit()
    clear_admin_session()
    flash('Logout realizado!', 'info')
    return redirect(url_for('main.index'))


# Rota do status (protegida)
@main_bp.route('/status')
@admin_login_required
def status():
    """Página de status com estatísticas"""
    visitantes, downloads, visitas = obter_contadores()
    return render_template('status.html', visitantes=visitantes, downloads=downloads, visitas=visitas)


@main_bp.route('/admin-dashboard')
@admin_login_required
def admin_dashboard():
    """Dashboard administrativo com estatísticas"""

    visitantes, downloads, visitas = obter_contadores()
    period_days = request.args.get('periodo', default=30, type=int)

    # Estatísticas de relatos
    from models import Relato, Comentario
    total_relatos = Relato.query.count()
    relatos_aprovados = Relato.query.filter_by(status='aprovado').count()
    relatos_pendentes = Relato.query.filter_by(status='pendente').count()
    relatos_rejeitados = Relato.query.filter_by(status='rejeitado').count()
    ultimos_relatos = Relato.query.order_by(Relato.data_envio.desc()).limit(10).all()

    # Estatísticas de comentários
    total_comentarios = Comentario.query.count()
    comentarios_aprovados = Comentario.query.filter_by(status='aprovado').count()
    comentarios_pendentes = Comentario.query.filter_by(status='pendente').count()
    comentarios_rejeitados = Comentario.query.filter_by(status='rejeitado').count()
    ultimos_comentarios = Comentario.query.order_by(Comentario.data_envio.desc()).limit(10).all()
    logs_auditoria = LogAuditoria.query.order_by(LogAuditoria.data_acao.desc()).limit(20).all()

    analytics = build_dashboard_analytics(visitas, period_days=period_days)

    return render_template('admin_dashboard.html', 
                          visitantes=visitantes, 
                          downloads=downloads, 
                          visitas=visitas,
                          periodo_selecionado=analytics['period_days'],
                          visitas_labels=analytics['visitas_labels'],
                          visitas_data=analytics['visitas_data'],
                          downloads_data=analytics['downloads_data'],
                          visitas_tendencia=analytics['visitas_tendencia'],
                          horas_labels=analytics['horas_labels'],
                          horas_data=analytics['horas_data'],
                          hora_pico=analytics['hora_pico'],
                          hora_pico_total=analytics['hora_pico_total'],
                          total_relatos=total_relatos,
                          relatos_aprovados=relatos_aprovados,
                          relatos_pendentes=relatos_pendentes,
                          relatos_rejeitados=relatos_rejeitados,
                          ultimos_relatos=ultimos_relatos,
                          ultimos_comentarios=ultimos_comentarios,
                          logs_auditoria=logs_auditoria,
                          total_comentarios=total_comentarios,
                          comentarios_aprovados=comentarios_aprovados,
                          comentarios_pendentes=comentarios_pendentes,
                          comentarios_rejeitados=comentarios_rejeitados,
                          paises=analytics['paises'])


@main_bp.route('/admin-dashboard/relatos/<int:relato_id>/delete', methods=['POST'])
@admin_login_required
@csrf_protect
def admin_delete_relato(relato_id):
    """Exclui um relato diretamente pelo dashboard."""
    relato = Relato.query.get_or_404(relato_id)
    titulo = relato.titulo
    admin_usuario, ip_admin = get_admin_identity()
    registrar_log_auditoria(
        acao='excluir_relato',
        alvo_tipo='relato',
        alvo_id=relato.id,
        descricao=f'Relato "{titulo}" excluido pelo admin.',
        admin_usuario=admin_usuario,
        ip_admin=ip_admin,
    )
    db.session.delete(relato)
    db.session.commit()
    flash(f'Relato "{titulo}" apagado com sucesso.', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main_bp.route('/admin-dashboard/comentarios/<int:comentario_id>/delete', methods=['POST'])
@admin_login_required
@csrf_protect
def admin_delete_comentario(comentario_id):
    """Exclui um comentário diretamente pelo dashboard."""
    comentario = Comentario.query.get_or_404(comentario_id)
    autor = comentario.autor
    admin_usuario, ip_admin = get_admin_identity()
    registrar_log_auditoria(
        acao='excluir_comentario',
        alvo_tipo='comentario',
        alvo_id=comentario.id,
        descricao=f'Comentario de "{autor}" excluido pelo admin.',
        admin_usuario=admin_usuario,
        ip_admin=ip_admin,
    )
    db.session.delete(comentario)
    db.session.commit()
    flash(f'Comentário de "{autor}" apagado com sucesso.', 'success')
    return redirect(url_for('main.admin_dashboard'))



@main_bp.route('/mural')
def mural():
    return redirect(url_for('relatos.mural', **request.args), code=302)


@main_bp.route('/post/<int:post_id>')
def ver_post(post_id):
    post = Relato.query.get_or_404(post_id)
    
    # Incrementar visualizações
    post.visualizacoes += 1
    db.session.commit()
    
    comentarios_aprovados = Comentario.query.filter_by(relato_id=post_id, status='aprovado').order_by(Comentario.data_envio.desc()).all()
    comment_recaptcha_site_key = current_app.config.get('COMMENT_RECAPTCHA_SITE_KEY')
    comment_recaptcha_secret_key = current_app.config.get('COMMENT_RECAPTCHA_SECRET_KEY')
    use_math_captcha = not (comment_recaptcha_site_key and comment_recaptcha_secret_key)

    captcha_left = None
    captcha_right = None
    if use_math_captcha:
        captcha_left = random.randint(1, 9)
        captcha_right = random.randint(1, 9)
        session['comment_captcha_answer'] = captcha_left + captcha_right
    else:
        session.pop('comment_captcha_answer', None)
    
    return render_template(
        'post.html',
        post=post,
        comentarios_aprovados=comentarios_aprovados,
        comment_recaptcha_site_key=comment_recaptcha_site_key,
        use_math_captcha=use_math_captcha,
        captcha_left=captcha_left,
        captcha_right=captcha_right
    )


@main_bp.route('/post/<int:post_id>/comentar', methods=['POST'])
@limiter.limit('5 per hour')
def comentar(post_id):
    submitted_csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(submitted_csrf_token):
        flash('Falha na validacao de seguranca do formulario. Tente novamente.', 'danger')
        return redirect(url_for('main.ver_post', post_id=post_id))

    autor = request.form.get('autor', '').strip()
    email = request.form.get('email', '').strip()
    conteudo = request.form.get('conteudo', '').strip()
    captcha_answer = request.form.get('captcha_answer', '').strip()
    recaptcha_response = request.form.get('g-recaptcha-response', '').strip()
    ip = request.remote_addr
    
    if not autor or not conteudo:
        flash('Nome e comentário são obrigatórios!', 'danger')
        return redirect(url_for('main.ver_post', post_id=post_id))

    comment_recaptcha_secret_key = current_app.config.get('COMMENT_RECAPTCHA_SECRET_KEY')
    comment_recaptcha_site_key = current_app.config.get('COMMENT_RECAPTCHA_SITE_KEY')

    if comment_recaptcha_secret_key and comment_recaptcha_site_key:
        recaptcha_ok, recaptcha_error = verify_recaptcha(
            secret_key=comment_recaptcha_secret_key,
            response_token=recaptcha_response,
            remote_ip=request.remote_addr,
            logger=current_app.logger,
            form_name='comentario'
        )
        if not recaptcha_ok:
            flash(recaptcha_error, 'danger')
            return redirect(url_for('main.ver_post', post_id=post_id))
    else:
        captcha_expected = session.get('comment_captcha_answer')
        if captcha_expected is None or not captcha_answer.isdigit() or int(captcha_answer) != captcha_expected:
            flash('Captcha invalido. Resolva a conta antes de enviar o comentario.', 'danger')
            return redirect(url_for('main.ver_post', post_id=post_id))
    
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

    try:
        send_comment_notification_email(comentario)
    except (EmailDeliveryError, EmailNetworkError) as notification_error:
        current_app.logger.warning(
            'Comentario salvo, mas a notificacao ao admin falhou: %s',
            notification_error,
        )

    session.pop('comment_captcha_answer', None)
    
    flash('Comentário enviado! Aguarde aprovação.', 'success')
    return redirect(url_for('main.ver_post', post_id=post_id))