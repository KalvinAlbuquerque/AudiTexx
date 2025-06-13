from collections import defaultdict
import json
import os
import re
from typing import List
import pandas as pd
from ..core.json_utils import carregar_json_utf


def obter_vulnerabilidades_comum_csv(csv_files: List[str]) -> dict:
    """
    Obtém as vulnerabilidades comuns entre os arquivos CSV, agrupando-as por Name,
    listando os hosts afetados e a severidade (Risk).
    """
    common_vulnerabilities = defaultdict(lambda: {"hosts": set(), "risks": set()})

    if not csv_files:
        return {}
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, usecols=['Name', 'Host', 'Risk'], encoding='utf-8', on_bad_lines='skip')
            df = df.dropna(subset=['Name', 'Host', 'Risk'])

            for _, row in df.iterrows():
                name = str(row['Name']).strip()
                host = str(row['Host']).strip()
                risk = str(row['Risk']).strip().lower()

                if risk in {'critical', 'high', 'medium', 'low'}:
                    common_vulnerabilities[name]["hosts"].add(host)
                    common_vulnerabilities[name]["risks"].add(risk)
        except pd.errors.EmptyDataError:
            print(f"Aviso: O arquivo CSV '{csv_file}' está vazio ou não possui dados.")
        except Exception as e:
            print(f"Erro ao processar {csv_file}: {e}")

    return {
        name: {
            "hosts": list(data["hosts"]),
            "risks": list(data["risks"])
        }
        for name, data in common_vulnerabilities.items()
    }
    
def contar_vulnerabilidades_csv(vulnerabilidades: dict) -> dict:
    """
    Conta a quantidade total de vulnerabilidades por nível de risco.
    """
    contagem = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for dados in vulnerabilidades.values():
        hosts_afetados = dados["hosts"]
        riscos = dados["risks"]

        if riscos:
            if len(riscos) == 1:
                risco = riscos[0]
                if risco in contagem:
                    contagem[risco] += len(hosts_afetados)
            else:
                print(f"Atenção: Múltiplos níveis de risco encontrados para a vulnerabilidade '{list(vulnerabilidades.keys())[0]}': {riscos}. Contando pelo risco mais alto.")
                
    return contagem

def extrair_hosts_csv(csv_files: List[str]) -> List[str]:
    """
    Extrai os hosts únicos a partir dos arquivos CSV exportados do Tenable.
    """
    hosts = set()

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, usecols=['Host'], encoding='utf-8', on_bad_lines='skip')
            df['Host'] = df['Host'].astype(str).str.strip()

            for host in df['Host'].dropna():
                if host:
                    hosts.add(host)
        except pd.errors.EmptyDataError:
            print(f"Aviso: O arquivo CSV '{csv_file}' está vazio ou não possui dados de hosts.")
        except Exception as e:
            print(f"Erro ao processar {csv_file}: {e}")

    return list(hosts)

