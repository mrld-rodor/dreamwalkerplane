"""
control/contador.py
=============================================================================
DreamWalker Plane - Contador de Visitas
=============================================================================

Funcionalidades:
- inicializar_contador(): Cria o contador no banco se não existir
- obter_contadores(): Retorna (visitantes, downloads, lista_visitas)
- atualizar_contadores(): Atualiza contadores e registra visita
- analisar_ip(): Analisa IP do visitante (localização, tipo, OS)
=============================================================================
"""

import requests
import ipaddress
from datetime import datetime
from models import db, Contador


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
# FUNÇÕES DO CONTADOR (USANDO BANCO DE DADOS)
# ============================================================================

def inicializar_contador():
    """Inicializa o contador no banco de dados se não existir"""
    try:
        # Verifica se o contador já existe
        if not Contador.query.get(1):
            c = Contador(id=1, visitantes=0, downloads=0, visitas=[])
            db.session.add(c)
            db.session.commit()
            print("[INFO] Contador inicializado no banco de dados")
    except Exception as e:
        print(f"[WARN] Não foi possível inicializar contador no banco: {e}")


def obter_contadores():
    """
    Retorna (visitantes, downloads, lista_visitas)
    """
    try:
        c = Contador.query.get(1)
        if c:
            d = c.to_dict()
            return d['visitantes'], d['downloads'], d['visitas']
    except Exception as e:
        print(f"[WARN] Erro ao obter contadores do banco: {e}")
    
    # Fallback: valores padrão
    return 0, 0, []


def atualizar_contadores(visitas=0, downloads=0, ip=None):
    """
    Atualiza os contadores e registra uma nova visita
    """
    try:
        # Obtém valores atuais
        visitantes_atual, downloads_atual, visitas_lista = obter_contadores()
        
        visitantes_novo = visitantes_atual + visitas
        downloads_novo = downloads_atual + downloads
        
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
        
        # Registro da visita
        registro_visita = {
            'data': agora,
            'ip': ip if ip else 'desconhecido',
            'tipo': tipo_ip,
            'local': local
        }
        
        visitas_lista.append(registro_visita)
        
        # Mantém apenas as últimas 500 visitas
        if len(visitas_lista) > 500:
            visitas_lista = visitas_lista[-500:]
        
        # Salva no banco
        c = Contador.query.get(1)
        if not c:
            c = Contador(id=1, visitantes=visitantes_novo, downloads=downloads_novo, visitas=visitas_lista)
            db.session.add(c)
        else:
            c.visitantes = visitantes_novo
            c.downloads = downloads_novo
            c.visitas = visitas_lista
        
        db.session.commit()
        
    except Exception as e:
        print(f"[WARN] Erro ao atualizar contadores no banco: {e}")
        db.session.rollback()