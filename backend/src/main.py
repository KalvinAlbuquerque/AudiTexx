# AudiTex/backend/src/main.py

from flask import Flask
from flask_cors import CORS
# Importações dos módulos core
from .core.config import Config
from .core.database import Database
from .api.tenable import TenableApi
import os # Importar os para construir o caminho

# Importação dos blueprints (rotas)
from .routes.scans import scans_bp
from .routes.lists import lists_bp
from .routes.reports import reports_bp
from .routes.vulnerabilities_manager import vulnerabilities_manager_bp

# Inicializa a configuração
config = Config("config.json") 

# Para manter a compatibilidade com o que já existia:
tenable_api = TenableApi() 

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], supports_credentials=True)

# Registro dos blueprints
app.register_blueprint(scans_bp)
app.register_blueprint(lists_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(vulnerabilities_manager_bp)

# CORREÇÃO AQUI: Servir a pasta de imagens estaticamente através do Flask
# O caminho é relativo à raiz do backend (AudiTex/backend/)
# A pasta base_report/assets está em AudiTex/shared_data/report_templates/base_report/assets
images_folder_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), # /home/kalvin/AudiTex/backend/src
    '..', # /home/kalvin/AudiTex/backend
    'shared_data', # /home/kalvin/AudiTex/shared_data
    'report_templates', # /home/kalvin/AudiTex/shared_data/report_templates
    'base_report', # /home/kalvin/AudiTex/shared_data/report_templates/base_report
    'assets' # /home/kalvin/AudiTex/shared_data/report_templates/base_report/assets
)

app.static_folder = images_folder_path # Define a pasta estática do Flask
app.static_url_path = '/backend_assets' # URL prefixo para acessar esses arquivos

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True, host='0.0.0.0', port=5000)