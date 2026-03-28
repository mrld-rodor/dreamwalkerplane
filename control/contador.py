"""
control/contador.py
=============================================================================
DreamWalker Plane - Contador de Visitas e Scanner de IP
=============================================================================

Este arquivo contém:
1. FUNÇÕES DE CONTADOR (para o site funcionar)
   - inicializar_contador()
   - obter_contadores() 
   - atualizar_contadores()
   - iniciar_pingador()
   
2. FUNÇÕES DE SCANNER DE IP (sua implementação avançada)
   - classificar_ip()
   - obter_localizacao()
   - detectar_os_ttl()
   - fingerprint_os()
   - analisar_ip()
=============================================================================
"""

import threading
import time
import os
import requests
import yaml
import socket
import ipaddress
from datetime import datetime
from scapy.all import IP, ICMP, sr1

# ============================================================================
# PARTE 1: CONTADOR DE VISITAS (NECESSÁRIO PARA O SITE)
# ============================================================================

# Caminho para o arquivo que irá armazenar os dados
contador_file = 'contador.txt'

def inicializar_contador():
    """Inicializa o arquivo de contador se não existir"""
    if not os.path.exists(contador_file):
        with open(contador_file, 'w') as f:
            data = {
                'visitantes': 0,
                'downloads': 0,
                'visitas': []
            }
            yaml.dump(data, f, default_flow_style=False)
            print("[contador] Arquivo inicializado com sucesso!")


def obter_contadores():
    """Retorna (visitantes, downloads, lista_visitas)"""
    if not os.path.exists(contador_file):
        inicializar_contador()

    with open(contador_file, 'r') as f:
        conteudo = f.read()

    data = yaml.safe_load(conteudo)

    if data is None:
        data = {
            'visitantes': 0,
            'downloads': 0,
            'visitas': []
        }

    return data.get('visitantes', 0), data.get('downloads', 0), data.get('visitas', [])


def atualizar_contadores(visitas=0, downloads=0, ip=None):
    """
    Atualiza os contadores e registra uma nova visita
    Agora com análise avançada do IP (usando suas funções)
    """
    visitantes, downloads_atual, visitas_lista = obter_contadores()

    visitantes += visitas
    downloads_atual += downloads

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Usa sua função avançada de análise de IP
    if ip:
        info_ip = analisar_ip(ip)
        local = info_ip['localizacao']
        tipo_ip = info_ip['tipo']
        os_detectado = info_ip['os']
        
        # Cria um registro mais completo da visita
        registro_visita = {
            'data': agora,
            'ip': ip,
            'tipo': tipo_ip,
            'local': local,
            'os': os_detectado
        }
    else:
        registro_visita = {
            'data': agora,
            'ip': 'desconhecido',
            'tipo': 'desconhecido',
            'local': 'Desconhecido',
            'os': 'desconhecido'
        }

    visitas_lista.append(registro_visita)

    # Mantém apenas as últimas 1000 visitas para não crescer demais
    if len(visitas_lista) > 1000:
        visitas_lista = visitas_lista[-1000:]

    with open(contador_file, 'w') as f:
        data = {
            'visitantes': visitantes,
            'downloads': downloads_atual,
            'visitas': visitas_lista
        }
        yaml.dump(data, f, default_flow_style=False)



# ============================================================================
# PARTE 2: SCANNER DE IP (SUA IMPLEMENTAÇÃO AVANÇADA)
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


def obter_localizacao_geografica(ip):
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


def detectar_os_ttl(ip):
    """Detecta sistema operacional baseado no TTL do ICMP"""
    try:
        pkt = IP(dst=ip) / ICMP()
        resposta = sr1(pkt, timeout=2, verbose=0)

        if resposta is None:
            return "Desconhecido"

        ttl = resposta.ttl

        if ttl <= 64:
            return "Linux/Unix"
        elif ttl <= 128:
            return "Windows"
        else:
            return "Network Device"

    except Exception:
        return "Desconhecido"


def pegar_banner(ip, porta):
    """Tenta obter banner de serviço em uma porta"""
    try:
        sock = socket.socket()
        sock.settimeout(2)
        sock.connect((ip, porta))
        banner = sock.recv(1024).decode(errors="ignore").lower()
        sock.close()
        return banner
    except Exception:
        return ""


def detectar_os_banner(banner):
    """Detecta OS a partir do banner do serviço"""
    if "windows" in banner:
        return "Windows"
    elif "linux" in banner or "ubuntu" in banner or "debian" in banner:
        return "Linux"
    elif "unix" in banner:
        return "Unix"
    elif "cisco" in banner:
        return "Cisco"
    elif "openbsd" in banner or "freebsd" in banner:
        return "BSD"
    else:
        return "Desconhecido"


def fingerprint_os(ip):
    """Combina múltiplas técnicas para identificar o OS"""
    portas_comuns = [22, 80, 443, 8080, 3306, 5432]

    # Primeiro tenta banner grabbing nas portas comuns
    for porta in portas_comuns:
        banner = pegar_banner(ip, porta)
        os_detectado = detectar_os_banner(banner)

        if os_detectado != "Desconhecido":
            return os_detectado

    # Fallback: detecção por TTL
    return detectar_os_ttl(ip)


def analisar_ip(ip):
    """
    Análise completa de um IP
    Retorna dicionário com todas as informações
    """
    tipo = classificar_ip(ip)

    if tipo == "Público":
        localizacao = obter_localizacao_geografica(ip)
        os_detectado = fingerprint_os(ip)
    else:
        localizacao = "Rede Local"
        os_detectado = detectar_os_ttl(ip)  # TTL funciona em rede local

    return {
        "ip": ip,
        "tipo": tipo,
        "localizacao": localizacao,
        "os": os_detectado,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
