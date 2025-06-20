# backend/src/auth/decorators.py

from functools import wraps
import jwt
from flask import request, jsonify, current_app
from ..core.database import Database
from bson.objectid import ObjectId

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            # O cabeçalho deve ser 'Bearer <token>'
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token está faltando!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            db = Database()
            current_user = db.find_one("users", {'_id': ObjectId(data['public_id'])})
            db.close()
            if not current_user:
                 return jsonify({'message': 'Usuário do token não encontrado!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirou!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token é inválido!'}), 401
        except Exception as e:
            return jsonify({'message': f'Erro ao processar token: {str(e)}'}), 500

        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.get('role') != 'admin':
            return jsonify({'message': 'Acesso restrito a administradores!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated