import json
import re
import os
import shutil
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime, date
from babel.dates import format_date
import unicodedata # Adicionado para transliteração de nomes de arquivo de imagem

# Importa as funções de utilidade e JSON do core
from ..core.json_utils import carregar_json_utf, _load_data_
from ..core.config import Config

# Inicializa a configuração
config = Config("config.json")

# =======================================================================
# FUNÇÕES DE CARREGAMENTO DE VULNERABILIDADES DE ARQUIVOS TXT DE RELATÓRIO
# Essas funções foram movidas para cá de json_parser.py e csv_parser.py
# =======================================================================
def carregar_vulnerabilidades_do_relatorio(caminho_arquivo: str) -> List[Dict[str, Any]]:
    """
    Carrega e extrai informações de vulnerabilidades a partir de um arquivo TXT de relatório de Web App.

    Parâmetros:
    - caminho_arquivo (str): O caminho completo do arquivo TXT contendo as vulnerabilidades.

    Retorno:
    - list: Uma lista de dicionários, onde cada dicionário contém os dados de uma vulnerabilidade.
    """
    vulnerabilities = []
    with open(caminho_arquivo, 'r', encoding="utf-8") as file:
        vulnerability = None
        total_affected_uris = None
        affected_uris = []
        for line in file:
            line = line.strip()
            match_vulnerability = re.match(r"^Vulnerabilidade:(.*)", line)
            if match_vulnerability:
                if vulnerability:
                    vulnerabilities.append({
                        "Vulnerabilidade": vulnerability,
                        "Total de URI Afetadas": total_affected_uris,
                        "URI Afetadas": affected_uris
                    })
                vulnerability = match_vulnerability.group(1).strip()
                affected_uris = []
                continue
            match_total_uris = re.match(r"^Total de URI Afetadas:(\d+)", line)
            if match_total_uris:
                total_affected_uris = int(match_total_uris.group(1))
                continue
            match_uris = re.match(r"^http(s)?://.*", line)
            if match_uris:
                affected_uris.append(line)
        if vulnerability:
            vulnerabilities.append({
                "Vulnerabilidade": vulnerability,
                "Severidade": "unknown", # Valor padrão para 'severity' para webapp, já que não é extraído do TXT
                "Total de URI Afetadas": total_affected_uris,
                "URI Afetadas": affected_uris
            })
    return vulnerabilities

def carregar_vulnerabilidades_do_relatorio_csv(caminho_arquivo: str) -> List[Dict[str, Any]]:
    """
    Carrega e extrai informações de vulnerabilidades e hosts afetados a partir de um arquivo TXT de relatório de Servidores.

    Parâmetros:
    - caminho_arquivo (str): O caminho completo do arquivo TXT contendo as vulnerabilidades.

    Retorno:
    - list: Uma lista de dicionários com dados de cada vulnerabilidade.
    """
    vulnerabilities = []
    with open(caminho_arquivo, 'r', encoding="utf-8") as file:
        vulnerability = None
        severity = None
        collecting_hosts = False
        affected_hosts = []
        for line in file:
            line = line.strip()
            match_vuln = re.match(r'^Vulnerabilidade:\s*(.+)', line)
            if match_vuln:
                if vulnerability:
                    vulnerabilities.append({
                        "Vulnerabilidade": vulnerability,
                        "Severidade": severity,
                        "Total de Hosts Afetados": len(affected_hosts),
                        "Hosts": affected_hosts
                    })
                vulnerability = match_vuln.group(1).strip()
                severity = None
                affected_hosts = []
                collecting_hosts = False
                continue
            match_sev = re.match(r'^Severidade:\s*(.+)', line)
            if match_sev:
                severity = match_sev.group(1).strip().lower()
                collecting_hosts = False
                continue
            if line.startswith("Hosts Afetados:"):
                collecting_hosts = True
                continue
            if collecting_hosts and line and not line.startswith("Vulnerabilidade:"):
                affected_hosts.append(line.strip())
        if vulnerability:
            vulnerabilities.append({
                "Vulnerabilidade": vulnerability,
                "Severidade": severity,
                "Total de Hosts Afetados": len(affected_hosts),
                "Hosts": affected_hosts
            })
    return vulnerabilities
# =======================================================================


def gerar_relatorio_txt(output_file: str, risk_factor_counts: dict, common_vulnerabilities: dict, targets: List[str]):
    """
    Gera um relatório de texto com as vulnerabilidades de web apps e as informações coletadas.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as output:
            output.write("Resumo das Vulnerabilidades por Risk Factor (Web Apps):\n\n")
            output.write(f"Critical: {risk_factor_counts['Critical']}\n")
            output.write(f"High: {risk_factor_counts['High']}\n")
            output.write(f"Medium: {risk_factor_counts['Medium']}\n")
            output.write(f"Low: {risk_factor_counts['Low']}\n")
            total = sum(risk_factor_counts.values())
            output.write(f"Total de Vulnerabilidades: {total}\n\n")
            output.write("\nDomínios analisados:\n")
            output.write(f"\nTotal de sites: {len(targets)}\n")
            output.write("\n".join(targets))
            output.write("\n\nVulnerabilidades em comum, entre os sites/URI:\n\n")
            sorted_vulnerabilities = sorted(common_vulnerabilities.items(), key=lambda x: len(set(x[1])), reverse=True)
            for (name, plugin_id), uris in sorted_vulnerabilities:
                unique_uris = sorted(list(set(uris)))
                output.write(f"\nVulnerabilidade: {name}\n")
                # REMOVIDO: output.write(f"Plugin ID: {plugin_id}\n")
                output.write(f"Total de URI Afetadas: {len(unique_uris)}\n") # CORRIGIDO: Sempre escreve o total
                output.write(f"URI Afetadas:\n")
                if unique_uris: # Escreve as URIs se houver
                    for url in unique_uris:
                        output.write(f"{url}\n")
                else: # Se não houver URIs, ainda indica
                    output.write("Nenhuma URI afetada.\n") # Ou deixe em branco se preferir
        print(f"Relatório TXT para Web Apps gerado em: {output_file}")
    except Exception as e:
        print(f"Erro ao gerar relatório TXT para Web Apps: {e}")
                    
def gerar_relatorio_txt_csv(output_file: str, risk_factor_counts: dict, common_vulnerabilities: dict, targets: List[str]):
    """
    Gera um relatório de texto com as vulnerabilidades de servidores e as informações coletadas.
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as output:
            output.write("Resumo das Vulnerabilidades por Risk Factor (Servidores):\n\n")
            output.write(f"Critical: {risk_factor_counts.get('critical', 0)}\n")
            output.write(f"High: {risk_factor_counts.get('high', 0)}\n")
            output.write(f"Medium: {risk_factor_counts.get('medium', 0)}\n")
            output.write(f"Low: {risk_factor_counts.get('low', 0)}\n")
            total = sum(risk_factor_counts.values())
            output.write(f"\nTotal de Vulnerabilidades: {total}\n\n")
            output.write("Hosts analisados:\n")
            output.write(f"Total de Hosts: {len(targets)}\n")
            output.write("\n".join(targets))
            output.write("\n\nVulnerabilidades em comum entre os Hosts:\n\n")
            sorted_vulnerabilities = sorted(
                common_vulnerabilities.items(),
                key=lambda item: len(item[1]['hosts']),
                reverse=True
            )
            for name, data in sorted_vulnerabilities:
                hosts_afetados = sorted(data['hosts'])
                riscos = sorted(data['risks'])
                output.write(f"\nVulnerabilidade: {name}\n")
                output.write(f"Severidade: {', '.join(riscos).capitalize()}\n")
                output.write(f"Total de Hosts Afetados: {len(hosts_afetados)}\n")
                output.write("Hosts Afetados:\n")
                for host in hosts_afetados:
                    output.write(f"{host}\n")
        print(f"Relatório TXT para Servidores gerado em: {output_file}")
    except Exception as e:
        print(f"Erro ao gerar relatório TXT para Servidores: {e}")

def carregar_descritivo_vulnerabilidades(caminho_arquivo: str) -> List[Dict[str, Any]]:
    """
    Carrega e organiza as informações de categorias e subcategorias de vulnerabilidades
    a partir de um arquivo JSON descritivo.
    """
    descritivo = []
    dados = _load_data_(caminho_arquivo)
    for categoria in dados.get("vulnerabilidades", []):
        categoria_nome = categoria["categoria"]
        categoria_descricao = categoria["descricao"]
        descritivo.append({
            "categoria": categoria_nome,
            "descricao": categoria_descricao
        })
        for subcategoria in categoria.get("subcategorias", []):
            descritivo.append({
                "categoria": categoria_nome,
                "subcategoria": subcategoria["subcategoria"],
                "descricao": subcategoria["descricao"]
            })
    return descritivo

