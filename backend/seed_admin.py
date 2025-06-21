# backend/seed_admin.py
import sys
import os
from flask_bcrypt import Bcrypt

# Adiciona o diretório 'src' ao path para que possamos importar 'Database'
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from core.database import Database

bcrypt = Bcrypt()

def seed_admin():
    print("Iniciando o seeding do usuário administrador...")
    db = Database()
    
    # Verifique se o admin já existe
    admin_user = db.find_one('users', {'username': 'admin'})
    if admin_user:
        print("Usuário 'admin' já existe. Nenhum novo usuário foi criado.")
        db.close()
        return

    # Crie o usuário admin se ele não existir
    # Lembre-se de usar uma senha forte em um ambiente real
    password = 'admin_password_123' 
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    db.insert_one('users', {
        'username': 'admin',
        'password': hashed_password,
        'role': 'admin'
    })
    
    print("Usuário 'admin' criado com sucesso!")
    db.close()

if __name__ == '__main__':
    seed_admin()
    
    
""" 
COMO USAR
Após iniciar seus contêineres com docker compose up -d, execute este script dentro do contêiner do backend:

docker compose exec backend python seed_admin.py
"""