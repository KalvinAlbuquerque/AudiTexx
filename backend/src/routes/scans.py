from flask import Blueprint, jsonify, request
from flask_cors import CORS
from ..api.tenable import tenable_api
from ..core.config import Config
import logging
import os
import json

# Define o Blueprint para as rotas de scans
scans_bp = Blueprint('scans', __name__, url_prefix='/scans')

# Aplica o CORS a TODAS as rotas neste blueprint
CORS(scans_bp)

# Inicializa a configuração para ter acesso aos caminhos
config = Config("config.json")

@scans_bp.route('/webapp/scansfromfolderofuser/', methods=['POST'])
def webapp_scansfromfolderofuser():
    """
    Busca scans de aplicação web de uma pasta específica de um usuário.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição não pode ser vazio."}), 400

        # Corrigido para usar as chaves exatas do seu código de exemplo
        folder_name = data.get('nomePasta')
        user_name = data.get('nomeUsuario')
        
        if not folder_name or not user_name:
            return jsonify({"error": "Parâmetros 'nomePasta' e 'nomeUsuario' são obrigatórios"}), 400

        scans = tenable_api.get_web_app_scans_from_folder_of_user(folder_name, user_name)

        # Se a API retornar um erro, repassa para o frontend
        if isinstance(scans, dict) and 'error' in scans:
             return jsonify(scans), 404 # 404 para não encontrado ou erro de API
        
        # Se a busca for bem-sucedida mas não houver itens
        if isinstance(scans, dict) and scans.get("pagination", {}).get("total", 0) == 0:
            return jsonify({"message": "Nenhum scan encontrado nesta pasta para este usuário."}), 404

        return jsonify(scans)

    except Exception as e:
        logging.error(f"Erro em /webapp/scansfromfolderofuser/: {e}")
        return jsonify({"error": f"Ocorreu um erro inesperado: {str(e)}"}), 500

@scans_bp.route('/webapp/downloadscans/', methods=['POST'])
def webapp_downloadscans():
    """
    Baixa os resultados de scans de aplicação web e os salva como arquivos JSON.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição não pode ser vazio."}), 400
        
        scans_data = data.get("scans")
        # O ID da lista é usado como nome da pasta
        list_id = data.get("nomePasta") 

        if not scans_data or not list_id:
            return jsonify({"error": "Campos 'scans' e 'nomePasta' (ID da lista) são obrigatórios."}), 400
        
        # Define o caminho de destino para os arquivos
        target_dir = os.path.join(config.caminho_shared_jsons, str(list_id))
        os.makedirs(target_dir, exist_ok=True)

        # Itera sobre cada scan para baixar seus resultados
        for scan_config in scans_data.get("items", []):
            vulnerabilities = tenable_api.download_scans_results_json(scan_config)
            
            if vulnerabilities and 'error' not in vulnerabilities:
                # Usa o ID da configuração do scan para nomear o arquivo
                config_id = scan_config.get("config_id")
                file_path = os.path.join(target_dir, f"{config_id}.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(vulnerabilities, f, ensure_ascii=False, indent=4)
                logging.info(f"Resultados do scan {config_id} salvos em {file_path}")
            else:
                logging.warning(f"Não foi possível baixar resultados para o scan {scan_config.get('config_id')}. Resposta: {vulnerabilities}")

        return jsonify({"message": "Download dos scans concluído."})

    except Exception as e:
        logging.error(f"Erro em /webapp/downloadscans/: {e}")
        return jsonify({"error": f"Ocorreu um erro inesperado: {str(e)}"}), 500

@scans_bp.route('/vm/getScanByName/', methods=['POST'])
def get_vm_scan_by_name_route():
    """
    Busca um scan de VM pelo nome.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição não pode ser vazio."}), 400
        
        # Corrigido para usar a chave 'name' como no seu código de exemplo
        scan_name = data.get('name')

        if not scan_name:
            return jsonify({"error": "Parâmetro 'name' é obrigatório"}), 400

        scan_details = tenable_api.get_vm_scan_by_name(scan_name)
        
        if isinstance(scan_details, dict) and 'error' in scan_details:
             return jsonify(scan_details), 404

        return jsonify(scan_details)

    except Exception as e:
        logging.error(f"Erro em /vm/getScanByName/: {e}")
        return jsonify({"error": f"Ocorreu um erro inesperado: {str(e)}"}), 500

@scans_bp.route('/vm/downloadscans/', methods=['POST'])
def vm_downloadscans():
    """
    Baixa o resultado de um scan de VM em formato CSV.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Corpo da requisição não pode ser vazio."}), 400

        list_id = data.get("nomeListaId")
        scan_id = data.get("idScan")
        # history_id não é usado na implementação atual da API, mas pode ser adicionado no futuro
        history_id = data.get("historyId")

        if not list_id or not scan_id:
            return jsonify({"error": "Campos 'nomeListaId' e 'idScan' são obrigatórios."}), 400

        # Define o caminho de destino
        target_dir = os.path.join(config.caminho_shared_jsons, str(list_id))
        os.makedirs(target_dir, exist_ok=True)
        
        csv_content = tenable_api.download_vmscans_csv(scan_id)

        if csv_content and not (isinstance(csv_content, dict) and 'error' in csv_content):
            file_path = os.path.join(target_dir, f"vm_scan_{scan_id}.csv")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(csv_content)
            logging.info(f"Scan de VM {scan_id} salvo em {file_path}")
            return jsonify({"message": "Scan VM baixado com sucesso!"})
        else:
            logging.error(f"Falha ao baixar scan de VM {scan_id}. Resposta: {csv_content}")
            return jsonify({"error": "Falha ao baixar o arquivo CSV do scan.", "details": csv_content}), 500

    except Exception as e:
        logging.error(f"Erro em /vm/downloadscans/: {e}")
        return jsonify({"error": f"Ocorreu um erro inesperado: {str(e)}"}), 500
