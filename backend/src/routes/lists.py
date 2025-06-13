import json
from flask import Blueprint, jsonify, request, send_file
from flask_cors import CORS, cross_origin

import time
import os
from pathlib import Path
import shutil
import re # Importado para usar re.search
import pandas as pd # Importado para usar pd.DataFrame

from bson.objectid import ObjectId

# Importa a classe Config
from ..core.config import Config
# Importa a TenableApi do novo local
from ..api.tenable import TenableApi
# Importa o Database
from ..core.database import Database

# Importa as funções de processamento de dados
from ..data_processing.vulnerability_analyzer import processar_relatorio_csv, processar_relatorio_json, extrair_quantidades_vulnerabilidades_por_site
# Importa as funções de construção de relatório e compilação
from ..report_generation.report_builder import terminar_relatorio_preprocessado, carregar_vulnerabilidades_do_relatorio, carregar_vulnerabilidades_do_relatorio_csv # Adicionado carregadores TXT
from ..report_generation.latex_compiler import compilar_latex
from ..report_generation.plot_generator import gerar_Grafico_Quantitativo_Vulnerabilidades_Por_Site # CORREÇÃO: Importar a função de plotagem

# Inicializa a configuração e a API Tenable
config = Config("config.json")
tenable_api = TenableApi()

# CORREÇÃO: Renomear listas_bp para lists_bp para corresponder à importação em main.py
lists_bp = Blueprint('listas', __name__, url_prefix='/lists') 
CORS(lists_bp, origins=["http://localhost:3000", "http://127.0.0.1:3000"]) # Adicione CORS para este blueprint AQUI

