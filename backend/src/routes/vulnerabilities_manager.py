from flask import Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
import os
from werkzeug.utils import secure_filename # Importar secure_filename para segurança
import re # Adicionado: Importar regex para sanitização em sanitize_string
import unicodedata # Adicionado: Importar unicodedata para sanitização em sanitize_string

# Importa a classe Config do novo local
from ..core.config import Config
# Importa as funções de manipulação de JSON do novo módulo core
from ..core.json_utils import _load_data, _save_data, add_vulnerability, \
                             get_all_vulnerabilities, update_vulnerability, \
                             delete_vulnerability, _load_data_ # Corrigido: delete_vulnerabilidade
# Adicionado: Importa a nova função de sanitização
from ..core.utils import sanitize_string

# Inicializa a configuração
config = Config("config.json")

# Definir as extensões permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Garante que a pasta de upload de imagens exista
UPLOAD_BASE_DIR = os.path.join(config.caminho_report_templates_base, "assets")
os.makedirs(UPLOAD_BASE_DIR, exist_ok=True)

# Crie uma instância do Blueprint com o novo nome
vulnerabilities_manager_bp = Blueprint('vulnerabilities_manager', __name__, url_prefix='/vulnerabilities')

# --- Função Auxiliar para Obter o Caminho do Arquivo JSON ---
def _get_vuln_file_path(vuln_type: str):
    """Retorna o caminho do arquivo JSON com base no tipo de vulnerabilidade."""
    if vuln_type == "sites":
        return os.path.join(config.caminho_report_templates_descriptions, "vulnerabilities_webapp.json")
    elif vuln_type == "servers":
        return os.path.join(config.caminho_report_templates_descriptions, "vulnerabilities_servers.json")
    else:
        raise ValueError(f"Tipo de vulnerabilidade inválido: '{vuln_type}'. Use 'sites' ou 'servers'.")

# --- Função Auxiliar para Obter o Caminho do Arquivo Descritivo ---
def _get_descritivo_file_path(vuln_type: str):
    """Retorna o caminho do arquivo JSON descritivo com base no tipo de vulnerabilidade."""
    if vuln_type == "sites":
        return os.path.join(config.caminho_report_templates_descriptions, "descritivo_webapp.json")
    elif vuln_type == "servers":
        return os.path.join(config.caminho_report_templates_descriptions, "descritivo_servers.json")
    else:
        raise ValueError(f"Tipo de vulnerabilidade inválido para descritivo: '{vuln_type}'. Use 'sites' ou 'servers'.")

# --- Função Auxiliar para Verificar Extensão do Arquivo ---
def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Rota: Upload de Imagem (Ajustada) ---
@vulnerabilities_manager_bp.route('/uploadImage/', methods=['POST'])
def upload_image_api():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "Nenhum arquivo de imagem fornecido."}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({"error": "Nenhum arquivo selecionado para upload."}), 400

        if file and allowed_file(file.filename):
            category = request.form.get('categoria')
            subcategory = request.form.get('subcategoria')
            vulnerability_name_raw = request.form.get('vulnerabilidade')

            if not all([category, subcategory, vulnerability_name_raw]):
                return jsonify({"error": "Categoria, subcategoria e nome da vulnerabilidade são obrigatórios para o upload da imagem."}), 400

            sanitized_vulnerability_name_for_filename = sanitize_string(
                vulnerability_name_raw, remove_accents=True
            ).replace(' ', '-').lower()

            sanitized_category_for_path = sanitize_string(category, remove_accents=True).replace(' ', '-').lower()
            sanitized_subcategory_for_path = sanitize_string(subcategory, remove_accents=True).replace(' ', '-').lower()

            image_sub_path = os.path.join('images-was', sanitized_category_for_path, sanitized_subcategory_for_path)
            image_full_folder = os.path.join(UPLOAD_BASE_DIR, image_sub_path)

            os.makedirs(image_full_folder, exist_ok=True)

            file_extension = os.path.splitext(file.filename)[1].lower()

            final_filename = f"{sanitized_vulnerability_name_for_filename}{file_extension}"
            file_path = os.path.join(image_full_folder, final_filename)

            file.save(file_path)

            relative_image_path = os.path.join(image_sub_path, final_filename).replace(os.sep, '/')
            return jsonify({"message": "Imagem enviada com sucesso!", "imagePath": relative_image_path}), 200
        else:
            return jsonify({"error": "Tipo de arquivo não permitido. Apenas PNG, JPG, JPEG e GIF são aceitos."}), 400
    except Exception as e:
        print(f"Erro no upload_image_api: {e}")
        return jsonify({"error": f"Erro interno ao fazer upload da imagem: {str(e)}"}), 500

