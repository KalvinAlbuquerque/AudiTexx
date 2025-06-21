# backend/src/core/logger.py
from datetime import datetime
from .database import Database

def log_action(user: dict, action: str, details: dict):
    """
    Registra uma ação do usuário no banco de dados.

    :param user: O objeto do usuário que realizou a ação (deve conter _id e username).
    :param action: Uma string descrevendo a ação (ex: 'generate_report').
    :param details: Um dicionário com detalhes relevantes sobre a ação.
    """
    try:
        db = Database()
        log_entry = {
            "user_id": user['_id'],
            "username": user['username'],
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow()
        }
        db.insert_one("logs", log_entry)
        db.close()
    except Exception as e:
        # Imprime o erro no console do backend, mas não interrompe a requisição principal.
        print(f"ERRO AO REGISTRAR LOG: {e}")