import os
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

    def download_scans_results_json(self, target_dir: str, scans: dict) -> None:
        """
        Baixa os resultados dos scans de aplicação web para o diretório especificado.
        Args:
            target_dir (str): O caminho do diretório onde os arquivos JSON serão salvos.
            scans (dict): O dicionário completo retornado pela API do Tenable (contendo a chave 'items').
        """
        if not self.client:
            logging.error("Cliente Tenable não inicializado. Não é possível baixar scans.")
            return

        if not isinstance(scans, dict) or "items" not in scans:
            logging.error(f"Formato inválido para 'scans' em download_scans_results_json. Esperado um dicionário com a chave 'items'. Recebido: {type(scans)}")
            return

        scans_list = scans["items"]
        
        os.makedirs(target_dir, exist_ok=True)
        logging.info(f"Diretório de destino '{target_dir}' garantido.")

        for data in scans_list:
            if not isinstance(data, dict):
                logging.warning(f"Item inesperado na lista de scans: {data}. Ignorando.")
                continue

            last_scan_info = data.get("last_scan")
            if not last_scan_info or "scan_id" not in last_scan_info:
                logging.warning(f"Configuração de scan {data.get('config_id')} não possui um último scan ('last_scan') ou 'scan_id'. Pulando download.")
                continue

            scan_id = last_scan_info["scan_id"]
            logging.info(f"Iniciando processo de download para WAS scan ID: {scan_id}")

            url_init_report = f"/was/v2/scans/{scan_id}/report"
            url_get_report = f"/was/v2/scans/{scan_id}/report" # A URL para GET é a mesma

            try:
                # 1. Iniciar a geração do relatório
                response_put = self.client.put(url_init_report)
                response_put.raise_for_status()
                logging.info(f"Geração de relatório iniciada para scan {scan_id}. Status: {response_put.status_code}")

                # 2. Baixar o relatório
                response_get = self.client.get(url_get_report)
                response_get.raise_for_status()
                logging.info(f"Relatório obtido para scan {scan_id}. Status: {response_get.status_code}")

                # 3. Salvar os dados do scan
                file_path = os.path.join(target_dir, f"{scan_id}.json")
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(response_get.text)
                logging.info(f"Scan {scan_id} salvo com sucesso em {file_path}")

            except httpx.HTTPStatusError as e:
                logging.error(f"Erro HTTP ao baixar scan {scan_id}: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                logging.error(f"Erro inesperado ao processar scan {scan_id}: {str(e)}")


    def download_vmscans_csv(self, target_dir: str, id_scan: str, history_id: str = None) -> None:
            """
            Baixa os resultados de um scan de VM em formato CSV.
            Usa o 'file' retornado pela API para rastrear o download.
            Args:
                target_dir (str): O caminho do diretório onde o arquivo CSV será salvo.
                id_scan (str): O ID do scan VM.
                history_id (str, optional): O ID do histórico do scan, se aplicável.
            """
            if not self.client:
                logging.error("Cliente Tenable não inicializado. Não é possível baixar scans VM.")
                return

            url_export_init = f"/scans/{id_scan}/export"
            export_payload = {
                "format": "csv",
                "chapters": "vuln_by_host"
            }
            if history_id:
                export_payload["history_id"] = history_id
                logging.info(f"Iniciando exportação CSV para o histórico {history_id} do scan de VM ID: {id_scan}")
            else:
                logging.info(f"Iniciando exportação CSV para a última execução do scan de VM ID: {id_scan}")

            try:
                # 1. Iniciar a exportação e obter o 'file' ID
                # Usando client.post diretamente para ter mais controle sobre a resposta bruta se _make_request for muito genérico
                response = self.client.post(url_export_init, json=export_payload)
                response.raise_for_status() # Levanta um erro para status codes 4xx/5xx
                export_response = response.json()
                
                if not isinstance(export_response, dict) or "file" not in export_response:
                    logging.error(f"Falha ao iniciar a exportação do scan {id_scan}. Resposta inesperada: {export_response}")
                    return

                file_id = export_response["file"]
                logging.info(f"Exportação iniciada para scan {id_scan} com File ID: {file_id}")

                # 2. Polling para verificar o status do download
                url_status = f"/scans/{id_scan}/export/{file_id}/status"
                for i in range(30): # Aumentado o número de tentativas
                    status_check_response = self.client.get(url_status).json() # Chamada direta
                    
                    if isinstance(status_check_response, dict) and status_check_response.get("status") == "ready":
                        logging.info(f"Exportação para scan {id_scan} está pronta. Baixando o arquivo...")
                        break
                    
                    logging.info(f"Aguardando a exportação para scan {id_scan} ficar pronta... (tentativa {i+1}/30)")
                    time.sleep(5) # Espera 5 segundos entre as verificações
                else:
                    logging.error(f"A exportação para o scan {id_scan} não ficou pronta a tempo (timeout após 150s).")
                    return

                # 3. Baixar o arquivo CSV
                url_download = f"/scans/{id_scan}/export/{file_id}/download"
                download_response = self.client.get(url_download)
                download_response.raise_for_status() # Lança erro para status HTTP 4xx/5xx

                # Salvar o conteúdo CSV no arquivo
                os.makedirs(target_dir, exist_ok=True)
                file_path = os.path.join(target_dir, f"vm_scan_{id_scan}.csv")
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(download_response.text)
                logging.info(f"Scan VM {id_scan} baixado com sucesso para {file_path}")

            except httpx.HTTPStatusError as e:
                logging.error(f"Erro HTTP ao baixar scan VM {id_scan}: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                logging.error(f"Erro inesperado ao processar download de scan VM {id_scan}: {str(e)}")

# Instância singleton que será usada em toda a aplicação
tenable_api = TenableApi()