@lists_bp.route('/criarLista/', methods=['POST'])
##@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def criarLista():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Sem dados no request"}), 400

        nomeLista = data.get("nomeLista")

        if not nomeLista:
            return jsonify({"error": "Campo 'nomeLista' é obrigatório."}), 400

        db_instance = Database()
        
        lista_existente = db_instance.find_one("listas", {"nomeLista": nomeLista})

        if lista_existente:
            db_instance.close()
            return jsonify({"error": f"Já existe uma lista com o nome \"{nomeLista}\"."}), 409

        id_lista = db_instance.insert_one("listas", {
            "nomeLista": nomeLista,
            "pastas_scans_webapp": None,
            "id_scan": None,
            "historyid_scanservidor": None,
            "nomeScanStoryId": None,
            "scanStoryIdCriadoPor": None,
            "relatorioGerado": False
        }).inserted_id

        pasta_scan = os.path.join(config.caminho_shared_jsons, str(id_lista)) + os.sep
        
        db_instance.update_one("listas", {"_id": id_lista}, {"pastas_scans_webapp": pasta_scan})

        os.makedirs(pasta_scan, exist_ok=True)

        db_instance.close()

        return jsonify({"message": "Lista criada com sucesso!", "idLista": str(id_lista)}), 201

    except Exception as e:
        print(f"Erro ao criar lista: {e}")
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    
@lists_bp.route('/getScansDeLista/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def getScansDeLista():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido."}), 400

        nome_lista = data.get("nomeLista")

        if not nome_lista:
            return jsonify({"error": "Nome da lista não fornecido"}), 400

        db_instance = Database()

        documento = db_instance.find_one("listas", {"nomeLista": nome_lista})

        db_instance.close()

        if not documento:
            return jsonify({"error": "Lista não encontrada"}), 404
        
        scans = []
        pasta_scans = documento.get("pastas_scans_webapp")

        if not pasta_scans or not os.path.exists(pasta_scans):
            return jsonify({"message": "Pasta de scans não encontrada ou vazia para esta lista."}), 200

        for arquivo in os.listdir(pasta_scans):
            if arquivo.endswith(".json"):
                caminho_arquivo = os.path.join(pasta_scans, arquivo)
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        conteudo = json.load(f)
                        nome_scan = conteudo.get("config", {}).get("name")
                        if nome_scan:
                            scans.append(nome_scan)
                except json.JSONDecodeError:
                    print(f"Aviso: Arquivo JSON inválido: {caminho_arquivo}")
                except Exception as e:
                    print(f"Erro ao ler scan JSON '{caminho_arquivo}': {e}")
        
        return jsonify(scans), 200

    except Exception as e:
        print(f"Erro em getScansDeLista: {e}")
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    

@lists_bp.route('/getVMScansDeLista/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def getVMScansDeLista():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido."}), 400

        nome_lista = data.get("nomeLista")

        if not nome_lista:
            return jsonify({"error": "Nome da lista não fornecido"}), 400

        db_instance = Database()

        documento = db_instance.find_one("listas", {"nomeLista": nome_lista})

        db_instance.close()

        if not documento:
            return jsonify({"error": "Lista não encontrada"}), 404

        nomeScanStoryId = documento.get("nomeScanStoryId")
        criadoPor = documento.get("scanStoryIdCriadoPor")

        if not nomeScanStoryId or not criadoPor:
            return jsonify({"message": "Não existem dados de VM para esta lista."}), 404

        return jsonify([nomeScanStoryId, criadoPor]), 200

    except Exception as e:
        print(f"Erro em getVMScansDeLista: {e}")
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@lists_bp.route('/limparScansDeLista/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def limparScansDeLista():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido."}), 400

        nome_lista = data.get("nomeLista")

        if not nome_lista:
            return jsonify({"error": "Nome da lista não fornecido"}), 400

        db_instance = Database()

        documento = db_instance.find_one("listas", {"nomeLista": nome_lista})

        db_instance.close()

        if not documento:
            return jsonify({"error": "Lista não encontrada"}), 404
        
        pasta_scans = documento.get("pastas_scans_webapp")

        if pasta_scans and os.path.exists(pasta_scans):
            for item in os.listdir(pasta_scans):
                item_path = os.path.join(pasta_scans, item)
                if os.path.isfile(item_path):
                    if item.endswith(".json"):
                        os.unlink(item_path)
                        print(f"DEBUG: Arquivo JSON de WebApp excluído: {item_path}")
        
        return jsonify({"message": "Scans de WebApp da lista limpos com sucesso!"}), 200

    except Exception as e:
        print(f"Erro ao limpar scans de WebApp da lista: {e}")
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    
@lists_bp.route('/limparVMScansDeLista/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def limparVMScansDeLista():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido."}), 400

        nome_lista = data.get("nomeLista")

        if not nome_lista:
            return jsonify({"error": "Nome da lista não fornecido"}), 400

        db_instance = Database()

        documento = db_instance.find_one("listas", {"nomeLista": nome_lista})

        if not documento:
            return jsonify({"error": "Lista não encontrada"}), 404
        
        pasta_scans = documento.get("pastas_scans_webapp")
        csv_path = None
        if pasta_scans:
            csv_path = os.path.join(pasta_scans, "servidores_scan.csv")
        
        db_instance.update_one(
            "listas",
            {"_id": ObjectId(documento["_id"])},
            {"id_scan": None,
             "historyid_scanservidor": None,
             "nomeScanStoryId": None,
             "scanStoryIdCriadoPor": None}
        )
        
        if csv_path and os.path.exists(csv_path):
            os.unlink(csv_path)
            print(f"DEBUG: Arquivo CSV de VM excluído: {csv_path}")

        db_instance.close()

        return jsonify({"message": "Scans de VM da lista limpos com sucesso!"}), 200

    except Exception as e:
        print(f"Erro ao limpar scans de VM da lista: {e}")
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@lists_bp.route('/editarNomeLista/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def editar_nome_lista():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido."}), 400

        lista_id = data.get("id")
        novo_nome = data.get("novoNome")

        if not lista_id or not novo_nome:
            return jsonify({"error": "ID da lista ou novo nome não fornecido."}), 400

        db_instance = Database()

        lista_existente_com_novo_nome = db_instance.find_one("listas", {"nomeLista": novo_nome})
        if lista_existente_com_novo_nome and str(lista_existente_com_novo_nome["_id"]) != lista_id:
            db_instance.close()
            return jsonify({"error": f"Já existe uma lista com o nome \"{novo_nome}\"."}), 409

        resultado = db_instance.update_one(
            "listas",
            {"_id": ObjectId(lista_id)},
            {"nomeLista": novo_nome}
        )

        db_instance.close()

        if resultado.modified_count == 0:
            return jsonify({"message": "Nenhuma modificação realizada. O nome pode ser o mesmo ou a lista não foi encontrada."}), 404

        return jsonify({"message": "Nome da lista atualizado com sucesso!"}), 200

    except Exception as e:
        print(f"Erro ao editar nome da lista: {e}")
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    
@lists_bp.route('/adicionarWAPPScanALista/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def adicionarWAPPScanALista():  
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido."}), 400

        nome_lista = data.get("nomeLista")
        scans_para_baixar = data.get("scans")

        if not nome_lista or not scans_para_baixar:
            return jsonify({"error": "Nome da lista ou scans não fornecidos."}), 400

        db_instance = Database()

        documento = db_instance.find_one("listas", {"nomeLista": nome_lista})

        if not documento:
            db_instance.close()
            return jsonify({"error": "Lista não encontrada"}), 404
        
        pasta_destino_scans = documento.get("pastas_scans_webapp")
        if not pasta_destino_scans:
            db_instance.close()
            return jsonify({"error": "Caminho da pasta de scans para a lista não configurado."}), 500
        
        os.makedirs(pasta_destino_scans, exist_ok=True)

        tenable_api.download_scans_results_json(
            pasta_destino_scans,
            scans_para_baixar
        )

        db_instance.close()

        return jsonify({"message": "Scans de WebApp adicionados à lista com sucesso!"}), 200

    except Exception as e:
        print(f"Erro ao adicionar scans de WebApp à lista: {e}")
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@lists_bp.route('/adicionarVMScanALista/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def adicionarVMScanALista():  
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido."}), 400

        nome_lista = data.get("nomeLista")
        id_scan_tenable = data.get("idScan")
        nome_scan_tenable = data.get("nomeScan")
        criado_por_tenable = data.get("criadoPor")
        id_nmr_tenable = str(data.get("idNmr"))

        if not all([nome_lista, id_scan_tenable, nome_scan_tenable, criado_por_tenable, id_nmr_tenable]):
            return jsonify({"error": "Dados de VM scan incompletos."}), 400

        db_instance = Database()

        documento = db_instance.find_one("listas", {"nomeLista": nome_lista})

        if not documento:
            return jsonify({"error": "Lista não encontrada"}), 404
        
        pasta_destino_scans = documento.get("pastas_scans_webapp")
        if not pasta_destino_scans:
            db_instance.close()
            return jsonify({"error": "Caminho da pasta de scans para a lista não configurado."}), 500
        
        os.makedirs(pasta_destino_scans, exist_ok=True)

        db_instance.update_one(
            "listas",
            {"_id": ObjectId(documento["_id"])},
            {"id_scan": id_nmr_tenable,
             "historyid_scanservidor": id_scan_tenable,
             "nomeScanStoryId": nome_scan_tenable,
             "scanStoryIdCriadoPor": criado_por_tenable}
        )

        db_instance.close()

        tenable_api.download_vmscans_csv(
            pasta_destino_scans,
            id_nmr_tenable,
            id_scan_tenable
        )

        return jsonify({"message": "Scan VM adicionado à lista com sucesso!"}), 200

    except Exception as e:
        print(f"Erro ao adicionar scan VM à lista: {e}")
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@lists_bp.route('/getTodasAsListas/', methods=['GET'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def getTodasAsListas():

    try:
        db_instance = Database()

        listas = db_instance.find("listas")

        listas_json = []

        for lista in listas:
            listas_json.append({
                "idLista": str(lista["_id"]),
                "nomeLista": lista["nomeLista"],
                "relatorioGerado": lista.get("relatorioGerado", False)
            })

        db_instance.close()

        return jsonify(listas_json), 200

    except Exception as e:
        print(f"Erro ao obter todas as listas: {e}")
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    
""" @lists_bp.route('/gerarRelatorioDeLista/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def gerarRelatorioDeLista():

    try:

        data = request.get_json()

        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        id_lista = data.get("idLista")
        nome_secretaria = data.get("nomeSecretaria")
        sigla_secretaria = data.get("siglaSecretaria")
        data_inicio = data.get("dataInicio")
        data_fim = data.get("dataFim")
        ano = data.get("ano")
        mes = data.get("mes")
        google_drive_link = data.get("linkGoogleDrive")

        db_instance = Database()

        try:
            objeto_id = ObjectId(id_lista)
        except Exception:
            db_instance.close()
            return jsonify({"error": "ID de lista inválido"}), 400
        
        lista_doc = db_instance.find_one("listas", {"_id": objeto_id})

        if not lista_doc:
            db_instance.close()
            return jsonify({"error": "Lista não encontrada"}), 404

        novo_relatorio_id = db_instance.insert_one("relatorios", {"nome": nome_secretaria, "id_lista": id_lista, "destino_relatorio_preprocessado" : None}).inserted_id

        pasta_destino_relatorio_temp = Path(config.caminho_shared_relatorios) / str(novo_relatorio_id) / "relatorio_preprocessado"
        pasta_destino_relatorio_temp.mkdir(parents=True, exist_ok=True)
        
        pasta_scans_da_lista = lista_doc.get("pastas_scans_webapp")

        db_instance.update_one(
            "relatorios",
            {"_id": novo_relatorio_id},
            {"destino_relatorio_preprocessado": str(pasta_destino_relatorio_temp)}
        )

        # Processamento de Scans WebApp (JSON)
        webapp_report_txt_path = pasta_destino_relatorio_temp / "Sites_agrupados_por_vulnerabilidades.txt"
        webapp_csv_path = pasta_destino_relatorio_temp / "vulnerabilidades_agrupadas_por_site.csv"
        
        if pasta_scans_da_lista and os.path.exists(pasta_scans_da_lista) and len([f for f in os.listdir(pasta_scans_da_lista) if f.endswith('.json')]) > 0:
            processar_relatorio_json(pasta_scans_da_lista, str(pasta_destino_relatorio_temp))
            extrair_quantidades_vulnerabilidades_por_site(str(webapp_csv_path), pasta_scans_da_lista)
        else:
            print(f"Aviso: Não há scans WebApp na pasta {pasta_scans_da_lista} ou a pasta está vazia. Pulando processamento WebApp.")
            pd.DataFrame(columns=['Site', 'Critical', 'High', 'Medium', 'Low', 'Total']).to_csv(webapp_csv_path, index=False)
            Path(webapp_report_txt_path).touch()
            Path(pasta_destino_relatorio_temp / "(LATEX)Sites_agrupados_por_vulnerabilidades.txt").touch()

        # Processamento de Scans Servidores (CSV)
        servers_report_txt_path = pasta_destino_relatorio_temp / "Servidores_agrupados_por_vulnerabilidades.txt"
        
        if lista_doc.get("historyid_scanservidor") and lista_doc.get("id_scan") and \
           pasta_scans_da_lista and os.path.exists(os.path.join(pasta_scans_da_lista, "servidores_scan.csv")):
            processar_relatorio_csv(pasta_scans_da_lista, str(pasta_destino_relatorio_temp))
        else:
            print("Aviso: Não há scans de Servidores associados a esta lista ou o arquivo CSV não foi encontrado. Pulando processamento de Servidores.")
            Path(servers_report_txt_path).touch()
            Path(pasta_destino_relatorio_temp / "(LATEX)Servidores_agrupados_por_vulnerabilidades.txt").touch()

        # Leitura dos totais para o relatório final
        webapp_risk_counts = {'Critical': '0', 'High': '0', 'Medium': '0', 'Low': '0'}
        total_sites = '0'
        total_vulnerabilidades_web = '0'
        if webapp_report_txt_path.exists():
            with open(webapp_report_txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                total_sites_match = re.search(r'Total de sites:\s*(\d+)', content)
                total_vulnerabilidades_web_match = re.search(r'Total de Vulnerabilidades:\s*(\d+)', content)
                critical_match = re.search(r'Critical:\s*(\d+)', content)
                high_match = re.search(r'High:\s*(\d+)', content)
                medium_match = re.search(r'Medium:\s*(\d+)', content)
                low_match = re.search(r'Low:\s*(\d+)', content)

                if total_sites_match: total_sites = total_sites_match.group(1)
                if total_vulnerabilidades_web_match: total_vulnerabilidades_web = total_vulnerabilidades_web_match.group(1)
                if critical_match: webapp_risk_counts['Critical'] = critical_match.group(1)
                if high_match: webapp_risk_counts['High'] = high_match.group(1)
                if medium_match: webapp_risk_counts['Medium'] = medium_match.group(1)
                if low_match: webapp_risk_counts['Low'] = low_match.group(1)

        servers_risk_counts = {'critical': '0', 'high': '0', 'medium': '0', 'low': '0'}
        total_vulnerabilidade_vm = '0'
        if servers_report_txt_path.exists():
            with open(servers_report_txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                total_vulnerabilidade_vm_match = re.search(r'Total de Vulnerabilidades:\s*(\d+)', content)
                critical_match = re.search(r'Critical:\s*(\d+)', content)
                high_match = re.search(r'High:\s*(\d+)', content)
                medium_match = re.search(r'Medium:\s*(\d+)', content)
                low_match = re.search(r'Low:\s*(\d+)', content)

                if total_vulnerabilidade_vm_match: total_vulnerabilidade_vm = total_vulnerabilidade_vm_match.group(1)
                if critical_match: servers_risk_counts['critical'] = critical_match.group(1)
                if high_match: servers_risk_counts['high'] = high_match.group(1)
                if medium_match: servers_risk_counts['medium'] = medium_match.group(1)
                if low_match: servers_risk_counts['low'] = low_match.group(1)

        caminho_final_main_tex = str(pasta_destino_relatorio_temp / "RelatorioPronto" / "main.tex")

        terminar_relatorio_preprocessado(
            nome_secretaria,
            sigla_secretaria,
            data_inicio,
            data_fim,
            ano,
            mes,
            str(pasta_destino_relatorio_temp),
            caminho_final_main_tex,
            google_drive_link,
            total_vulnerabilidades_web,
            total_vulnerabilidade_vm,
            webapp_risk_counts['Critical'],
            webapp_risk_counts['High'],
            webapp_risk_counts['Medium'],
            webapp_risk_counts['Low'],
            servers_risk_counts['critical'],
            servers_risk_counts['high'],
            servers_risk_counts['medium'],
            servers_risk_counts['low'],
            total_sites
        )

        graph_output_webapp = str(pasta_destino_relatorio_temp / "RelatorioPronto" / "assets" / "images-was" / "Vulnerabilidades_x_site.png")
        gerar_Grafico_Quantitativo_Vulnerabilidades_Por_Site(
            str(webapp_csv_path),
            graph_output_webapp,
            "descendente"
        )
        
        pasta_final_latex = str(pasta_destino_relatorio_temp / "RelatorioPronto")
        compilar_latex(os.path.join(pasta_final_latex, "main.tex"), pasta_final_latex)

        pasta_front_downloads = Path("../frontend/downloads") / str(novo_relatorio_id)
        pasta_front_downloads.mkdir(parents=True, exist_ok=True)
        
        shutil.copy(
            Path(pasta_final_latex) / "main.pdf",
            pasta_front_downloads / "main.pdf"
        )

        db_instance.update_one("listas", {"_id": objeto_id}, {"relatorioGerado": True})
        db_instance.close()

        return str(novo_relatorio_id), 200

    except Exception as e:
        print(f"Erro ao gerar relatório de lista: {str(e)}")
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno ao gerar relatório: {str(e)}"}), 500 """

@lists_bp.route('/excluirLista/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def excluirLista():

    try:

        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado recebido."}), 400
        
        id_lista = data.get("idLista")

        db_instance = Database()

        try:
            objeto_id = ObjectId(id_lista)
        except Exception:
            db_instance.close()
            return jsonify({"error": "ID inválido"}), 400

        lista_doc = db_instance.find_one("listas", {"_id": objeto_id})
        if not lista_doc:
            db_instance.close()
            return jsonify({"message": "Lista não encontrada no banco de dados."}), 404
            
        delete_result = db_instance.delete_one("listas", {"_id": objeto_id})

        if delete_result.deleted_count == 0:
            db_instance.close()
            return jsonify({"message": "Lista não encontrada para exclusão."}), 404

        pasta_lista = lista_doc.get("pastas_scans_webapp")
        if pasta_lista and os.path.exists(pasta_lista):
            shutil.rmtree(pasta_lista)
            print(f"DEBUG: Pasta da lista excluída: {pasta_lista}")
        else:
            print(f"DEBUG: Pasta da lista '{pasta_lista}' não encontrada ou não é um diretório.")

        db_instance.close()

        return jsonify({"message": "Lista excluída com sucesso!"}), 200
        
    except Exception as e:
        print(f"Erro ao excluir lista: {e}")
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500