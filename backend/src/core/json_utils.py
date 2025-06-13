import json
import os

def carregar_json(caminho_arquivo_json: str) -> str:
    """
    Função para carregar o conteúdo de um arquivo JSON.
    """

    with open(caminho_arquivo_json, 'r', encoding="utf-8") as arquivo:
        return json.load(arquivo)

def carregar_json_utf(caminho_arquivo_json: str) -> str:
    """
    Função para carregar o conteúdo de um arquivo JSON com encoding UTF-8.
    """

    with open(caminho_arquivo_json, 'r', encoding='utf-8') as arquivo:
        return json.load(arquivo)

def salvar_json(caminho_arquivo_json:str, dados:str) -> None:
    """
    Função para salvar dados em um arquivo JSON.
    """
    with open(caminho_arquivo_json, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)


# --- Funções Auxiliares ---

def _load_data(file_path):
    """
    Carrega os dados das vulnerabilidades de um arquivo JSON.
    Cria o arquivo com uma lista vazia se não existir.
    """
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        print(f"Arquivo '{file_path}' criado, pois não existia.")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"Aviso: O conteúdo de '{file_path}' não é uma lista JSON. Retornando lista vazia.")
                return []
            return data
    except json.JSONDecodeError:
        print(f"Erro: Arquivo JSON '{file_path}' inválido ou vazio. Retornando lista vazia.")
        return []
    except Exception as e:
        print(f"Erro ao carregar dados do arquivo '{file_path}': {e}")
        return []

def _load_data_(file_path):
    """
    Carrega os dados de um arquivo JSON.
    Cria o arquivo com uma estrutura base se não existir.
    """
    is_descritivo_file = "descritivo_vulnerabilidades" in file_path or "descritivo_webapp" in file_path or "descritivo_servers" in file_path # Verifica se é um arquivo descritivo

    if not os.path.exists(file_path):
        initial_content = {"vulnerabilidades": []} if is_descritivo_file else []
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(initial_content, f, indent=4, ensure_ascii=False)
        print(f"Arquivo '{file_path}' criado, pois não existia, com a estrutura inicial.")
        return initial_content

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            if is_descritivo_file:
                if isinstance(data, dict) and "vulnerabilidades" in data:
                    return data
                else:
                    print(f"Aviso: O conteúdo de '{file_path}' não é um dicionário JSON com a chave 'vulnerabilidades'. Retornando estrutura vazia.")
                    return {"vulnerabilidades": []}
            else:
                if isinstance(data, list):
                    return data
                else:
                    print(f"Aviso: O conteúdo de '{file_path}' não é uma lista JSON. Retornando lista vazia.")
                    return []
    except json.JSONDecodeError:
        print(f"Erro: Arquivo JSON '{file_path}' inválido ou vazio. Retornando estrutura vazia.")
        return {"vulnerabilidades": []} if is_descritivo_file else []
    except Exception as e:
        print(f"Erro ao carregar dados do arquivo '{file_path}': {e}")
        return {"vulnerabilidades": []} if is_descritivo_file else []


def _save_data(file_path, data):
    """Salva os dados das vulnerabilidades de volta no arquivo JSON."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar dados no arquivo '{file_path}': {e}")

# --- C: Create (Criar) ---

def add_vulnerability(file_path, new_vuln_data):
    """
    Adiciona uma nova vulnerabilidade a um arquivo JSON.
    :param file_path: Caminho para o arquivo JSON.
    :param new_vuln_data: Um dicionário contendo os dados da nova vulnerabilidade.
    :return: (True, message) se adicionado, (False, error_message) caso contrário.
    """
    vulnerabilities = _load_data(file_path)

    if not isinstance(new_vuln_data, dict):
        return False, "A vulnerabilidade a ser adicionada deve ser um dicionário."

    vuln_name = new_vuln_data.get('Vulnerabilidade')
    if vuln_name is None or not vuln_name.strip():
        return False, "A vulnerabilidade não possui um campo 'Vulnerabilidade' válido."

    if any(v.get('Vulnerabilidade') == vuln_name for v in vulnerabilities):
        return False, f"Vulnerabilidade '{vuln_name}' já existe'."

    vulnerabilities.append(new_vuln_data)
    _save_data(file_path, vulnerabilities)
    return True, f"Vulnerabilidade '{vuln_name}' adicionada com sucesso'."

# --- R: Read (Ler) ---
def get_all_vulnerabilities(file_path):
    """
    Retorna todas as vulnerabilidades de um arquivo JSON.
    """
    return _load_data(file_path)

def find_vulnerability_by_name(file_path, vuln_name):
    """
    Encontra uma vulnerabilidade pelo seu nome em um arquivo JSON.
    """
    vulnerabilities = _load_data(file_path)
    for vuln in vulnerabilities:
        if vuln.get('Vulnerabilidade') == vuln_name:
            return vuln
    return None

def find_vulnerabilities_by_category(file_path, category_name):
    """
    Encontra vulnerabilidades por categoria em um arquivo JSON.
    """
    vulnerabilities = _load_data(file_path)
    found_vulns = []
    for vuln in vulnerabilities:
        if vuln.get('Categoria') == category_name:
            found_vulns.append(vuln)
    return found_vulns

# --- U: Update (Atualizar) ---

def update_vulnerability(file_path, old_vuln_name, new_data):
    """
    Atualiza uma vulnerabilidade existente em um arquivo JSON.
    """
    vulnerabilities = _load_data(file_path)
    updated = False
    message = f"Vulnerabilidade '{old_vuln_name}' não encontrada para atualização'."

    for i, vuln in enumerate(vulnerabilities):
        if vuln.get('Vulnerabilidade') == old_vuln_name:
            if 'Vulnerabilidade' in new_data and new_data['Vulnerabilidade'] != old_vuln_name:
                return False, "O nome da vulnerabilidade não pode ser alterado diretamente na atualização. Crie uma nova ou exclua e adicione novamente."

            vulnerabilities[i].update(new_data)
            updated = True
            message = f"Vulnerabilidade '{old_vuln_name}' atualizada com sucesso'."
            break

    if updated:
        _save_data(file_path, vulnerabilities)
        return True, message
    else:
        return False, message

# --- D: Delete (Deletar) ---

def delete_vulnerability(file_path, vuln_name): # Corrigido o nome da função aqui
    """
    Deleta uma vulnerabilidade pelo seu nome de um arquivo JSON.
    """
    vulnerabilities = _load_data(file_path)
    original_count = len(vulnerabilities)

    vulnerabilities = [v for v in vulnerabilities if v.get('Vulnerabilidade') != vuln_name]

    if len(vulnerabilities) < original_count:
        _save_data(file_path, vulnerabilities)
        return True, f"Vulnerabilidade '{vuln_name}' deletada com sucesso'."
    else:
        return False, f"Vulnerabilidade '{vuln_name}' não encontrada'."