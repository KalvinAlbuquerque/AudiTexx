import re
from flask import Blueprint, request, jsonify, send_file
from flask_cors import CORS, cross_origin
import os
from pathlib import Path
import shutil
from bson.objectid import ObjectId
import pandas as pd
import traceback 

# Importa a classe Config
from ..core.config import Config
# Importa o Database
from ..core.database import Database
# Importa as funções de processamento de dados
from ..data_processing.vulnerability_analyzer import processar_relatorio_csv, processar_relatorio_json, extrair_quantidades_vulnerabilidades_por_site
# Importa as funções de construção de relatório e compilação
from ..report_generation.report_builder import terminar_relatorio_preprocessado
from ..report_generation.latex_compiler import compilar_latex
from ..report_generation.plot_generator import gerar_Grafico_Quantitativo_Vulnerabilidades_Por_Site, gerar_grafico_donut, gerar_grafico_donut_webapp 

# Inicializa a configuração e o banco de dados
config = Config("config.json") 
db = Database() 

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/getRelatoriosGerados/', methods=['GET'])
def getRelatoriosGerados():
    try:
        db_instance = Database()
        relatorios = db_instance.find("relatorios")
        relatorios_list = []
        for relatorio in relatorios:
            relatorios_list.append({
                "nome": relatorio["nome"],
                "id": str(relatorio["_id"])
            })
        db_instance.close()
        return jsonify(relatorios_list), 200
    except Exception as e:
        print(f"Erro ao obter relatórios gerados: {e}")
        traceback.print_exc() 
        return jsonify({"error": str(e)}), 500

@reports_bp.route('/deleteRelatorio/<string:relatorio_id>', methods=['DELETE'])
def deleteRelatorio(relatorio_id):
    try:
        db_instance = Database()
        
        delete_result = db_instance.delete_one("relatorios", {"_id": db_instance.get_object_id(relatorio_id)})
        
        if delete_result.deleted_count == 0:
            db_instance.close()
            return jsonify({"message": "Relatório não encontrado no banco de dados."}), 404

        report_folder_path = Path(config.caminho_shared_relatorios) / relatorio_id
        
        if report_folder_path.exists() and report_folder_path.is_dir():
            shutil.rmtree(report_folder_path)
            print(f"DEBUG: Pasta do relatório excluída: {report_folder_path}")
        else:
            print(f"DEBUG: Pasta do relatório não encontrada ou não é um diretório: {report_folder_path}")

        db_instance.close()
        return jsonify({"message": "Relatório excluído com sucesso."}), 200

    except Exception as e:
        print(f"Erro ao excluir relatório {relatorio_id}: {str(e)}")
        traceback.print_exc() 
        return jsonify({"error": f"Erro interno ao excluir relatório: {str(e)}"}), 500

@reports_bp.route('/deleteAllRelatorios/', methods=['DELETE'])
def deleteAllRelatorios():
    try:
        db_instance = Database()
        
        all_relatorios = db_instance.find("relatorios")
        
        delete_db_result = db_instance.delete_many("relatorios", {})
        
        deleted_folders_count = 0
        for relatorio in all_relatorios:
            relatorio_id = str(relatorio["_id"])
            report_folder_path = Path(config.caminho_shared_relatorios) / relatorio_id
            
            if report_folder_path.exists() and report_folder_path.is_dir():
                try:
                    shutil.rmtree(report_folder_path)
                    deleted_folders_count += 1
                    print(f"DEBUG: Pasta {report_folder_path} excluída com sucesso.") 
                except Exception as folder_e: 
                    print(f"ATENÇÃO: Não foi possível excluir a pasta {report_folder_path}: {str(folder_e)}")
            else:
                print(f"DEBUG: Pasta {report_folder_path} não encontrada ou não é um diretório.")

        db_instance.close()
        return jsonify({
            "message": f"Todos os {delete_db_result.deleted_count} relatórios foram excluídos do banco de dados e {deleted_folders_count} pastas foram removidas do sistema de arquivos."
        }), 200

    except Exception as e:
        print(f"Erro ao excluir todos os relatórios: {str(e)}")
        traceback.print_exc() 
        return jsonify({"error": f"Erro interno ao excluir todos os relatórios: {str(e)}"}), 500

@reports_bp.route('/gerarRelatorioDeLista/', methods=['POST'])
def gerarRelatorioDeLista():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400

        id_lista = data.get("idLista")
        nome_secretaria = data.get("nomeSecretaria")
        sigla_secretaria = data.get("siglaSecretaria")
        data_inicio = data.get("dataInicio")
        data_fim = data.get("dataFim")
        ano = data.get("ano")
        mes = data.get("mes")
        google_drive_link = data.get("linkGoogleDrive")

        db_instance = Database()

        try:
            objeto_id = ObjectId(id_lista)
        except Exception:
            db_instance.close()
            return jsonify({"error": "ID de lista inválido."}), 400

        lista_doc = db_instance.find_one("listas", {"_id": objeto_id})

        if not lista_doc:
            db_instance.close()
            return jsonify({"error": "Lista não encontrada."}), 404

        criado_por_vm_scan = lista_doc.get("scanStoryIdCriadoPor", "Não informado")

        base_report_template_path = Path(config.caminho_report_templates_base)
        static_vm_donut_output_path = str(base_report_template_path / "assets" / "images-vmscan" / "total-vulnerabilidades-vm-donut.png")
        static_webapp_donut_output_path = str(base_report_template_path / "assets" / "images-was" / "total-vulnerabilidades-was-donut.png")
        static_webapp_x_site_output_path = str(base_report_template_path / "assets" / "images-was" / "vulnerabilidades-x-site.png")

        # Inicializa o ID do novo relatório e o destino de pré-processamento
        novo_relatorio_id = db_instance.insert_one(
            "relatorios",
            {"nome": nome_secretaria, "id_lista": id_lista, "destino_relatorio_preprocessado" : None}
        ).inserted_id

        pasta_destino_relatorio_temp_base = Path(config.caminho_shared_relatorios) / str(novo_relatorio_id) / "relatorio_preprocessado"
        pasta_destino_relatorio_temp_base.mkdir(parents=True, exist_ok=True)

        db_instance.update_one(
            "relatorios",
            {"_id": novo_relatorio_id},
            {"destino_relatorio_preprocessado": str(pasta_destino_relatorio_temp_base)}
        )

        # Processamento de WebApp Scans
        webapp_report_txt_path = pasta_destino_relatorio_temp_base / "Sites_agrupados_por_vulnerabilidades.txt"
        webapp_risk_counts = {'Critical': '0', 'High': '0', 'Medium': '0', 'Low': '0'}
        total_sites = '0'
        total_vulnerabilidades_web = '0'

        if lista_doc.get("pastas_scans_webapp") and os.path.exists(lista_doc["pastas_scans_webapp"]) and len(os.listdir(lista_doc["pastas_scans_webapp"])) > 0:
            pasta_scans_da_lista_webapp = lista_doc["pastas_scans_webapp"]
            processar_relatorio_json(pasta_scans_da_lista_webapp, str(pasta_destino_relatorio_temp_base))
            output_csv_path = str(pasta_destino_relatorio_temp_base / "vulnerabilidades_agrupadas_por_site.csv")
            extrair_quantidades_vulnerabilidades_por_site(output_csv_path, pasta_scans_da_lista_webapp)

            with open(webapp_report_txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                total_sites_match = re.search(r'Total de sites:\s*(\d+)', content)
                total_vulnerabilidades_web_match = re.search(r'Total de Vulnerabilidades:\s*(\d+)', content)
                critical_match = re.search(r'Critical:\s*(\d+)', content)
                high_match = re.search(r'High:\s*(\d+)', content)
                medium_match = re.search(r'Medium:\s*(\d+)', content)
                low_match = re.search(r'Low:\s*(\d+)', content)

                if total_sites_match: total_sites = total_sites_match.group(1)
                if total_vulnerabilidades_web_match: total_vulnerabilidades_web = total_vulnerabilidades_web_match.group(1)
                if critical_match: webapp_risk_counts['Critical'] = critical_match.group(1)
                if high_match: webapp_risk_counts['High'] = high_match.group(1)
                if medium_match: webapp_risk_counts['Medium'] = medium_match.group(1)
                if low_match: webapp_risk_counts['Low'] = low_match.group(1)

            webapp_risk_counts_int = {k: int(v) for k, v in webapp_risk_counts.items()}
            if not gerar_grafico_donut_webapp(webapp_risk_counts_int, static_webapp_donut_output_path):
                print(f"Aviso: Gráfico donut para WebApp não foi gerado (sem dados ou erro). O arquivo {static_webapp_donut_output_path} pode não existir.")

            gerar_Grafico_Quantitativo_Vulnerabilidades_Por_Site(
                str(pasta_destino_relatorio_temp_base / "vulnerabilidades_agrupadas_por_site.csv"),
                static_webapp_x_site_output_path,
                "descendente"
            )
            print(f"Gráfico (Vulnerabilidades por Site) salvo em: {static_webapp_x_site_output_path}")

        else:
            print(f"Aviso: Não há scans WebApp na pasta {lista_doc.get('pastas_scans_webapp')} ou a pasta está vazia. Pulando processamento WebApp.")
            pd.DataFrame(columns=['Site', 'Critical', 'High', 'Medium', 'Low', 'Total']).to_csv(str(pasta_destino_relatorio_temp_base / "vulnerabilidades_agrupadas_por_site.csv"), index=False)
            webapp_report_txt_path.touch()
            (pasta_destino_relatorio_temp_base / "(LATEX)Sites_agrupados_por_vulnerabilidades.txt").touch()

        # Processamento de Server Scans (VM)
        servers_report_txt_path = pasta_destino_relatorio_temp_base / "Servidores_agrupados_por_vulnerabilidades.txt"
        servers_risk_counts = {'critical': '0', 'high': '0', 'medium': '0', 'low': '0'}
        total_vulnerabilidade_vm = '0'

        # Verificação se o CSV de servidores existe na pasta de scans
        csv_servidor_path = None
        if lista_doc.get("pastas_scans_webapp"): # 'pastas_scans_webapp' é o diretório onde o CSV do VM scan é salvo
            csv_servidor_path = Path(lista_doc["pastas_scans_webapp"]) / "servidores_scan.csv"

        if lista_doc.get("historyid_scanservidor") and lista_doc.get("id_scan") and csv_servidor_path and csv_servidor_path.exists():
            pasta_scans_da_lista_vm = lista_doc["pastas_scans_webapp"]
            processar_relatorio_csv(pasta_scans_da_lista_vm, str(pasta_destino_relatorio_temp_base))

            with open(servers_report_txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                total_vulnerabilidade_vm_match = re.search(r'Total de Vulnerabilidades:\s*(\d+)', content)
                critical_match = re.search(r'Critical:\s*(\d+)', content)
                high_match = re.search(r'High:\s*(\d+)', content)
                medium_match = re.search(r'Medium:\s*(\d+)', content)
                low_match = re.search(r'Low:\s*(\d+)', content)

                if total_vulnerabilidade_vm_match: total_vulnerabilidade_vm = total_vulnerabilidade_vm_match.group(1)
                if critical_match: servers_risk_counts['critical'] = critical_match.group(1)
                if high_match: servers_risk_counts['high'] = high_match.group(1)
                if medium_match: servers_risk_counts['medium'] = medium_match.group(1)
                if low_match: servers_risk_counts['low'] = low_match.group(1)

            vm_risk_counts_int = {k: int(v) for k, v in servers_risk_counts.items()}
            if not gerar_grafico_donut(vm_risk_counts_int, static_vm_donut_output_path):
                print(f"Aviso: Gráfico donut para servidores não foi gerado (sem dados ou erro). O arquivo {static_vm_donut_output_path} pode não existir.")
        else:
            print("Aviso: Não há scans de Servidores associados a esta lista ou o arquivo CSV não foi encontrado. Pulando processamento de Servidores.")
            servers_report_txt_path.touch()
            (pasta_destino_relatorio_temp_base / "(LATEX)Servidores_agrupados_por_vulnerabilidades.txt").touch()

        pasta_final_latex = pasta_destino_relatorio_temp_base / "RelatorioPronto"

        total_vulnerabilidades_combinado = int(total_vulnerabilidades_web) + int(total_vulnerabilidade_vm)

        terminar_relatorio_preprocessado(
            nome_secretaria,
            sigla_secretaria,
            data_inicio,
            data_fim,
            ano,
            mes,
            str(pasta_destino_relatorio_temp_base),
            str(pasta_final_latex / "main.tex"),
            google_drive_link,
            total_vulnerabilidades_web,
            total_vulnerabilidade_vm,
            webapp_risk_counts['Critical'],
            webapp_risk_counts['High'],
            webapp_risk_counts['Medium'],
            webapp_risk_counts['Low'],
            servers_risk_counts['critical'],
            servers_risk_counts['high'],
            servers_risk_counts['medium'],
            servers_risk_counts['low'],
            total_sites,
            criado_por_vm_scan,
            static_vm_donut_output_path, # Passa o caminho completo da imagem gerada no template base
            static_webapp_donut_output_path, # Passa o caminho completo da imagem gerada no template base
            static_webapp_x_site_output_path # Passa o caminho completo da imagem gerada no template base
        )

        # NOVO: Chamar compilar_latex e verificar o status
        success, message = compilar_latex(os.path.join(str(pasta_final_latex), "main.tex"), str(pasta_final_latex))

        if not success:
            # Se a compilação falhou (incluindo erro de imagem), retorna um erro para o frontend
            db_instance.close()
            # Retorne um status 500 ou 400 dependendo da natureza do erro, e a mensagem detalhada.
            return jsonify({"error": f"Falha na geração do PDF: {message}"}), 500

        # Se a compilação foi bem-sucedida
        db_instance.update_one("listas", {"_id": objeto_id}, {"relatorioGerado": True})
        db_instance.close()

        return jsonify(str(novo_relatorio_id)), 200 # Retorna o ID do relatório gerado com sucesso

    except Exception as e:
        print(f"Erro ao gerar relatório de lista: {str(e)}")
        traceback.print_exc()
        if 'db_instance' in locals() and db_instance.client:
            db_instance.close()
        return jsonify({"error": f"Erro interno ao gerar relatório: {str(e)}"}), 500
    
    
@reports_bp.route('/baixarRelatorioPdf/', methods=['POST'])
def baixarRelatorioPdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
        
        relatorio_id = data.get("idRelatorio")
        if not relatorio_id:
            return jsonify({"error": "ID do relatório não fornecido."}), 400

        # Constrói o caminho completo para o PDF
        # O PDF está em: /app/shared_data/generated_reports/<relatorioId>/relatorio_preprocessado/RelatorioPronto/main.pdf
        pdf_path = Path(config.caminho_shared_relatorios) / relatorio_id / "relatorio_preprocessado" / "RelatorioPronto" / "main.pdf"

        if not pdf_path.exists():
            print(f"Erro: PDF não encontrado no caminho: {pdf_path}")
            return jsonify({"error": "PDF do relatório não encontrado."}), 404
        
        # Usa send_file para enviar o PDF
        return send_file(
            str(pdf_path),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Relatorio_Auditoria_{relatorio_id}.pdf"
        )
    except Exception as e:
        print(f"Erro ao baixar relatório PDF: {str(e)}")
        import traceback
        traceback.print_exc() # Imprime o traceback completo para depuração
        return jsonify({"error": f"Erro interno ao baixar o PDF: {str(e)}"}), 500
    
@reports_bp.route('/getRelatorioMissingVulnerabilities/', methods=['GET'])
def getRelatorioMissingVulnerabilities():
    try:
        relatorio_id = request.args.get('relatorioId')
        vuln_type = request.args.get('type') # 'sites' or 'servers'

        if not relatorio_id or not vuln_type:
            return jsonify({"error": "Parâmetros 'relatorioId' e 'type' são obrigatórios."}), 400

        # Constrói o nome do arquivo TXT com base no tipo
        if vuln_type == 'sites':
            filename = "vulnerabilidades_sites_ausentes.txt"
        elif vuln_type == 'servers':
            filename = "vulnerabilidades_servidores_ausentes.txt"
        else:
            return jsonify({"error": "Tipo de vulnerabilidade inválido. Use 'sites' ou 'servers'."}), 400

        # Constrói o caminho completo para o arquivo TXT
        # Os arquivos TXT são salvos em: /app/shared_data/generated_reports/<relatorioId>/relatorio_preprocessado/
        file_path = Path(config.caminho_shared_relatorios) / relatorio_id / "relatorio_preprocessado" / filename

        if not file_path.exists():
            # Se o arquivo não existir, significa que não há vulnerabilidades ausentes daquele tipo
            return jsonify({"content": []}), 200 # Retorna uma lista vazia, indicando que não há ausentes
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content_lines = [line.strip() for line in f if line.strip()] # Lê as linhas e remove vazias
        
        return jsonify({"content": content_lines}), 200

    except Exception as e:
        print(f"Erro ao obter vulnerabilidades ausentes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Erro interno ao buscar vulnerabilidades ausentes: {str(e)}"}), 500