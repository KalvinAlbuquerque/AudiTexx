from collections import defaultdict
import os
import pandas as pd
import re # Adicionado: Importar regex
import unicodedata # Adicionado: Importar unicodedata

from .json_utils import _load_data # Modificado: Importa _load_data do json_utils.py

def formatar_uri(target: str, uri: str) -> str:
    """
    Formata a URI com o domínio do alvo e a URI específica.
    """
    return f"{target}{uri}"

def limpar_protocolos_url(target: str) -> str:
    """
    Limpa o nome do site para remover 'http://', 'https://' e outros elementos.
    """
    return target.replace('http://', '').replace('https://', '').split('.saude')[0]

def contar_riscos(findings: list) -> dict:
    """
    Conta a quantidade de vulnerabilidades para cada nível de risco.
    """
    risk_factor_counts = {'High': 0, 'Critical': 0, 'Low': 0, 'Medium': 0}

    for finding in findings:
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

def verificar_e_salvar_vulnerabilidades_ausentes(
    vulnerabilidades_identificadas: dict,
    caminho_json_descricoes: str,
    caminho_diretorio_txt: str,
    nome_arquivo_txt: str
) -> tuple[bool, str, list[str]]:
    """
    Verifica quais vulnerabilidades identificadas não possuem descrição no JSON
    de descrições e salva as ausentes em um arquivo TXT.
    """
    vulnerabilidades_json_data = _load_data(caminho_json_descricoes) # Usando _load_data

    # Acessa a lista de vulnerabilidades dentro do dicionário retornado por _load_data
    if isinstance(vulnerabilidades_json_data, dict) and "vulnerabilidades" in vulnerabilidades_json_data:
        vulnerabilidades_json = vulnerabilidades_json_data["vulnerabilidades"]
    elif isinstance(vulnerabilidades_json_data, list):
        # Isso pode acontecer se o arquivo json_descricoes for apenas uma lista diretamente
        vulnerabilidades_json = vulnerabilidades_json_data
    else:
        print(f"Aviso: Conteúdo inesperado em '{caminho_json_descricoes}'. Esperado um dicionário com 'vulnerabilidades' ou uma lista.")
        vulnerabilidades_json = []

    vulnerabilidades_nomes_json = {
        vuln.get('Vulnerabilidade') for vuln in vulnerabilidades_json if vuln.get('Vulnerabilidade')
    }

    vulnerabilidades_nao_encontradas = []

    for chave_vuln_identificada in vulnerabilidades_identificadas.keys():
        vuln_nome = ""
        if isinstance(chave_vuln_identificada, tuple) and len(chave_vuln_identificada) >= 1:
            vuln_nome = chave_vuln_identificada[0]
        elif isinstance(chave_vuln_identificada, str):
            vuln_nome = chave_vuln_identificada
        else:
            print(f"Aviso: Tipo de chave inesperado encontrado: {type(chave_vuln_identificada)}. Pulando.")
            continue

        if vuln_nome and vuln_nome not in vulnerabilidades_nomes_json:
            if vuln_nome not in vulnerabilidades_nao_encontradas:
                vulnerabilidades_nao_encontradas.append(vuln_nome)

    if not vulnerabilidades_nao_encontradas:
        return True, "Todas as vulnerabilidades identificadas foram encontradas no JSON de descrições.", []

    try:
        os.makedirs(caminho_diretorio_txt, exist_ok=True)
    except OSError as e:
        return False, f"Erro ao criar o diretório '{caminho_diretorio_txt}': {e}", vulnerabilidades_nao_encontradas

    caminho_completo_txt = os.path.join(caminho_diretorio_txt, nome_arquivo_txt)

    try:
        with open(caminho_completo_txt, 'w', encoding='utf-8') as f:
            for vuln_nome in vulnerabilidades_nao_encontradas:
                f.write(vuln_nome + '\n')
        return True, f"Vulnerabilidades não encontradas salvas em: {caminho_completo_txt}", vulnerabilidades_nao_encontradas
    except IOError as e:
        return False, f"Erro de I/O ao salvar o arquivo TXT: {e}", vulnerabilidades_nao_encontradas
    except Exception as e:
        return False, f"Erro inesperado ao salvar TXT: {e}", vulnerabilidades_nao_encontradas

def extrair_nomes_vulnerabilidades_identificadas(vulnerabilidades_agrupadas: defaultdict) -> list[str]:
    """
    Extrai uma lista única de nomes de vulnerabilidades a partir do defaultdict.
    """
    nomes_unicos = set()
    for (vuln_nome, vuln_id) in vulnerabilidades_agrupadas.keys():
        nomes_unicos.add(vuln_nome)
    return list(nomes_unicos)

# NOVO: Função de sanitização robusta para strings
def sanitize_string(text: str, remove_accents: bool = False, to_title_case: bool = False) -> str:
    """
    Sanitiza uma string para uso em dados de vulnerabilidade.
    Remove espaços extras, normaliza espaços internos, e opcionalmente
    remove acentos e converte para título.
    """
    if not isinstance(text, str):
        return ""

    text = text.strip()
    text = re.sub(r'\s+', ' ', text)

    if remove_accents:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

    if to_title_case:
        text = text.title()

    return text