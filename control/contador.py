# control/contador.py


import threading
import time
import os
import requests
import yaml
from datetime import datetime

# Caminho para o arquivo que irá armazenar os dados
contador_file = 'contador.txt'

def inicializar_contador():
    if not os.path.exists(contador_file):
        with open(contador_file, 'w') as f:
            # Inicializa o arquivo com valores padrão
            data = {
                'visitantes': 0,
                'downloads': 0,
                'visitas': []
            }
            yaml.dump(data, f, default_flow_style=False)


def obter_contadores():
    if not os.path.exists(contador_file):
        inicializar_contador()

    with open(contador_file, 'r') as f:
        conteudo = f.read()

    # Carrega os dados do arquivo, que está em formato YAML
    data = yaml.safe_load(conteudo)


    # Garante que 'data' não seja None
    if data is None:
        data = {
            'visitantes': 0,
            'downloads': 0,
            'visitas': []
        }

    # Retorna o número de visitantes, downloads e a lista de visitas
    return data.get('visitantes', 0), data.get('downloads', 0), data.get('visitas', [])


# Função para atualizar os contadores e registrar visitas
def atualizar_contadores(visitas=0, downloads=0, ip=None):
    # Lê os dados atuais
    visitantes, downloads_atual, visitas_lista = obter_contadores()

    # Atualiza os contadores
    visitantes += visitas
    downloads_atual += downloads

    # Obtém a data/hora atual
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Obtém a localização do usuário, se o IP for fornecido
    local = obter_localizacao(ip) if ip else 'Desconhecido'

    # Adiciona a nova visita à lista de visitas
    visitas_lista.append({
        'data': agora, 
        'local': local
    })

    # Escreve os dados atualizados no arquivo
    with open(contador_file, 'w') as f:
        data = {
            'visitantes': visitantes,
            'downloads': downloads_atual,
            'visitas': visitas_lista
        }
        yaml.dump(data, f, default_flow_style=False)  # Usa o formato YAML


# Função para obter a localização do IP
def obter_localizacao(ip):
    try:
        # Faz a requisição para obter os dados de geolocalização
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        dados = response.json()
        
        # Obtém cidade, região e país, se disponíveis
        cidade = dados.get('city', 'Desconhecido')
        regiao = dados.get('region', 'Desconhecido')
        pais = dados.get('country', 'Desconhecido')
        
        # Retorna a string com a localização completa
        return f'{cidade}, {regiao}, {pais}'
    except Exception as e:
        # Caso a requisição falhe, retorna "Desconhecido"
        return 'Desconhecido'
    
# Testando com um IP público específico
print(obter_localizacao('8.8.8.8'))  # Exemplo de IP público do Google



# ========== CONFIG DO AUTO-PING ==========
URL = "http://127.0.0.1:5000"  # Substitua pela URL real do seu site
INTERVALO_MINUTOS = 14

def auto_ping():
    while True:
        try:
            r = requests.get(URL)
            print(f"[{time.ctime()}] Ping enviado! Status: {r.status_code}")
        except Exception as e:
            print(f"[{time.ctime()}] Erro ao pingar: {e}")
        time.sleep(INTERVALO_MINUTOS * 60)

def iniciar_pingador():
    thread = threading.Thread(target=auto_ping, daemon=True)
    thread.start()