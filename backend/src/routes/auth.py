# backend/src/routes/auth.py

import jwt
import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_bcrypt import Bcrypt
from ..core.database import Database
from ..auth.decorators import token_required


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
                'role': user['role'],
                'email': user.get('email')

            }
        })

    return jsonify({"error": "Usuário ou senha inválidos"}), 401

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    data = request.get_json()
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400

    # Verificar se a senha atual está correta
    if not bcrypt.check_password_hash(current_user['password'], data['current_password']):
        return jsonify({'error': 'Senha atual incorreta'}), 401

    # Criptografar a nova senha
    hashed_password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')

    # Atualizar no banco de dados
    db = Database()
    db.update_one(
        'users',
        {'_id': current_user['_id']},
        {'password': hashed_password}
    )
    db.close()

    return jsonify({'message': 'Senha alterada com sucesso!'}), 200