def escape_path_for_latex(path_str: str) -> str:
    """
    Escapa uma string de caminho de arquivo para inclusão segura em comandos \includegraphics do LaTeX.
    - Converte barras invertidas para barras normais.
    - Translitera caracteres acentuados para ASCII.
    - Substitui espaços por hífens.
    - Escapa caracteres LaTeX problemáticos em nomes de arquivo/caminhos.
    - Garante uma extensão de imagem válida e trata pontos dentro da parte do nome do arquivo.
    """
    if not isinstance(path_str, str):
        return path_str

    # Normaliza os separadores de caminho (Windows para Unix-like)
    path_str = path_str.replace('\\', '/')

    # Divide o caminho em diretório e nome base do arquivo
    dir_name, base_name = os.path.split(path_str)

    # 1. Limpa possíveis hífens ou caracteres malformados que antecedem a extensão
    # Ex: 'image.png-' -> 'image.png'
    base_name = re.sub(r'-(?=\.(png|jpg|jpeg|gif|pdf)$)', '', base_name, flags=re.IGNORECASE)
    base_name = base_name.rstrip('-') # Remove outros hífens no final

    # 2. Translitera caracteres acentuados para ASCII (ex: 'Configurações' -> 'Configuracoes')
    base_name = unicodedata.normalize('NFKD', base_name).encode('ascii', 'ignore').decode('utf-8')

    # 3. Substitui espaços por hífens
    base_name = base_name.replace(' ', '-')

    # 4. Garante uma extensão de arquivo apropriada e lida com pontos dentro do nome do arquivo
    filename_stem, ext = os.path.splitext(base_name)
    valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.pdf']

    if ext and ext.lower() in valid_extensions:
        # Se uma extensão válida for encontrada, mantém-na
        final_ext = ext.lower()
        # Substitui quaisquer outros pontos no 'filename_stem' por hífens
        filename_stem = filename_stem.replace('.', '-')
    else:
        # Se nenhuma extensão válida for encontrada, ou for uma "extensão falsa" como ".0-pollution",
        # substitui todos os pontos no 'base_name' original por hífens e adiciona .png
        filename_stem = base_name.replace('.', '-')
        final_ext = ".png"

    # Reconstrói o nome base do arquivo limpo
    base_name_cleaned = filename_stem + final_ext

    # 5. Escapa caracteres especiais do LaTeX no caminho completo (incluindo o diretório)
    # Reúne o diretório e o nome base limpo para o caminho completo antes do escape final
    full_path_cleaned = os.path.join(dir_name, base_name_cleaned).replace('\\', '/')

    # Escapa caracteres especiais do LaTeX
    full_path_escaped = full_path_cleaned.replace('_', '\\_')
    full_path_escaped = full_path_escaped.replace('%', '\\%')
    full_path_escaped = full_path_escaped.replace('$', '\\$')
    full_path_escaped = full_path_escaped.replace('&', '\\&')
    full_path_escaped = full_path_escaped.replace('~', '\\textasciitilde{}')
    full_path_escaped = full_path_escaped.replace('^', '\\textasciicircum{}')
    full_path_escaped = full_path_escaped.replace('{', '\\{')
    full_path_escaped = full_path_escaped.replace('}', '\\}')

    return full_path_escaped

