# backend/src/routes/logs.py
from flask import Blueprint, request, jsonify
from ..core.database import Database
from ..auth.decorators import admin_required
from datetime import datetime, time

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

@logs_bp.route('', methods=['GET'])
@admin_required
def get_logs(current_user):
    """
    Endpoint para buscar logs com filtros e paginação.
    Acessível apenas por administradores.
    Query params: ?page=1&limit=20&username=fulano&action=create_user&date=2023-10-27
    """
    try:
        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit

        # Parâmetros de filtro
        username_filter = request.args.get('username')
        action_filter = request.args.get('action')
        date_filter_str = request.args.get('date')

        query = {}
        if username_filter:
            query['username'] = username_filter
        
        if action_filter:
            query['action'] = action_filter

        if date_filter_str:
            try:
                filter_date = datetime.strptime(date_filter_str, '%Y-%m-%d')
                start_of_day = datetime.combine(filter_date, time.min)
                end_of_day = datetime.combine(filter_date, time.max)
                query['timestamp'] = {'$gte': start_of_day, '$lte': end_of_day}
            except ValueError:
                return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD."}), 400

        db = Database()
        
        # Busca os logs com filtro, ordenação e paginação
        logs_cursor = db.find_with_pagination(
            collection='logs', 
            query=query, 
            skip=skip, 
            limit=limit,
            sort_by=[('timestamp', -1)] # -1 para ordem decrescente (mais recentes primeiro)
        )
        
        total_logs = db.count_documents('logs', query)
        
        logs_list = []
        for log in logs_cursor:
            log['_id'] = str(log['_id'])
            # Formata o timestamp para um formato padrão (ISO 8601)
            log['timestamp'] = log['timestamp'].isoformat()
            logs_list.append(log)

        db.close()
        
        return jsonify({
            "logs": logs_list,
            "total_pages": (total_logs + limit - 1) // limit, # Calcula o total de páginas
            "current_page": page,
            "total_records": total_logs
        }), 200

    except Exception as e:
        print(f"Erro ao buscar logs: {e}")
        return jsonify({"error": str(e)}), 500