# AudiTex/backend/src/main.py

from flask import Flask
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os

# Importações dos módulos core
# A inicialização da configuração e do banco de dados agora é feita
# diretamente nos módulos que precisam delas, como em `tenable.py`
from .api.tenable import tenable_api 

# Importação dos blueprints (rotas)
from .routes.scans import scans_bp
from .routes.lists import lists_bp
from .routes.reports import reports_bp
from .routes.vulnerabilities_manager import vulnerabilities_manager_bp
from .routes.api_key_manager import api_keys_bp 
from .routes.auth import auth_bp
from .routes.users import users_bp
# Inicializa a aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-dificil-de-adivinhar'

# Inicializa o Bcrypt
bcrypt = Bcrypt(app)
# Configura o CORS para permitir requisições do seu frontend
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], supports_credentials=True)

# Registro dos blueprints
app.register_blueprint(scans_bp)
app.register_blueprint(lists_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(vulnerabilities_manager_bp)
app.register_blueprint(api_keys_bp) 
app.register_blueprint(auth_bp) 
app.register_blueprint(users_bp)

# Define o caminho para a pasta de imagens estáticas para os relatórios
images_folder_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    '..', 
    'shared_data', 
    'report_templates', 
    'base_report', 
    'assets' 
)
app.static_folder = images_folder_path
app.static_url_path = '/backend_assets'

if __name__ == "__main__":
    print("Rotas registradas:")
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(debug=True, host='0.0.0.0', port=5000)