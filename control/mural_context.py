from collections import defaultdict
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload, load_only

from models import Comentario, Relato, db


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_mural_context(args):
    """Monta o contexto completo usado pela página do mural."""
    query = Relato.query.options(
        joinedload(Relato.comentarios).load_only(Comentario.id, Comentario.status)
    ).filter_by(status='aprovado')

    busca = (args.get('q', '') or '').strip()
    if busca:
        query = query.filter(
            Relato.titulo.contains(busca) | Relato.conteudo.contains(busca)
        )

    ano = _parse_int(args.get('ano'))
    mes = _parse_int(args.get('mes'))
    if ano:
        query = query.filter(db.extract('year', Relato.data_aprovacao) == ano)
    if mes:
        query = query.filter(db.extract('month', Relato.data_aprovacao) == mes)

    page = args.get('page', 1, type=int)
    paginacao = query.order_by(Relato.data_aprovacao.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False,
    )

    posts_por_ano = defaultdict(lambda: defaultdict(list))
    for post in paginacao.items:
        referencia = post.data_aprovacao or post.data_envio
        if not referencia:
            continue
        posts_por_ano[referencia.year][referencia.strftime('%B')].append(post)

    arquivo_map = {}
    arquivo_rows = db.session.query(
        func.extract('year', Relato.data_aprovacao).label('ano'),
        func.extract('month', Relato.data_aprovacao).label('mes'),
        func.count(Relato.id).label('total'),
    ).filter(
        Relato.status == 'aprovado',
        Relato.data_aprovacao.isnot(None),
    ).group_by(
        'ano',
        'mes',
    ).order_by(
        func.extract('year', Relato.data_aprovacao).desc(),
        func.extract('month', Relato.data_aprovacao).desc(),
    ).all()

    for row in arquivo_rows:
        ano_post = int(row.ano)
        mes_num = int(row.mes)
        total_mes = int(row.total)
        referencia = datetime(ano_post, mes_num, 1)
        mes_info = {
            'numero': mes_num,
            'nome': referencia.strftime('%B'),
            'total': total_mes,
        }

        if ano_post not in arquivo_map:
            arquivo_map[ano_post] = {
                'ano': ano_post,
                'total': 0,
                'meses': {},
            }

        if mes_num not in arquivo_map[ano_post]['meses']:
            arquivo_map[ano_post]['meses'][mes_num] = mes_info

        arquivo_map[ano_post]['total'] += total_mes

    arquivo_anos = []
    for ano_post in sorted(arquivo_map.keys(), reverse=True):
        ano_info = arquivo_map[ano_post]
        arquivo_anos.append({
            'ano': ano_info['ano'],
            'total': ano_info['total'],
            'meses': [
                ano_info['meses'][mes_num]
                for mes_num in sorted(ano_info['meses'].keys(), reverse=True)
            ],
        })

    posts_populares = Relato.query.filter_by(status='aprovado')\
        .order_by(Relato.visualizacoes.desc(), Relato.data_aprovacao.desc())\
        .limit(5)\
        .all()

    return {
        'posts_por_ano': {ano_post: dict(posts_mes) for ano_post, posts_mes in posts_por_ano.items()},
        'arquivo_anos': arquivo_anos,
        'posts_populares': posts_populares,
        'paginacao': paginacao,
        'busca': busca,
    }