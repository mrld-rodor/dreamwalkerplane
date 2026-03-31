from models import db, Contador
"""
control/contador.py
=============================================================================
DreamWalker Plane - Contador de Visitas
=============================================================================

Funcionalidades:
- inicializar_contador(): Cria o arquivo de contador se não existir
- obter_contadores(): Retorna (visitantes, downloads, lista_visitas)
- atualizar_contadores(): Atualiza contadores e registra visita
- analisar_ip(): Analisa IP do visitante (localização, tipo, OS)
=============================================================================
"""

import os
import requests
import yaml
import socket
import ipaddress
from datetime import datetime


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

contador_file = 'contador.txt'


# ============================================================================
# FUNÇÕES DE ANÁLISE DE IP
# ============================================================================

def classificar_ip(ip):
    """Classifica o IP como Loopback, Privado ou Público"""
    try:
        ip_obj = ipaddress.ip_address(ip)

        if ip_obj.is_loopback:
            return "Loopback"
        elif ip_obj.is_private:
            return "Privado"
        else:
            return "Público"

    except ValueError:
        return "Inválido"


def obter_localizacao_por_ip(ip):
    """Obtém localização geográfica via ipinfo.io"""
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)

        if response.status_code != 200:
            return "Desconhecido"

        dados = response.json()

        cidade = dados.get("city") or "Desconhecido"
        regiao = dados.get("region") or "Desconhecido"
        pais = dados.get("country") or "Desconhecido"

        return f"{cidade}, {regiao}, {pais}"

    except Exception:
        return "Desconhecido"


def analisar_ip(ip):
    """
    Análise completa de um IP
    Retorna dicionário com todas as informações
    """
    tipo = classificar_ip(ip)

    if tipo == "Público":
        localizacao = obter_localizacao_por_ip(ip)
    else:
        localizacao = "Rede Local"

    return {
        "ip": ip,
        "tipo": tipo,
        "localizacao": localizacao,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# ============================================================================
# FUNÇÕES DO CONTADOR
# ============================================================================

def obter_contadores():
    try:
        with open('caminho/do/arquivo.yaml', 'r') as file:
            conteudo = file.read()
        data = yaml.safe_load(conteudo)
        # ... resto do código
    except FileNotFoundError:
        # Cria arquivo padrão se não existir
        data = {'visitantes': 0, 'downloads': 0, 'visitas': []}
        with open('caminho/do/arquivo.yaml', 'w') as file:
            yaml.dump(data, file)
        return data


def inicializar_contador():
        # Inicializa no banco, se possível
        try:
            if not Contador.query.get(1):
                c = Contador(id=1, visitantes=0, downloads=0, visitas=[])
                db.session.add(c)
                db.session.commit()
        except Exception:
            pass
        """Inicializa o arquivo de contador se não existir"""
        if not os.path.exists(contador_file):
            data = {'visitantes': 0, 'downloads': 0, 'visitas': []}
            with open(contador_file, 'w') as f:
                yaml.dump(data, f)

def obter_contadores():
    """Retorna (visitantes, downloads, lista_visitas)"""
    # Primeiro tenta banco
    try:
        c = Contador.query.get(1)
        if c:
            d = c.to_dict()
            return d['visitantes'], d['downloads'], d['visitas']
    except Exception:
        pass
    # Fallback: arquivo
    if not os.path.exists(contador_file):
        inicializar_contador()
    with open(contador_file, 'r') as f:
        conteudo = f.read()
    data = yaml.safe_load(conteudo)
    if data is None:
        data = {'visitantes': 0, 'downloads': 0, 'visitas': []}
    return data.get('visitantes', 0), data.get('downloads', 0), data.get('visitas', [])


def atualizar_contadores(visitas=0, downloads=0, ip=None):
    """
    Atualiza os contadores e registra uma nova visita
    """
    visitantes, downloads_atual, visitas_lista = obter_contadores()
    visitantes += visitas
    downloads_atual += downloads
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Análise do IP
    if ip and ip not in ['127.0.0.1', 'localhost']:
        try:
            info_ip = analisar_ip(ip)
            local = info_ip['localizacao']
            tipo_ip = info_ip['tipo']
        except Exception:
            local = "Desconhecido"
            tipo_ip = "Desconhecido"
    else:
        local = "Localhost"
        tipo_ip = "Privado"
    registro_visita = {
        'data': agora,
        'ip': ip if ip else 'desconhecido',
        'tipo': tipo_ip,
        'local': local
    }
    visitas_lista.append(registro_visita)
    if len(visitas_lista) > 500:
        visitas_lista = visitas_lista[-500:]
    # Primeiro tenta banco
    try:
        c = Contador.query.get(1)
        if not c:
            c = Contador(id=1, visitantes=visitantes, downloads=downloads_atual, visitas=visitas_lista)
            db.session.add(c)
        else:
            c.visitantes = visitantes
            c.downloads = downloads_atual
            c.visitas = visitas_lista
        db.session.commit()
        return
    except Exception:
        pass
    # Fallback: arquivo
    with open(contador_file, 'w') as f:
        data = {
            'visitantes': visitantes,
            'downloads': downloads_atual,
            'visitas': visitas_lista
        }
        yaml.dump(data, f, default_flow_style=False)


# # ============================================================================
# # TESTE (executado apenas se rodar este arquivo diretamente)
# # ============================================================================

# if __name__ == '__main__':
#     """Teste das funcionalidades"""
#     print("\n" + "="*60)
#     print("   DREAMWALKER PLANE - TESTE DO CONTADOR")
#     print("="*60 + "\n")
    
#     # Testa inicialização
#     print("[1] Testando inicialização...")
#     inicializar_contador()
    
#     # Testa atualização com IP público
#     print("[2] Testando atualização de contador...")
#     atualizar_contadores(visitas=1, downloads=0, ip='8.8.8.8')
    
#     # Testa leitura
#     print("[3] Testando leitura dos contadores...")
#     visitantes, downloads, visitas = obter_contadores()
    
#     print(f"    Visitantes totais: {visitantes}")
#     print(f"    Downloads totais: {downloads}")
#     print(f"    Últimas 3 visitas:")
#     for v in visitas[-3:]:
#         print(f"        - {v['data']} | {v['ip']} | {v['local']}")
    
#     print("\n[+] Teste concluído com sucesso!")