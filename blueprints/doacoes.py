"""
blueprints/doacoes.py - Seção de Doações e Links Hotmart
"""

from flask import Blueprint, render_template, current_app

doacoes_bp = Blueprint('doacoes', __name__, url_prefix='/doacoes')


@doacoes_bp.route('/')
def doacoes():
    """
    Página de doações e apoio
    """
    paypal_link = current_app.config.get('PAYPAL_LINK', '#')
    
    # Links dos contos na Hotmart
    hotmart_links = {
        'conto_000': current_app.config.get('HOTMART_CONTO_000', '#'),
        'conto_001': current_app.config.get('HOTMART_CONTO_001', '#'),
        'conto_002': current_app.config.get('HOTMART_CONTO_002', '#'),
    }
    
    # Lista de contos para exibir
    contos_para_venda = [
        {
            'id': '002',
            'titulo': 'O Carnaval',
            'descricao': 'Um conto surreal sobre sonhos lúcidos e transformação.',
            'preco': 'R$ 9,90',
            'hotmart_link': hotmart_links['conto_002']
        },
        {
            'id': '001',
            'titulo': 'O Trem',
            'descricao': 'Mistério e suspense em uma jornada onírica.',
            'preco': 'R$ 9,90',
            'hotmart_link': hotmart_links['conto_001']
        },
        {
            'id': '000',
            'titulo': 'O Grande Livro',
            'descricao': 'Filosofia e guerra em um universo paralelo.',
            'preco': 'R$ 9,90',
            'hotmart_link': hotmart_links['conto_000']
        }
    ]
    
    return render_template('doacoes.html', 
                          paypal_link=paypal_link,
                          contos=contos_para_venda)