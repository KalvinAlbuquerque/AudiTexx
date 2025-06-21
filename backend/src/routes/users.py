# backend/src/routes/users.py

from flask import Blueprint, request, jsonify
from ..core.database import Database
from ..auth.decorators import admin_required
from flask_bcrypt import Bcrypt

users_bp = Blueprint('users', __name__, url_prefix='/users')
bcrypt = Bcrypt()

# Rota para criar um novo usuário (somente admin)
@users_bp.route('/', methods=['POST'])
@admin_required
def create_user(current_user):
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('role') or not data.get('email'):
        return jsonify({'error': 'Dados incompletos: username, password, email e role são obrigatórios'}), 400

    if data['role'] not in ['admin', 'user']:
        return jsonify({'error': 'Role inválido. Use "admin" ou "user"'}), 400
        
    db = Database()

    # Verifica se o usuário ou email já existe
    if db.find_one('users', {'username': data['username']}):
        db.close()
        return jsonify({'error': 'Nome de usuário já existe'}), 409
    
    if db.find_one('users', {'email': data['email']}):
        db.close()
        return jsonify({'error': 'Email já cadastrado'}), 409

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    new_user = {
        'username': data['username'],
        'email': data['email'],
        'password': hashed_password,
        'role': data['role']
    }
    
    db.insert_one('users', new_user)
    db.close()
    
    return jsonify({'message': 'Novo usuário criado com sucesso!'}), 201

# Rota para listar todos os usuários (somente admin)
@users_bp.route('/', methods=['GET'])
@admin_required
def get_all_users(current_user):
    db = Database()
    users = db.find('users')
    db.close()
    
    output = []
    for user in users:
        user_data = {
            'public_id': str(user['_id']),
            'username': user['username'],
            'email': user.get('email', 'N/A'),
            'role': user['role']
        }
        output.append(user_data)
        
    return jsonify({'users': output})

# Rota para deletar um usuário (somente admin)
@users_bp.route('/<public_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user, public_id):
    db = Database()
    
    # Previne que o admin se auto-delete
    if str(current_user['_id']) == public_id:
        db.close()
        return jsonify({'error': 'Administrador não pode se auto-deletar'}), 403

    user_to_delete = db.find_one('users', {'_id': db.get_object_id(public_id)})
    if not user_to_delete:
        db.close()
        return jsonify({'error': 'Usuário não encontrado'}), 404

    db.delete_one('users', {'_id': db.get_object_id(public_id)})
    db.close()
    
    return jsonify({'message': 'Usuário foi deletado com sucesso!'})


# Rota para atualizar a senha de um usuário (somente admin)
@users_bp.route('/<public_id>', methods=['PUT'])
@admin_required
def update_user(current_user, public_id):
    data = request.get_json()
    if not data or not data.get('password'):
        return jsonify({'error': 'A nova senha é obrigatória'}), 400

    db = Database()
    
    user_to_update = db.find_one('users', {'_id': db.get_object_id(public_id)})
    if not user_to_update:
        db.close()
        return jsonify({'error': 'Usuário não encontrado'}), 404

    if str(current_user['_id']) == public_id:
        db.close()
        return jsonify({'error': 'Ação não permitida.'}), 403

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # CORREÇÃO: Removido o operador '$set'.
    # A função db.update_one já adiciona o '$set' internamente.
    # Apenas o dicionário com os campos a serem atualizados deve ser passado.
    update_data = {'password': hashed_password}
    
    db.update_one(
        'users',
        {'_id': db.get_object_id(public_id)},
        update_data
    )
    db.close()

    return jsonify({'message': 'Senha do usuário atualizada com sucesso!'})
