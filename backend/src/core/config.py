import json
import os
from dotenv import load_dotenv

class Config:
    _instance = None
    _inicializado = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, arquivo_config: str):
        if not self._inicializado:
            # Carrega variáveis de ambiente de um arquivo .env no diretório do backend (credentials.env)
            load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'credentials.env')) 

            if arquivo_config is None:
                raise ValueError("arquivo_config deve ser fornecido na primeira inicialização.")

            config_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', arquivo_config)

            try:
                with open(config_json_path, 'r', encoding='utf-8') as f:
                    self._config_data = json.load(f)
            except FileNotFoundError:
                raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_json_path}")
            except json.JSONDecodeError:
                raise ValueError(f"Arquivo de configuração inválido (JSON malformado): {config_json_path}")

            self._inicializado = True

        self._arquivo_config = self._config_data

        # Prioriza variáveis de ambiente, com fallback para o config.json
        self._caminho_shared_relatorios = os.getenv('CAMINHO_SHARED_RELATORIOS', self._arquivo_config["caminho_shared_relatorios"])
        self._caminho_shared_jsons = os.getenv('CAMINHO_SHARED_JSONS', self._arquivo_config["caminho_shared_jsons"])
        self._caminho_report_templates_base = os.getenv('CAMINHO_REPORT_TEMPLATES_BASE', self._arquivo_config["caminho_report_templates_base"])
        self._caminho_report_templates_descriptions = os.getenv('CAMINHO_REPORT_TEMPLATES_DESCRIPTIONS', self._arquivo_config["caminho_report_templates_descriptions"])

    @property
    def caminho_shared_relatorios(self) -> str:
        return self._caminho_shared_relatorios

    @property
    def caminho_shared_jsons(self) -> str:
        return self._caminho_shared_jsons

    @property
    def caminho_report_templates_base(self) -> str:
        return self._caminho_report_templates_base

    @property
    def caminho_report_templates_descriptions(self) -> str:
        return self._caminho_report_templates_descriptions