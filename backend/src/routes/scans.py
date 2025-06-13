from flask import Blueprint, jsonify, request
from flask_cors import CORS, cross_origin
import os

from ..core.config import Config
from ..api.tenable import TenableApi # Importa a TenableApi do novo local

# Inicializa a configuração e a API Tenable
config = Config("config.json")
tenable_api = TenableApi()

scans_bp = Blueprint('scans', __name__, url_prefix='/scans') # Prefixo geral para scans
#CORS(scans_bp, origins=["http://localhost:3000", "http://127.0.0.1:3000"]) # Adicione CORS para este blueprint AQUI

@scans_bp.route('/webapp/scansfromfolderofuser/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def webapp_scansfromfolderofuser():
    """
    Busca scans de aplicação web de uma pasta específica de um usuário.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido."}), 400

        nome_usuario = data.get("nomeUsuario")
        nome_pasta = data.get("nomePasta")

        if not nome_usuario or not nome_pasta:
            return jsonify({"error": "Campos 'nomeUsuario' e 'nomePasta' são obrigatórios."}), 400

        scans = tenable_api.get_web_app_scans_from_folder_of_user(nome_pasta, nome_usuario)

        if scans['pagination']['total'] == 0:
            return jsonify({"message": "Não foi possível encontrar scans nesta pasta. Verifique o usuário e o nome da pasta e tente novamente."}), 404 # 404 para não encontrado

        return jsonify(scans), 200

    except Exception as e:
        print(f"Erro em webapp_scansfromfolderofuser: {e}")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    
@scans_bp.route('/webapp/downloadscans/', methods=['POST'])
#@cross_origin(origins=["http://localhost:3000", "127.0.0.1"]) # Ajustado a porta para 3000 (frontend)
def webapp_downloadscans():
    """
    Baixa os resultados de scans de aplicação web e os salva.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido."}), 400
        
        scans = data.get("scans") # 'scans' aqui é o dicionário completo retornado pela API (com 'items' e 'pagination')
        usuario = data.get("usuario")
        nome_pasta_scan_lista = data.get("nomePasta") # nome da pasta para salvar dentro de json_exports/id_lista

        if not scans or not usuario or not nome_pasta_scan_lista:
            return jsonify({"error": "Campos 'scans', 'usuario' e 'nomePasta' são obrigatórios."}), 400
        
        # O caminho completo para salvar os scans será dentro de json_exports/<ID_DA_LISTA>/
        # 'nome_pasta_scan_lista' aqui deve ser o ID_DA_LISTA recebido do frontend.
        folder_path = os.path.join(config.caminho_shared_jsons, nome_pasta_scan_lista)
        
        # Garante que a pasta existe. Não é necessário lógica de contador aqui,
        # pois cada lista terá seu próprio ID único como pasta raiz.
        os.makedirs(folder_path, exist_ok=True)

        tenable_api.download_scans_results_json(folder_path, scans)

        return jsonify({"message": "Scans baixados com sucesso!"}), 200
    
    except Exception as e:
        print(f"Erro em webapp_downloadscans: {e}")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@scans_bp.route('/vm/getScanByName/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def vm_get_scan_by_name():
    """
    Obtém os detalhes de um scan de Vulnerability Management (VM) pelo nome.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Nenhum dado fornecido."}), 400
    
    name = data.get("name")

    if not name:
        return jsonify({"error": "Campo 'name' é obrigatório."}), 400

    scan = tenable_api.get_vmscans_from_name(name)

    if not scan:
        return jsonify({"message": "Scan não encontrado."}), 404

    return jsonify(scan), 200

@scans_bp.route('/vm/downloadscans/', methods=['POST'])
#@cross_origin(origins=["http://localhost:5173", "127.0.0.1"])
def vm_downloadscans():
    """
    Baixa o resultado de um scan de Vulnerability Management (VM) em formato CSV.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido."}), 400
        
        nome_lista_id = data.get("nomeListaId") # ID da lista que é o nome da pasta de destino
        id_scan = data.get("idScan") # ID do scan VM na Tenable
        history_id = data.get("historyId") # History ID do scan VM na Tenable

        if not nome_lista_id or not id_scan or not history_id:
            return jsonify({"error": "Campos 'nomeListaId', 'idScan' e 'historyId' são obrigatórios."}), 400

        # O caminho completo para salvar o CSV será dentro de json_exports/<ID_DA_LISTA>/
        folder_path = os.path.join(config.caminho_shared_jsons, nome_lista_id)
        
        os.makedirs(folder_path, exist_ok=True) # Garante que a pasta existe

        tenable_api.download_vmscans_csv(folder_path, id_scan, history_id)

        return jsonify({"message": "Scan VM baixado com sucesso!"}), 200
    
    except Exception as e:
        print(f"Erro em vm_downloadscans: {e}")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500