# --- Rota para obter categorias e subcategorias descritivas ---
@vulnerabilities_manager_bp.route('/getDescritivos/', methods=['GET'])
def get_descritivos_api():
    try:
        vuln_type = request.args.get('type')
        if not vuln_type:
            return jsonify({"error": "Parâmetro 'type' é obrigatório (sites ou servers)."}), 400

        file_path = _get_descritivo_file_path(vuln_type)
        full_data_from_file = _load_data_(file_path)

        if isinstance(full_data_from_file, dict) and "vulnerabilidades" in full_data_from_file:
            data_to_return = full_data_from_file.get("vulnerabilidades", [])
        elif isinstance(full_data_from_file, list):
            data_to_return = full_data_from_file
        else:
            print(f"Aviso: Conteúdo de '{file_path}' não é um dicionário com 'vulnerabilidades' ou uma lista. Retornando lista vazia.")
            data_to_return = []

        return jsonify(data_to_return), 200
    except ValueError as ve:
        print(f"ValueError em get_descritivos_api: {ve}")
        return jsonify({"error": str(ve)}), 400
    except FileNotFoundError:
        print(f"Erro: Arquivo descritivo não encontrado em {file_path}")
        return jsonify({"error": "Arquivo descritivo não encontrado."}), 404
    except Exception as e:
        print(f"Erro em get_descritivos_api: {e}")
        return jsonify({"error": str(e)}), 500

# --- Rotas Existentes (GET, POST, PUT, DELETE) ---

@vulnerabilities_manager_bp.route('/getVulnerabilidades/', methods=['GET'])
def get_all_vulnerabilities_api():
    try:
        vuln_type = request.args.get('type')
        if not vuln_type:
            return jsonify({"error": "Parâmetro 'type' é obrigatório (sites ou servers)."}), 400

        file_path = _get_vuln_file_path(vuln_type)
        data = get_all_vulnerabilities(file_path)
        return jsonify(data), 200
    except ValueError as ve:
        print(f"ValueError em get_all_vulnerabilities_api: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Erro em get_all_vulnerabilities_api: {e}")
        return jsonify({"error": str(e)}), 500

@vulnerabilities_manager_bp.route('/addVulnerabilidade/', methods=['POST'])
def add_vulnerability_api():
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({"error": "Dados não fornecidos."}), 400

        vuln_type = request_data.get('type')
        new_vuln_raw_data = request_data.get('data')

        if not vuln_type or not new_vuln_raw_data:
            return jsonify({"error": "Parâmetros 'type' e 'data' são obrigatórios no corpo da requisição."}), 400

        # --- Validação e Sanitização ---
        required_fields = ["Vulnerabilidade", "Categoria", "Subcategoria", "Descrição", "Solução"]
        for field in required_fields:
            if field not in new_vuln_raw_data or not new_vuln_raw_data[field]:
                return jsonify({"error": f"Campo '{field}' é obrigatório e não pode estar vazio."}), 400

        # Sanitizar todos os campos de string
        new_vuln_data_sanitized = {
            "Vulnerabilidade": sanitize_string(new_vuln_raw_data["Vulnerabilidade"], to_title_case=True),
            "Categoria": sanitize_string(new_vuln_raw_data["Categoria"], to_title_case=True),
            "Subcategoria": sanitize_string(new_vuln_raw_data["Subcategoria"], to_title_case=True),
            "Descrição": sanitize_string(new_vuln_raw_data["Descrição"]),
            "Solução": sanitize_string(new_vuln_raw_data["Solução"]),
            "Imagem": new_vuln_raw_data.get("Imagem", "") # Imagem já deve vir sanitizada pelo upload
        }

        # Validação extra para garantir que a sanitização não resultou em campos vazios essenciais
        for field in required_fields:
            if not new_vuln_data_sanitized[field]:
                return jsonify({"error": f"Campo '{field}' resultou vazio após sanitização. Verifique o conteúdo."}), 400

        file_path = _get_vuln_file_path(vuln_type)
        success, message = add_vulnerability(file_path, new_vuln_data_sanitized)

        if success:
            return jsonify({"message": message}), 201
        else:
            return jsonify({"error": message}), 409
    except ValueError as ve:
        print(f"ValueError em add_vulnerability_api: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Erro em add_vulnerability_api: {e}")
        return jsonify({"error": str(e)}), 500

