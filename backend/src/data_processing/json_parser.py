"""
Arquivo destinado a armazenar funções relacionadas à extração e análise de dados 
de arquivos JSON, incluindo a formatação de URLs, a coleta de vulnerabilidades e 
informações associadas, além de manipulação de dados relacionados a relatórios de 
segurança.

Funções presentes:
- Extração de targets e domínios a partir dos arquivos JSON.
- Agrupamento de vulnerabilidades por nome e plugin_id.
- Contagem de vulnerabilidades por tipo de risco (Crítico, Alto, Médio, Baixo).
- Formatação de URIs relativas para URLs absolutas.
"""


##LIBS
from collections import defaultdict
import json
import re
from urllib.parse import urlparse, urljoin
import glob
import os
from typing import List
from pathlib import Path

# Importa as funções de utilidade genéricas e as funções de JSON do módulo core
from ..core.utils import contar_riscos, limpar_protocolos_url
from ..core.json_utils import carregar_json, carregar_json_utf # Importa as funções específicas de carregar JSON


##FUNÇÕES

def localizar_arquivos(diretorio_path: str, formato: str) -> List[str]:
    """
    Função para encontrar todos os arquivos de terminada extensão em um diretório especificado.

    :param diretorio_path: O caminho para o diretório onde os arquivos estão localizados.
    :param formato: A extensão dos arquivos a serem encontrados (ex: 'json', 'txt', 'csv').
    :return: Lista de caminhos completos para os arquivos encontrados.
    """
    # Verifica se o diretório existe
    if not os.path.exists(diretorio_path):
        print(f"O diretório {diretorio_path} não existe.")
        return []
    
    # Encontrar todos os arquivos no diretório
    files = glob.glob(os.path.join(diretorio_path, "*." + formato))
    if not files:
        print(f"Nenhum arquivo com a extensão .{formato} encontrado no diretório {diretorio_path}.")
        return []
    
    # Converter os caminhos para o formato POSIX (com forward slashes)
    files_normalized = [Path(file).as_posix() for file in files]
    return files_normalized

def extrair_targets(json_files: List[str]) -> List[str]:
    """
    Extrai os targets (domínios) a partir dos arquivos JSON, retornando uma lista de targets únicos.

    Parâmetros:
    - json_files (List[str]): Lista com os caminhos dos arquivos JSON.

    Retorna:
    - List[str]: Lista com os targets extraídos dos arquivos JSON, sem duplicatas.
    """
    targets = set()
    for json_file in json_files:
        
        data = carregar_json(json_file)
        target = data.get('scan', {}).get('target', 'Não disponível')
        
        if target != 'Não disponível':
            targets.add(target)
            
    return list(targets)

def obter_vulnerabilidades_comum(json_files: List[str]) -> dict:
    """
    Obtém as vulnerabilidades comuns entre os arquivos JSON, agrupando-as por nome e plugin_id.

    Parâmetros:
    - json_files (List[str]): Lista com os caminhos dos arquivos JSON.

    Retorna:
    - dict: Dicionário com vulnerabilidades agrupadas por (nome, plugin_id) e as URIs afetadas.
    """
    common_vulnerabilities = defaultdict(list)
    for json_file in json_files:
        data = carregar_json(json_file)
        target = data.get('scan', {}).get('target', 'Não disponível')
        
        for finding in data.get('findings', []):
            risk_factor = finding.get('risk_factor', 'Não disponível')
            uri = finding.get('uri', 'Não disponível')
            name = finding.get('name', 'Não disponível')
            plugin_id = finding.get('plugin_id', 'Não disponível')
            if "info" not in risk_factor:
                formatted_uri = formatar_uri(target, uri)
                common_vulnerabilities[(name, plugin_id)].append(formatted_uri)
    return common_vulnerabilities

def extrair_dominio(target: str) -> str:
    """
    A função recebe um endereço URL (target) e retorna o domínio base.
    """
    parsed_url = urlparse(target)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"
    
def formatar_uri(target: str, uri: str) -> str:
    """
    A função recebe o target (uma URL base) e uma URI, e retorna a URL completa.
    """
    target_domain = extrair_dominio(target)
    parsed_uri = urlparse(uri)
    
    if not parsed_uri.netloc:
        return urljoin(target_domain, uri)
    else:
        return target_domain
    
def contar_vulnerabilidades(json_files: List[str]) -> dict:
    """
    Conta o número de vulnerabilidades por tipo (Critical, High, Medium, Low) em arquivos JSON.
    """
    risk_factor_counts = {'High': 0, 'Critical': 0, 'Low': 0, 'Medium': 0}
    for json_file in json_files:
        data = carregar_json(json_file)
        for finding in data.get('findings', []):
            risk_factor = finding.get('risk_factor', 'Não disponível')
            if "info" not in risk_factor:
                if risk_factor.lower() == 'high':
                    risk_factor_counts['High'] += 1
                elif risk_factor.lower() == 'critical':
                    risk_factor_counts['Critical'] += 1
                elif risk_factor.lower() == 'low':
                    risk_factor_counts['Low'] += 1
                elif risk_factor.lower() == 'medium':
                    risk_factor_counts['Medium'] += 1
    return risk_factor_counts

def extrair_dados_vulnerabilidades(data: dict) -> dict:
    """
    Extrai os dados de vulnerabilidade de um arquivo JSON.
    """
    target = data.get('scan', {}).get('target', 'Não disponível')
    if target == 'Não disponível':
        return None

    risk_factor_counts = contar_riscos(data.get('findings', []))
    cleaned_target = limpar_protocolos_url(target)
    total = sum(risk_factor_counts.values())
    
    return {
        'Site': cleaned_target,
        'Critical': risk_factor_counts['Critical'],
        'High': risk_factor_counts['High'],
        'Medium': risk_factor_counts['Medium'],
        'Low': risk_factor_counts['Low'],
        'Total': total
    }

# REMOVIDA: A função montar_conteudo_latex foi movida para report_builder.py.
# REMOVIDA: A função carregar_vulnerabilidades_do_relatorio foi movida para report_builder.py.
# REMOVIDA: A função carregar_descritivo_vulnerabilidades foi movida para report_builder.py (e agora é carregar_descritivo_vulnerabilidades em report_builder).
# REMOVIDA: A função gerar_conteudo_latex_para_vulnerabilidades foi movida para report_builder.py.