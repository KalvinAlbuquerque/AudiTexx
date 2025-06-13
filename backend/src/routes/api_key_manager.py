# backend/src/routes/api_key_manager.py

from flask import Blueprint, jsonify, request
from ..core.database import Database
from ..api.tenable import tenable_api 

api_keys_bp = Blueprint('api_keys', __name__, url_prefix='/api-keys')

@api_keys_bp.route('/tenable', methods=['GET'])
def get_tenable_api_keys():
    db = Database()
    config_doc = db.db.configs.find_one({"name": "tenable_api_keys"})
    
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
    data = request.get_json()
    # CORREÇÃO: Esperando as chaves em snake_case ('access_key', 'secret_key')
    if not data or 'access_key' not in data or 'secret_key' not in data:
        return jsonify({"error": "Chaves 'access_key' e 'secret_key' são obrigatórias"}), 400

    db = Database()
    db.db.configs.update_one(
        {"name": "tenable_api_keys"},
        {"$set": {
            # CORREÇÃO: Usando as chaves corretas do JSON recebido
            "TENABLE_ACCESS_KEY": data['access_key'],
            "TENABLE_SECRET_KEY": data['secret_key']
        }},
        upsert=True
    )
    
    tenable_api.reload_client()
    
    return jsonify({"message": "Chaves da API do Tenable atualizadas com sucesso."}), 200