def gerar_conteudo_latex_para_vulnerabilidades(
    vulnerabilidades_do_relatorio_txt: List[Dict[str, Any]],
    vulnerabilidades_detalhes_json: List[Dict[str, Any]],
    descritivo_vulnerabilidades_json: Dict[str, Any],
    tipo_vulnerabilidade: str
) -> str:
    conteudo = ""
    anexo_conteudo = ""
    categorias_agrupadas: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    categorias_formatadas: Dict[str, str] = {}
    vulnerabilidades_sem_categoria: List[str] = []

    # Certifique-se de que descritivo_list é uma lista de categorias, não um dicionário aninhado
    # _load_data_ já deve retornar o dicionário completo que contém a chave "vulnerabilidades"
    # então você precisa pegar a lista de categorias que está dentro dela.
    descritivo_data = descritivo_vulnerabilidades_json # descritivo_vulnerabilidades_json já é o dicionário completo.
    descritivo_list = descritivo_data.get("vulnerabilidades", []) # Correção para acessar a lista real.


    for v in vulnerabilidades_do_relatorio_txt:
        vulnerabilidade_nome = v["Vulnerabilidade"]
        dados_vuln = next(
            (vuln for vuln in vulnerabilidades_detalhes_json if vuln.get("Vulnerabilidade") == vulnerabilidade_nome),
            None
        )
        if dados_vuln:
            categoria_original = dados_vuln.get("Categoria", "Sem Categoria")
            subcategoria_original = dados_vuln.get("Subcategoria", "Outras")
            descricao = dados_vuln.get("Descrição", "Descrição não disponível.")
            solucao = dados_vuln.get("Solução", "Solução não disponível.")
            imagem = dados_vuln.get("Imagem", "")
            categoria_pad = categoria_original
            subcategoria_pad = subcategoria_original
            categorias_formatadas[categoria_pad] = categoria_original
            categorias_formatadas[subcategoria_pad] = subcategoria_original
            if categoria_pad not in categorias_agrupadas:
                categorias_agrupadas[categoria_pad] = {}
            if subcategoria_pad not in categorias_agrupadas[categoria_pad]:
                categorias_agrupadas[categoria_pad][subcategoria_pad] = []
            item_para_agrupar = {
                "Vulnerabilidade": vulnerabilidade_nome,
                "Descricao": descricao,
                "Solucao": solucao,
                "Imagem": imagem,
            }
            if tipo_vulnerabilidade == "webapp":
                item_para_agrupar["Total de URIs Afetadas"] = v.get("Total de URIs Afetadas", 0)
                item_para_agrupar["URIs Afetadas"] = v.get("URI Afetadas", [])
            else:
                item_para_agrupar["Total de Hosts Afetados"] = v.get("Total de Hosts Afetados", 0)
                item_para_agrupar["Hosts Afetados"] = v.get("Hosts", [])
            categorias_agrupadas[categoria_pad][subcategoria_pad].append(item_para_agrupar)
        else:
            vulnerabilidades_sem_categoria.append(vulnerabilidade_nome)

    categorias_ordenadas = sorted(categorias_agrupadas.keys(), key=lambda x: categorias_formatadas.get(x, x))
    outras_criticas_key = "Outras Vulnerabilidades Críticas e Explorações"
    if outras_criticas_key in categorias_ordenadas:
        categorias_ordenadas.remove(outras_criticas_key)
        categorias_ordenadas.append(outras_criticas_key)

    for categoria_padronizada in categorias_ordenadas:
        categoria_formatada = categorias_formatadas.get(categoria_padronizada, categoria_padronizada)
        # Primeiro, encontre a descrição da categoria principal
        descricao_categoria = next(
            (item["descricao"] for item in descritivo_list
             if item.get("categoria") == categoria_padronizada and "subcategoria" not in item),
            "Descrição não disponível."
        )
        conteudo += f"%-------------- INÍCIO DA CATEGORIA {categoria_formatada} --------------\n"
        conteudo += f"\\subsection{{{categoria_formatada}}}\n{escape_latex(descricao_categoria)}\n\n"

        subcategorias = categorias_agrupadas.get(categoria_padronizada, {})
        for subcategoria_padronizada in sorted(subcategorias.keys(), key=lambda x: categorias_formatadas.get(x, x)):
            subcategoria_formatada = categorias_formatadas.get(subcategoria_padronizada, subcategoria_padronizada)

            descricao_subcategoria = "Descrição não disponível."
            target_categoria_padded = categoria_formatada
            target_subcategoria_padded = subcategoria_formatada

            found_match_in_descritivo = False

            # Itere através das subcategorias da categoria principal no descritivo original
            # para encontrar a descrição correta da subcategoria.
            # Você precisa acessar a lista de subcategorias dentro da categoria correspondente.
            categoria_do_descritivo = next(
                (item for item in descritivo_list if item.get("categoria") == categoria_padronizada),
                None
            )

            if categoria_do_descritivo and "subcategorias" in categoria_do_descritivo:
                for item_sub_desc in categoria_do_descritivo["subcategorias"]:
                    item_desc_subcategoria_name = item_sub_desc.get("subcategoria")

                    # ADD THESE PRINT STATEMENTS for debugging
                    print(f"Comparing SUB: target_cat='{target_categoria_padded}' (found in descritivo_list)")
                    print(f"Comparing SUB: target_sub='{target_subcategoria_padded}' vs item_desc_sub_name='{item_desc_subcategoria_name}'")
                    print(f"Types SUB: target_sub={type(target_subcategoria_padded)}, item_desc_sub_name={type(item_desc_subcategoria_name)}")


                    if item_desc_subcategoria_name == target_subcategoria_padded:
                        descricao_subcategoria = item_sub_desc["descricao"]
                        found_match_in_descritivo = True
                        break

            if not found_match_in_descritivo:
                print(f"WARNING: No description found for category '{target_categoria_padded}' and subcategory '{target_subcategoria_padded}'")


            conteudo += f"%-------------- INÍCIO DA SUBCATEGORIA {subcategoria_formatada} --------------\n"
            conteudo += f"\\subsubsection{{{subcategoria_formatada}}}\n{escape_latex(descricao_subcategoria)}\n\n"
            conteudo += "\\begin{enumerate}\n"

            vulns_ordenadas = sorted(subcategorias[subcategoria_padronizada], key=lambda x: x['Vulnerabilidade'])
            for v in vulns_ordenadas:
                conteudo += f"%-------------- INÍCIO DA VULNERABILIDADE {v['Vulnerabilidade']} --------------\n"
                conteudo += f"\\item \\textbf{{\\texttt{{{escape_latex(v['Vulnerabilidade'])}}}}}\n"
                if v["Imagem"]:
                    caminho_imagem_latex = escape_path_for_latex(v["Imagem"])
                    conteudo += (
                        r"""
                        \begin{figure}[h!]
                        \centering
                        \includegraphics[width=0.8\textwidth]{""" + caminho_imagem_latex + r"""}
                        \end{figure}
                        \FloatBarrier
                        """
                    )
                conteudo += f"\\textbf{{Descrição:}} {escape_latex(v['Descricao'])}\n\n"
                conteudo += f"\\textbf{{Solução:}} {escape_latex(v['Solucao'])}\n\n"

                if tipo_vulnerabilidade == "webapp":
                    conteudo += f"\\textbf{{Total de URIs Afetadas:}} {v.get('Total de URIs Afetadas', 0)}\n\n"
                    instancias_afetadas = v.get("URIs Afetadas", [])
                    label_instancias = "URIs Afetadas"
                else:
                    conteudo += f"\\textbf{{Total de Hosts Afetados:}} {v.get('Total de Hosts Afetados', 0)}\n\n"
                    instancias_afetadas = v.get("Hosts Afetados", [])
                    label_instancias = "Hosts Afetados"

                if len(instancias_afetadas) > 10:
                    conteudo += f"\\textbf{{{label_instancias} (parcial):}}\n\\begin{{itemize}}\n"
                    for instancia in instancias_afetadas[:10]:
                        conteudo += f"    \\item \\url{{{instancia}}}\n"
                    conteudo += "\\end{itemize}\n"
                    conteudo += (
                        "A lista completa das instâncias que possuem esta vulnerabilidade pode ser "
                        f"encontrada no \\hyperref[anexoA]{{Anexo A}}.\\\\[0.5em]\n\n"
                    )

                    conteudo_anexo_vuln_nome = escape_latex(v['Vulnerabilidade'])
                    anexo_conteudo += f"%-------------- INÍCIO DO ANEXO PARA {conteudo_anexo_vuln_nome} --------------\n"
                    anexo_conteudo += f"\\subsubsection*{{{conteudo_anexo_vuln_nome} }}\n"
                    anexo_conteudo += "\\begin{multicols}{3}\n\\small\n\\begin{itemize}\n"
                    for instancia in instancias_afetadas:
                        anexo_conteudo += f"    \\item \\url{{{instancia}}}\n"
                    anexo_conteudo += "\\end{itemize}\n\\end{multicols}\n\n"
                else:
                    conteudo += f"\\textbf{{{label_instancias}:}}\n\\begin{{itemize}}\n"
                    for instancia in instancias_afetadas:
                        conteudo += f"    \\item \\url{{{instancia}}}\n"
                    conteudo += "\\end{itemize}\n\n"
                conteudo += f"%-------------- FIM DA VULNERABILIDADE {v['Vulnerabilidade']} --------------\n"

            conteudo += "\\end{enumerate}\n"
            conteudo += f"%-------------- FIM DA SUBCATEGORIA {subcategoria_formatada} --------------\n"

        conteudo += f"%-------------- FIM DA CATEGORIA {categoria_formatada} --------------\n"

    if anexo_conteudo:
        conteudo += "%-------------- INÍCIO DO ANEXO A --------------\n"
        conteudo += "\\section*{Anexo A}\n\\label{anexoA}\n"
        conteudo += anexo_conteudo
        conteudo += "%-------------- FIM DO ANEXO A --------------\n"

    return conteudo


