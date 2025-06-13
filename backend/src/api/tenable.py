import httpx
import logging
import time
from src.core.database import Database

class TenableApi:
    """
    Classe singleton para interagir com a API do Tenable.io.
    Combina o carregamento de chaves do DB com a lógica de API específica da aplicação.
    """
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
        """Inicializa ou reinicializa o cliente HTTP com as chaves da API."""
        if not self.access_key or not self.secret_key:
            logging.warning("Cliente Tenable não pode ser inicializado sem chaves de API.")
            self.client = None
            return

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-ApiKeys": f"accessKey={self.access_key};secretKey={self.secret_key}"
        }
        
        # Aumentando o timeout para 60 segundos para operações longas.
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=60.0, verify=False)
        logging.info("Cliente HTTP para Tenable API foi inicializado.")

    def reload_client(self):
        """Recarrega a configuração do banco de dados e reinicializa o cliente."""
        logging.info("Recarregando cliente da API do Tenable...")
        self._load_config()
        self._initialize_client()
        logging.info("Cliente da API do Tenable recarregado com sucesso.")
        
    def _make_request(self, method, endpoint, **kwargs):
        """Método auxiliar para fazer requisições de forma robusta."""
        if not self.client:
            logging.error("Cliente Tenable não inicializado. Verifique as chaves da API.")
            return {"error": "API keys not configured"}

        try:
            response = self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            
            if not response.content:
                return {"status": "success", "message": "Operation completed with no content."}

            return response.json()
            
        except httpx.HTTPStatusError as e:
            logging.error(f"Erro de status HTTP para {e.request.url}: {e.response.status_code} - {e.response.text}")
            try:
                return e.response.json()
            except Exception:
                return {"error": f"HTTP {e.response.status_code}", "message": e.response.text}
        except Exception as e:
            logging.error(f"Erro inesperado ao fazer requisição para {endpoint}: {str(e)}")
            return {"error": "Unexpected API error", "message": str(e)}

    # --- Métodos adaptados da sua implementação ---

    def get_web_app_scans_from_folder_of_user(self, folder_name: str, user_name: str):
        """
        Obtém os scans de aplicação web de uma pasta específica para um dado usuário,
        utilizando o header X-Impersonate.
        """
        if not self.client:
             return {"error": "API keys not configured"}

        logging.info(f"Buscando scans na pasta '{folder_name}' para o usuário '{user_name}'")

        headers_impersonate = self.client.headers.copy()
        headers_impersonate['X-Impersonate'] = f"username={user_name}"
        
        url = "/was/v2/configs/search"
        payload = {
            "field": "folder_name",
            "operator": "match",
            "value": folder_name,
        }
        params = {"limit": 200}

        scans = self._make_request("POST", url, headers=headers_impersonate, json=payload, params=params)
        
        if scans and isinstance(scans, dict) and scans.get("pagination", {}).get("total", 0) > 200:
            logging.info("Múltiplas páginas de scans encontradas, buscando todas...")
            # A lógica de paginação pode ser adicionada aqui se necessário.
            pass

        return scans if isinstance(scans, dict) else {"error": "Invalid response from Tenable API", "data": scans}

    def get_vm_scans_from_folder_of_user(self, folder_name: str, username: str):
        """Busca scans de VM. Esta lógica permanece a mesma, pois não usa X-Impersonate."""
        response = self._make_request("GET", "/folders")
        folder_id = None
        if response and "folders" in response:
            for folder in response["folders"]:
                if folder["name"] == folder_name:
                    folder_id = folder["id"]
                    break
        
        if not folder_id:
            logging.warning(f"Pasta de VM '{folder_name}' não encontrada.")
            return []

        logging.info(f"Buscando scans de VM na pasta ID: {folder_id}")
        scan_response = self._make_request("GET", f"/scans?folder_id={folder_id}")
        return scan_response.get("scans", []) if scan_response else []

    def get_vm_scan_by_name(self, scan_name: str):
        """
        Obtém os detalhes de um scan de Vulnerability Management (VM) pelo nome.
        """
        logging.info(f"Buscando scan de VM com o nome: {scan_name}")
        response = self._make_request("GET", "/scans")
        
        if response and isinstance(response, dict) and "scans" in response:
            for scan in response["scans"]:
                if scan.get("name") == scan_name:
                    logging.info(f"Scan de VM '{scan_name}' encontrado.")
                    return scan 
        
        logging.warning(f"Scan de VM com nome '{scan_name}' não foi encontrado.")
        return {"error": "Scan not found", "name": scan_name}

    def download_scans_results_json(self, scan_config: dict):
        """
        Baixa os resultados do último scan de uma configuração de WebApp.
        Recebe o dicionário de configuração do scan.
        """
        last_scan_info = scan_config.get("last_scan")
        if not last_scan_info or "scan_id" not in last_scan_info:
            logging.warning(f"Configuração de scan {scan_config.get('config_id')} não possui um último scan ('last_scan').")
            return {"error": "No last scan found for this configuration."}
        
        scan_id = last_scan_info["scan_id"]
        logging.info(f"Iniciando download para o scan de WAS ID: {scan_id}")

        # Endpoint direto para vulnerabilidades (mais eficiente que gerar relatório)
        return self._make_request("GET", f"/was/v2/scans/{scan_id}/vulnerabilities")

    def download_vmscans_csv(self, scan_id: int, history_id: int = None):
        """
        Baixa os resultados de um scan de VM em formato CSV.
        Se history_id for fornecido, baixa essa execução específica.
        """
        export_payload = {"format": "csv", "chapters": "vuln_by_host"}
        
        if history_id:
            export_payload["history_id"] = history_id
            logging.info(f"Iniciando exportação CSV para o histórico {history_id} do scan de VM ID: {scan_id}")
        else:
            logging.info(f"Iniciando exportação CSV para a última execução do scan de VM ID: {scan_id}")

        export_request = self._make_request("POST", f"/scans/{scan_id}/export", json=export_payload)
        
        if not isinstance(export_request, dict) or "export_uuid" not in export_request:
            logging.error(f"Falha ao iniciar a exportação do scan. Resposta: {export_request}")
            return None
        
        export_uuid = export_request["export_uuid"]
        logging.info(f"Exportação iniciada com UUID: {export_uuid}")

        for i in range(15): 
            status_response = self._make_request("GET", f"/scans/{scan_id}/export/{export_uuid}/status")
            if isinstance(status_response, dict) and status_response.get("status") == "ready":
                logging.info("Exportação pronta. Baixando o arquivo...")
                # Para download de CSV, o conteúdo é texto, não JSON
                download_response = self.client.request("GET", f"/scans/{scan_id}/export/{export_uuid}/download")
                download_response.raise_for_status()
                return download_response.text
            
            logging.info(f"Aguardando a exportação ficar pronta... (tentativa {i+1}/15)")
            time.sleep(10)

        logging.error(f"A exportação para o scan {scan_id} não ficou pronta a tempo (timeout).")
        return None

# Instância singleton que será usada em toda a aplicação
tenable_api = TenableApi()