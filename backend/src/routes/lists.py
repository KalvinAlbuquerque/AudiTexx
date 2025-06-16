import json
import logging
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
from ..api.tenable import tenable_api 
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

# CORREÇÃO: Renomear listas_bp para lists_bp para corresponder à importação em main.py
lists_bp = Blueprint('listas', __name__, url_prefix='/lists') 
CORS(lists_bp, origins=["http://localhost:3000", "http://127.0.0.1:3000"]) # Adicione CORS para este blueprint AQUI

@lists_bp.route('/criarLista/', methods=['POST'])
def criarLista():
    try:
        data = request.get_json()

        if not data:
            logging.error("Sem dados no request para criarLista.")
            return jsonify({"error": "Sem dados no request"}), 400

        nomeLista = data.get("nomeLista")

        if not nomeLista:
            logging.error("Campo 'nomeLista' é obrigatório ao criar lista.")
            return jsonify({"error": "Campo 'nomeLista' é obrigatório."}), 400

        db_instance = Database()
        
        lista_existente = db_instance.find_one("listas", {"nomeLista": nomeLista})

        if lista_existente:
            db_instance.close()
            logging.warning(f"Já existe uma lista com o nome \"{nomeLista}\".")
            return jsonify({"error": f"Já existe uma lista com o nome \"{nomeLista}\"."}), 409

        novo_documento_lista = {
            "nomeLista": nomeLista,
            "pastas_scans_webapp": None,
            "pastas_scans_vm": None,
            "id_scan": None,
            "historyid_scanservidor": None,
            "nomeScanStoryId": None,
            "scanStoryIdCriadoPor": None,
            "relatorioGerado": False
        }

        id_lista = db_instance.insert_one("listas", novo_documento_lista).inserted_id

        pasta_base_lista = os.path.join(config.caminho_shared_jsons, str(id_lista))
        pasta_scans_webapp_caminho = os.path.join(pasta_base_lista, "webapp")
        pasta_scans_vm_caminho = os.path.join(pasta_base_lista, "vm")
        
        os.makedirs(pasta_scans_webapp_caminho, exist_ok=True)
        os.makedirs(pasta_scans_vm_caminho, exist_ok=True)
        logging.info(f"Pastas criadas para lista {nomeLista}: {pasta_scans_webapp_caminho}, {pasta_scans_vm_caminho}")

        # CORREÇÃO AQUI: Passar apenas os campos a serem atualizados, sem o '$set'
        db_instance.update_one(
            "listas", 
            {"_id": id_lista}, 
            { # Este é o dicionário 'update' que será envolvido por {"$set": update} em database.py
                "pastas_scans_webapp": pasta_scans_webapp_caminho,
                "pastas_scans_vm": pasta_scans_vm_caminho
            }
        )

        db_instance.close()
        logging.info(f"Lista '{nomeLista}' criada com sucesso! ID: {str(id_lista)}")

        return jsonify({"message": "Lista criada com sucesso!", "idLista": str(id_lista)}), 201

    except Exception as e:
        logging.exception(f"Erro ao criar lista: {e}")
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

        # --- CORREÇÃO APLICADA AQUI ---
        # Alterado para buscar os nomes de campo corretos que foram salvos.
        nome_scan = documento.get("nome_scanservidor")
        criado_por = documento.get("criado_por_scanservidor")

        # Se os campos corretos não existirem ou estiverem vazios, retorna 404.
        if not nome_scan or not criado_por:
            return jsonify({"message": "Não existem dados de VM para esta lista."}), 404

        # Retorna os dados encontrados com sucesso.
        return jsonify([nome_scan, criado_por]), 200

    except Exception as e:
        print(f"Erro em getVMScansDeLista: {e}")
        # Garante que a conexão seja fechada em caso de erro.
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
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"]) # Descomente se precisar
def adicionarWAPPScanALista():  
    try:
        data = request.get_json()

        if not data:
            logging.error("Nenhum dado JSON fornecido na requisição para /adicionarWAPPScanALista/.")
            return jsonify({"error": "Nenhum dado fornecido."}), 400

        nome_lista = data.get("nomeLista")
        scans_from_request = data.get("scans") # Este é o dicionário completo com 'pagination' e 'items'

        if not nome_lista or not scans_from_request:
            logging.error("Nome da lista ou dados de scans não fornecidos.")
            return jsonify({"error": "Nome da lista ou scans não fornecidos."}), 400

        if not isinstance(scans_from_request, dict) or "items" not in scans_from_request:
            logging.error(f"Formato inesperado para 'scans'. Esperado um objeto com a chave 'items'. Recebido: {type(scans_from_request)}")
            return jsonify({"error": "Formato inválido para dados de scans. Esperado um objeto com a chave 'items'."}), 400

        db = Database()
        documento = db.find_one("listas", {"nomeLista": nome_lista})
        db.close() # Sempre fechar a conexão do DB

        if not documento:
            logging.warning(f"Lista '{nome_lista}' não encontrada no banco de dados.")
            return jsonify({"error": "Lista não encontrada"}), 404
        
        pasta_destino_scans = documento.get("pastas_scans_webapp")
        if not pasta_destino_scans:
            logging.error(f"Caminho da pasta de scans para a lista '{nome_lista}' não configurado no documento do banco de dados.")
            return jsonify({"error": "Caminho da pasta de scans para a lista não configurado."}), 500
        
        os.makedirs(pasta_destino_scans, exist_ok=True)
        logging.info(f"Diretório de destino '{pasta_destino_scans}' garantido para lista '{nome_lista}'.")

        # Chama a função download_scans_results_json passando o diretório e o dicionário completo de scans
        tenable_api.download_scans_results_json(
            pasta_destino_scans,
            scans_from_request
        )
        logging.info(f"Processamento de download de WebApp scans para lista '{nome_lista}' concluído.")

        # Opcional: Atualizar o documento da lista no banco de dados com os scans baixados.
        # Isso dependeria de como você quer armazenar as referências aos arquivos baixados.
        # Exemplo (requer reabrir a conexão com o DB ou passar uma instância aberta):
        # db_instance = Database()
        # for scan_data in scans_from_request.get("items", []):
        #     scan_id = scan_data.get("last_scan", {}).get("scan_id")
        #     if scan_id:
        #         file_path = os.path.join(pasta_destino_scans, f"{scan_id}.json")
        #         # Supondo que você queira adicionar apenas o ID e o caminho do arquivo à lista
        #         db_instance.update_one(
        #             "listas",
        #             {"nomeLista": nome_lista},
        #             {"$addToSet": {"scans_webapp": {"config_id": scan_data.get("config_id"), "scan_id": scan_id, "filePath": file_path}}}
        #         )
        # db_instance.close()

        return jsonify({"message": "Scans de WebApp adicionados à lista com sucesso!"}), 200

    except Exception as e:
        logging.exception(f"Erro inesperado na rota /adicionarWAPPScanALista/: {e}")
        # Garante que a conexão com o banco de dados seja fechada em caso de erro
        if 'db' in locals() and db.client:
            db.close()
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@lists_bp.route('/adicionarVMScanALista/', methods=['POST'])
def adicionarVMScanALista():
    """
    Adiciona um scan de VM a uma lista existente na coleção 'listas'.
    """
    try:
        # 1. Instanciar a sua classe (como você já faz nas outras funções)
        db_instance = Database()
        
        data = request.get_json()
        if not data:
            db_instance.close()
            return jsonify({"error": "Corpo da requisição não pode ser vazio."}), 400

        nome_lista = data.get("nomeLista")
        id_scan_vm = data.get("idScan")
        nome_scan_vm = data.get("nomeScan")
        criado_por_vm = data.get("criadoPor")
        history_id = data.get("idNmr")

        if not all([nome_lista, id_scan_vm, nome_scan_vm, criado_por_vm, history_id]):
            db_instance.close()
            return jsonify({"error": "Campos 'nomeLista', 'idScan', 'nomeScan', 'criadoPor' e 'idNmr' são obrigatórios."}), 400

        # --- CORREÇÃO PRINCIPAL AQUI ---
        # Usar o método .update_one() do seu objeto db_instance, assim como em 'criarLista'
        query = {"nomeLista": nome_lista}
        update_data = {
            "id_scanservidor": id_scan_vm,
            "nome_scanservidor": nome_scan_vm,
            "criado_por_scanservidor": criado_por_vm,
            "historyid_scanservidor": history_id
        }
        resultado = db_instance.update_one('listas', query, update_data)
        
        # Sempre feche a conexão após o uso
        db_instance.close()

        if resultado.matched_count == 0:
            return jsonify({"error": "Lista não encontrada."}), 404

        logging.info(f"Scan VM {nome_scan_vm} (ID: {id_scan_vm}) adicionado à lista '{nome_lista}' com sucesso.")
        return jsonify({"message": f"Scan VM adicionado à lista '{nome_lista}' com sucesso!"}), 200

    except Exception as e:
        logging.exception(f"Erro inesperado ao adicionar scan de VM à lista: {e}")
        # Garante que a conexão seja fechada em caso de erro
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Ocorreu um erro inesperado no servidor: {str(e)}"}), 500
    
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