def escape_latex(text: str) -> str:
    """
    Escapes special LaTeX characters in a string.
    """
    text = text.replace('&', '\\&')
    text = text.replace('%', '\\%')
    text = text.replace('$', '\\$')
    text = text.replace('#', '\\#')
    text = text.replace('_', '\\_')
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')
    text = text.replace('~', '\\textasciitilde{}')
    text = text.replace('^', '\\textasciicircum{}')
    # REMOVA A LINHA ABAIXO:
    # text = text.replace('\\', '\\textbackslash{}')
    return text


def montar_conteudo_latex(
    caminho_saida_latex_temp: str,
    caminho_relatorio_txt_webapp: str,
    caminho_dados_vulnerabilidades_webapp_json: str, # Este será o caminho para o JSON ORIGINAL
    caminho_descritivo_webapp_json: str # Este será o caminho para o JSON ORIGINAL
):
    """
    Monta o conteúdo LaTeX para o relatório de vulnerabilidades de Web Apps.
    """
    try:
        vulnerabilidades_do_txt = carregar_vulnerabilidades_do_relatorio(caminho_relatorio_txt_webapp)
        # Carrega o JSON LIMPO (SEM O _cleaned.json, pois o usuário manteve o mesmo nome)
        vulnerabilidades_dados_json = carregar_json_utf(caminho_dados_vulnerabilidades_webapp_json)
        # Carrega o JSON LIMPO (SEM O _cleaned.json, pois o usuário manteve o mesmo nome)
        descritivo_json = carregar_json_utf(caminho_descritivo_webapp_json)

        conteudo_latex_final = gerar_conteudo_latex_para_vulnerabilidades(
            vulnerabilidades_do_txt,
            vulnerabilidades_dados_json,
            descritivo_json,
            "webapp"
        )

        with open(caminho_saida_latex_temp, 'w', encoding='utf-8') as file:
            file.write(conteudo_latex_final)
        print(f"Conteúdo LaTeX para Web Apps gerado em: {caminho_saida_latex_temp}")
    except Exception as e:
        print(f"Erro ao montar conteúdo LaTeX para Web Apps: {e}")

