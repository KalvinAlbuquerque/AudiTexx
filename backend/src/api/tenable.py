# backend/src/api/tenable.py

import httpx
import logging
from src.core.database import Database

class TenableApi:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TenableApi, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.base_url = "https://cloud.tenable.com"
        self.access_key = None
        self.secret_key = None
        self.client = None
        
        self._load_config()
        self._initialize_client()

        self._initialized = True
        logging.info("Tenable API client inicializado.")

    def _load_config(self):
        """Carrega as chaves da API do banco de dados."""
        try:
            db = Database()
            # Correção: usar db.db.configs em vez de db.configs
            config = db.db.configs.find_one({"name": "tenable_api_keys"})
            if config:
                self.access_key = config.get("TENABLE_ACCESS_KEY")
                self.secret_key = config.get("TENABLE_SECRET_KEY")
                logging.info("Chaves da API do Tenable carregadas do banco de dados.")
            else:
                logging.warning("Configuração 'tenable_api_keys' não encontrada no banco de dados.")
        except Exception as e:
            logging.error(f"Erro ao carregar chaves da API do Tenable do banco de dados: {e}")
    def _initialize_client(self):
        """Inicializa o cliente HTTP com as chaves atuais."""
        if self.access_key and self.secret_key:
            headers = {
                "X-ApiKeys": f"accessKey={self.access_key};secretKey={self.secret_key}",
                "Content-Type": "application/json"
            }
            self.client = httpx.Client(base_url=self.base_url, headers=headers)
        else:
            self.client = httpx.Client(base_url=self.base_url)
            logging.warning("Cliente Tenable inicializado sem chaves de API.")

    def reload_client(self):
        """Recarrega a configuração do banco de dados e reinicializa o cliente."""
        logging.info("Recarregando cliente da API do Tenable...")
        self._load_config()
        self._initialize_client()
        logging.info("Cliente da API do Tenable recarregado com sucesso.")

    def get_scans(self, last_modification_date=None):
        if not self.client:
            logging.error("Cliente Tenable não inicializado.")
            return None
        
        endpoint = "/scans"
        params = {}
        if last_modification_date:
            params['last_modification_date'] = int(last_modification_date.timestamp())

        try:
            response = self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"Erro na requisição para a API do Tenable: {e.response.text}")
            return None

# Singleton instance
tenable_api = TenableApi()