@vulnerabilities_manager_bp.route('/updateVulnerabilidade/', methods=['PUT'])
def update_vulnerability_api():
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({"error": "Dados não fornecidos."}), 400

        vuln_type = request_data.get('type')
        old_name_raw = request_data.get('oldName')
        new_data_raw = request_data.get('data')

        if not vuln_type or not old_name_raw or not new_data_raw:
            return jsonify({"error": "Parâmetros 'type', 'oldName' e 'data' são obrigatórios no corpo da requisição."}), 400

        sanitized_old_name = sanitize_string(old_name_raw, to_title_case=True)

        updated_data_sanitized = {}
        for key, value in new_data_raw.items():
            if isinstance(value, str):
                if key in ["Vulnerabilidade", "Categoria", "Subcategoria"]:
                    updated_data_sanitized[key] = sanitize_string(value, to_title_case=True)
                else:
                    updated_data_sanitized[key] = sanitize_string(value)
            else:
                updated_data_sanitized[key] = value

        for field in ["Vulnerabilidade", "Categoria", "Subcategoria", "Descrição", "Solução"]:
            if field in updated_data_sanitized and not updated_data_sanitized[field]:
                return jsonify({"error": f"Campo '{field}' resultou vazio após sanitização. Verifique o conteúdo."}), 400

        file_path = _get_vuln_file_path(vuln_type)
        success, message = update_vulnerability(file_path, sanitized_old_name, updated_data_sanitized)

        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 404
    except ValueError as ve:
        print(f"ValueError em update_vulnerability_api: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Erro em update_vulnerability_api: {e}")
        return jsonify({"error": str(e)}), 500

@vulnerabilities_manager_bp.route('/deleteVulnerabilidade/', methods=['DELETE'])
def delete_vulnerability_api():
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({"error": "Dados não fornecidos."}), 400

        vuln_type = request_data.get('type')
        vuln_name_raw = request_data.get('name')

        if not vuln_type or not vuln_name_raw:
            return jsonify({"error": "Parâmetros 'type' e 'name' são obrigatórios no corpo da requisição."}), 400

        sanitized_vuln_name = sanitize_string(vuln_name_raw, to_title_case=True)

        file_path = _get_vuln_file_path(vuln_type)

        try:
            all_vulnerabilities = _load_data(file_path)
            vuln_to_delete = next((v for v in all_vulnerabilities if v.get("Vulnerabilidade") == sanitized_vuln_name), None)

            if vuln_to_delete and vuln_to_delete.get("Imagem"):
                relative_path_after_assets = vuln_to_delete["Imagem"].replace("assets/", "", 1)
                image_full_path = os.path.join(UPLOAD_BASE_DIR, relative_path_after_assets)

                if os.path.exists(image_full_path):
                    os.remove(image_full_path)
                    print(f"Imagem '{image_full_path}' deletada com sucesso.")
                else:
                    print(f"Aviso: Imagem '{image_full_path}' não encontrada no disco ao tentar deletar.")
            else:
                print(f"Nenhuma imagem associada ou vulnerabilidade '{sanitized_vuln_name}' não encontrada para deletar.")
        except Exception as img_e:
            print(f"Erro ao tentar deletar a imagem para '{sanitized_vuln_name}': {img_e}")

        success, message = delete_vulnerability(file_path, sanitized_vuln_name)

        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 404
    except ValueError as ve:
        print(f"ValueError em delete_vulnerability_api: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Erro em delete_vulnerability_api: {e}")
        return jsonify({"error": str(e)}), 500