def montar_conteudo_latex_csv(
    caminho_saida_latex_temp: str,
    caminho_relatorio_txt_servers: str,
    caminho_dados_vulnerabilidades_servers_json: str, # Este será o caminho para o JSON ORIGINAL
    caminho_descritivo_servers_json: str # Este será o caminho para o JSON ORIGINAL
):
    """
    Monta o conteúdo LaTeX para o relatório de vulnerabilidades de Servidores (CSV).
    """
    try:
        vulnerabilidades_do_txt_csv = carregar_vulnerabilidades_do_relatorio_csv(caminho_relatorio_txt_servers)
        
        vulnerabilidades_dados_json = carregar_json_utf(caminho_dados_vulnerabilidades_servers_json)
        
        descritivo_json = carregar_json_utf(caminho_descritivo_servers_json)

        conteudo_latex_final = gerar_conteudo_latex_para_vulnerabilidades(
            vulnerabilidades_do_txt_csv,
            vulnerabilidades_dados_json,
            descritivo_json,
            "servers"
        )

        with open(caminho_saida_latex_temp, 'w', encoding='utf-8') as file:
            file.write(conteudo_latex_final)
        print(f"Conteúdo LaTeX para Servidores gerado em: {caminho_saida_latex_temp}")
    except Exception as e:
        print(f"Erro ao montar conteúdo LaTeX para Servidores: {e}")


