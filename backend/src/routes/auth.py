# backend/src/routes/auth.py

import jwt
import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_bcrypt import Bcrypt
from ..core.database import Database

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Inicialize o Bcrypt dentro do escopo da aplicação
bcrypt = Bcrypt()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Credenciais não fornecidas"}), 400

    db = Database()
    user = db.find_one("users", {"username": data.get('username')})
    db.close()

    if not user:
        return jsonify({"error": "Usuário ou senha inválidos"}), 401

    # Inicializa o bcrypt com o app atual para acessar a configuração
    if not hasattr(current_app, 'bcrypt'):
        bcrypt.init_app(current_app)

    if bcrypt.check_password_hash(user['password'], data.get('password')):
        # Gera o token JWT
        token = jwt.encode({
            'public_id': str(user['_id']),
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24) # Token expira em 24 horas
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({
            'token': token,
            'user': {
                'username': user['username'],
                'role': user['role']
            }
        })

    return jsonify({"error": "Usuário ou senha inválidos"}), 401