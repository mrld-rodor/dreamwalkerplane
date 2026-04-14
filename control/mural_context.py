from collections import defaultdict

from models import Relato, db


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_mural_context(args):
    """Monta o contexto completo usado pela página do mural."""
    query = Relato.query.filter_by(status='aprovado')

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
    posts_aprovados = Relato.query.filter_by(status='aprovado')\
        .filter(Relato.data_aprovacao.isnot(None))\
        .order_by(Relato.data_aprovacao.desc())\
        .all()

    for post in posts_aprovados:
        referencia = post.data_aprovacao
        ano_post = referencia.year
        mes_num = referencia.month
        mes_info = {
            'numero': mes_num,
            'nome': referencia.strftime('%B'),
            'total': 0,
        }

        if ano_post not in arquivo_map:
            arquivo_map[ano_post] = {
                'ano': ano_post,
                'total': 0,
                'meses': {},
            }

        if mes_num not in arquivo_map[ano_post]['meses']:
            arquivo_map[ano_post]['meses'][mes_num] = mes_info

        arquivo_map[ano_post]['total'] += 1
        arquivo_map[ano_post]['meses'][mes_num]['total'] += 1

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