def copiar_relatorio_exemplo(caminho_relatorio_exemplo: str, caminho_saida: str):
    """
    Copia a estrutura base do template LaTeX para a pasta de geração do relatório.
    """
    try:
        src = Path(caminho_relatorio_exemplo)
        dst = Path(caminho_saida)
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"Estrutura base do relatório copiada de '{src}' para '{dst}'")

        # --- NOVO: Verificação explícita do arquivo preambulo.tex após a cópia ---
        copied_preambulo_path = dst / "preambulo.tex"
        if copied_preambulo_path.exists():
            print(f"DEBUG: 'preambulo.tex' foi copiado com sucesso para: {copied_preambulo_path}")
        else:
            print(f"ERRO: 'preambulo.tex' NÃO foi encontrado em: {copied_preambulo_path} APÓS a cópia.")
        # --- FIM NOVO ---

    except Exception as e:
        print(f"Erro ao copiar a estrutura de exemplo do relatório: {e}")


def substituir_placeholders(conteudo: str, substituicoes_globais: Dict[str, str]) -> str:
    """
    Substitui placeholders [CHAVE] no conteúdo LaTeX por valores fornecidos.
    """
    for alvo, novo in substituicoes_globais.items():
        conteudo = conteudo.replace(f'[{alvo}]', novo)
    return conteudo

