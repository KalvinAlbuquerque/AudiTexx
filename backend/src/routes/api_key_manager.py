from flask import Blueprint, jsonify, request
from ..core.database import Database
from ..api.tenable import TenableApi

api_keys_bp = Blueprint('api_keys', __name__, url_prefix='/api-keys')

@api_keys_bp.route('/tenable', methods=['GET'])
def get_tenable_api_keys():
    """
    Retorna as chaves de API do Tenable armazenadas no banco de dados.
    """
    db = Database()
    config_doc = db.find_one("configs", {"name": "tenable_api_keys"})
    db.close()

    if config_doc:
        return jsonify({
            "TENABLE_ACCESS_KEY": config_doc.get("TENABLE_ACCESS_KEY", ""),
            "TENABLE_SECRET_KEY": config_doc.get("TENABLE_SECRET_KEY", "")
        }), 200
    return jsonify({
        "TENABLE_ACCESS_KEY": "",
        "TENABLE_SECRET_KEY": ""
    }), 200

@api_keys_bp.route('/tenable', methods=['POST'])
def update_tenable_api_keys():
    """
    Atualiza as chaves de API do Tenable no banco de dados e recarrega a TenableApi.
    """
    data = request.get_json()
    access_key = data.get("TENABLE_ACCESS_KEY")
    secret_key = data.get("TENABLE_SECRET_KEY")

    if not access_key or not secret_key:
        return jsonify({"error": "Access Key e Secret Key são obrigatórios."}), 400

    db = Database()
    # Usa upsert=True para criar o documento se ele não existir
    result = db.update_one(
        "configs",
        {"name": "tenable_api_keys"},
        {"TENABLE_ACCESS_KEY": access_key, "TENABLE_SECRET_KEY": secret_key},
        upsert=True # Se o documento não existir, ele será inserido
    )
    db.close()

    # Força a recarga da instância do TenableApi para usar as novas chaves
    tenable_api = TenableApi()
    tenable_api.reload_client()

    return jsonify({"message": "Chaves da API Tenable atualizadas com sucesso!"}), 200