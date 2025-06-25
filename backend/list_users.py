# backend/list_users.py

import sys
import os

# Adiciona o diretório 'src' ao path para importar a classe Database
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from core.database import Database


def list_users():
    db = Database()

    try:
        users = db.find('users', {})  # Busca todos os documentos da coleção 'users'
        print("Usuários encontrados no banco de dados:\n")

        for user in users:
            print(f"ID: {user.get('_id')}")
            print(f"Username: {user.get('username')}")
            print(f"Email: {user.get('email')}")
            print(f"Role: {user.get('role')}")
            print("-" * 60)

        if not users:
            print("Nenhum usuário encontrado.")

    except Exception as e:
        print(f"[ERRO] Falha ao listar usuários: {e}")
    finally:
        db.close()


if __name__ == '__main__':
    list_users()