def terminar_relatorio_preprocessado(
    nome_secretaria: str,
    sigla_secretaria: str,
    inicio_data: str,
    fim_data: str,
    ano_conclusao: str,
    mes_conclusao: str,
    caminho_relatorio_preprocessado: str,
    caminho_saida_relatorio_final_latex: str,
    google_drive_link: str,
    total_vulnerabilidades_web: str,
    total_vulnerabilidade_vm: str,
    total_vulnerabilidades_criticas_web: str,
    total_vulnerabilidades_alta_web: str,
    total_vulnerabilidades_media_web: str,
    total_vulnerabilidades_baixa_web: str,
    total_vulnerabilidades_criticas_servidores: str,
    total_vulnerabilidades_alta_servidores: str,
    total_vulnerabilidades_media_servidores: str,
    total_vulnerabilidades_baixa_servidores: str,
    total_sites: str,
    criado_por_vm_scan: str,
    graph_output_vm_donut: str, 
    graph_output_webapp_donut: str,
    graph_output_webapp_x_site: str # NOVO: Adicione este parâmetro aqui
):
    """
    Finaliza o relatório LaTeX, inserindo os conteúdos preprocessados e placeholders.
    """
    caminho_relatorio_pronto = os.path.join(caminho_relatorio_preprocessado, "RelatorioPronto")

    copiar_relatorio_exemplo(
        os.path.join(config.caminho_report_templates_base),
        caminho_relatorio_pronto
    )

    with open(os.path.join(caminho_relatorio_pronto, 'main.tex'), 'r', encoding='utf-8') as f:
        latex_code = f.read()

    relatorio_sites_conteudo = []
    caminho_sites_vulnerabilidades_latex = os.path.join(caminho_relatorio_preprocessado, "(LATEX)Sites_agrupados_por_vulnerabilidades.txt")
    if os.path.exists(caminho_sites_vulnerabilidades_latex):
        with open(caminho_sites_vulnerabilidades_latex, "r", encoding='utf-8') as file:
            relatorio_sites_conteudo = file.readlines()
    else:
        print(f"Aviso: Arquivo '{caminho_sites_vulnerabilidades_latex}' não encontrado.")
    relatorio_sites_final = ''.join(relatorio_sites_conteudo)

    relatorio_servidores_conteudo = []
    caminho_servidores_vulnerabilidades_latex = os.path.join(caminho_relatorio_preprocessado, "(LATEX)Servidores_agrupados_por_vulnerabilidades.txt")
    if os.path.exists(caminho_servidores_vulnerabilidades_latex):
        with open(caminho_servidores_vulnerabilidades_latex, "r", encoding='utf-8') as file:
            relatorio_servidores_conteudo = file.readlines()
    else:
        print(f"Aviso: Arquivo '{caminho_servidores_vulnerabilidades_latex}' não encontrado.")
    relatorio_servidores_final = ''.join(relatorio_servidores_conteudo)

    total_vulnerabilidades_combinado = int(total_vulnerabilidades_web) + int(total_vulnerabilidade_vm)

    # NOVO: Placeholder para o gráfico de donut de servidores
    vm_donut_graph_latex = ""
    if graph_output_vm_donut:
        vm_donut_graph_latex = (
            r"""
            \begin{figure}[h!]
            \centering
            \includegraphics[width=0.5\textwidth]{""" + escape_path_for_latex(graph_output_vm_donut) + r"""}
            \caption{Distribuição de Vulnerabilidades de Servidores por Severidade}
            \end{figure}
            \FloatBarrier
            """
        )
    else:
        print("Aviso: Caminho do gráfico donut de servidores não fornecido ou vazio, não será incluído no LaTeX.")

    # NOVO: Placeholder para o gráfico de donut de WebApp
    webapp_donut_graph_latex = ""
    if graph_output_webapp_donut:
        webapp_donut_graph_latex = (
            r"""
            \begin{figure}[h!]
            \centering
            \includegraphics[width=0.5\textwidth]{""" + escape_path_for_latex(graph_output_webapp_donut) + r"""}
            \caption{Distribuição total de vulnerabilidades por severidade}
            \end{figure}
            \FloatBarrier
            """
        )
    else:
        print("Aviso: Caminho do gráfico donut de WebApp não fornecido ou vazio, não será incluído no LaTeX.")

    # Escapar caracteres especiais para LaTeX
    nome_secretaria_escaped = escape_latex(nome_secretaria)
    sigla_secretaria_escaped = escape_latex(sigla_secretaria)


    substituicoes_globais = {
        'NOME SECRETARIA': nome_secretaria_escaped,
        'SIGLA': sigla_secretaria_escaped,
        'INICIO DATA': inicio_data,
        'FIM DATA': fim_data,
        'MES CONCLUSAO': mes_conclusao,
        'ANO CONCLUSAO': ano_conclusao,
        'GOOGLE DRIVE LINK': google_drive_link,
        'RELATORIO GERADO': relatorio_sites_final,
        'RELATORIO SERVIDORES': relatorio_servidores_final,
        'TOTAL VULNERABILIDADES': str(total_vulnerabilidades_combinado),
        'TOTAL VULNERABILIDADES WEB': total_vulnerabilidades_web,
        'TOTAL VULNERABILIDADES VM': total_vulnerabilidade_vm,
        'TOTAL VULNERABILIDADES WAS CRITICA': total_vulnerabilidades_criticas_web,
        'TOTAL VULNERABILIDADES WAS ALTA': total_vulnerabilidades_alta_web,
        'TOTAL VULNERABILIDADES WAS MEDIA': total_vulnerabilidades_media_web,
        'TOTAL VULNERABILIDADES WAS BAIXA': total_vulnerabilidades_baixa_web,
        'TOTAL VULNERABILIDADES SERVIDORES CRITICA': total_vulnerabilidades_criticas_servidores,
        'TOTAL VULNERABILIDADES SERVIDORES ALTA': total_vulnerabilidades_alta_servidores,
        'TOTAL VULNERABILIDADES SERVIDORES MEDIA': total_vulnerabilidades_media_servidores,
        'TOTAL VULNERABILIDADES SERVIDORES BAIXA': total_vulnerabilidades_baixa_servidores,
        'TOTAL_SITES': total_sites,
        'CRIADO_POR_VM_SCAN': criado_por_vm_scan,
        'GRAFICO_DONUT_SERVIDORES': vm_donut_graph_latex, 
        'GRAFICO_DONUT_WEBAPP': webapp_donut_graph_latex, 
        'GRAFICO_WEBAPP_X_SITE': r"""
            \begin{figure}[h!]
            \centering
            \includegraphics[width=1.0\textwidth]{""" + escape_path_for_latex(graph_output_webapp_x_site) + r"""}
            \caption{Total de vulnerabilidades por site}
            \end{figure}
            \FloatBarrier
            """, # NOVO: Adicione este placeholder
    }

    latex_editado = substituir_placeholders(
        conteudo=latex_code,
        substituicoes_globais=substituicoes_globais
    )

    with open(os.path.join(caminho_relatorio_pronto, "main.tex"), "w", encoding="utf-8") as f:
        f.write(latex_editado)
    print(f"Relatório LaTeX final (main.tex) salvo em: {os.path.join(caminho_relatorio_pronto, 'main.tex')}")