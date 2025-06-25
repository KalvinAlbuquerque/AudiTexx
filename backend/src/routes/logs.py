from flask import Blueprint, request, jsonify, Response
from datetime import datetime, time

# Importações corrigidas para usar as instâncias e funções compartilhadas do projeto
from src.core.database import Database
from src.core.json_utils import dumps
from src.core.logger import log_action
from src.auth.decorators import admin_required

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

@logs_bp.route('', methods=['GET'])
@admin_required
def get_logs(current_user):
    """
    Endpoint para buscar logs com filtros e paginação.
    Acessível apenas por administradores.
    """
    db_connection = None  # Inicializa a variável para garantir que ela exista no bloco 'finally'
    try:
        # 3. Cria uma instância do banco de dados no início da função
        db_connection = Database()

        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit

        # Parâmetros de filtro
        query = {}
        username_filter = request.args.get('username')
        if username_filter:
            query['username'] = username_filter
        
        action_filter = request.args.get('action')
        if action_filter:
            query['action'] = action_filter

        date_filter_str = request.args.get('date')
        if date_filter_str:
            try:
                filter_date = datetime.strptime(date_filter_str, '%Y-%m-%d')
                start_of_day = datetime.combine(filter_date, time.min)
                end_of_day = datetime.combine(filter_date, time.max)
                query['timestamp'] = {'$gte': start_of_day, '$lte': end_of_day}
            except ValueError:
                return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD."}), 400

        # 4. Chama a função de paginação com os parâmetros corretos
        #    Corrigido de 'collection' para 'collection_name' para corresponder à sua classe Database
        logs_cursor = db_connection.find_with_pagination(
            collection_name='logs', 
            query=query, 
            skip=skip, 
            limit=limit,
            sort_by=[('timestamp', -1)]
        )
        
        # Busca o total de documentos para calcular o número de páginas
        total_logs = db_connection.count_documents('logs', query)
        
        # Converte os resultados para uma lista, formatando os campos necessários
        logs_list = []
        for log in logs_cursor:
            log['_id'] = str(log['_id'])
            log['timestamp'] = log['timestamp'].isoformat()
            logs_list.append(log)
        
        return jsonify({
            "logs": logs_list,
            "total_pages": (total_logs + limit - 1) // limit,
            "current_page": page,
            "total_records": total_logs
        }), 200

    except Exception as e:
        print(f"Erro ao buscar logs: {e}")
        return jsonify({"error": "Ocorreu um erro interno ao processar a solicitação."}), 500
    
    finally:
        # 5. Garante que a conexão com o banco seja fechada no final, mesmo se ocorrer um erro
        if db_connection:
            db_connection.close()
