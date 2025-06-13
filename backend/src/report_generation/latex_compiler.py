# backend/src/report_generation/latex_compiler.py (Modificar)

import subprocess
import os
from pathlib import Path
import sys
import re # Importar regex para análise de logs

def compilar_latex(caminho_main_tex: str, diretorio_saida: str):
    """
    Compila um arquivo LaTeX (.tex) para gerar um PDF e verifica erros comuns.

    Args:
        caminho_main_tex (str): O caminho completo para o arquivo main.tex.
        diretorio_saida (str): O diretório onde o PDF e outros arquivos de saída serão gerados.
    
    Returns:
        bool: True se a compilação foi bem-sucedida, False caso contrário.
        str: Mensagem de sucesso ou de erro detalhada.
    """
    try:
        Path(diretorio_saida).mkdir(parents=True, exist_ok=True)
        main_tex_filename = Path(caminho_main_tex).name

        preambulo_path = Path(diretorio_saida) / "preambulo.tex"
        if not preambulo_path.exists():
            return False, f"Erro: Arquivo '{preambulo_path}' não encontrado no diretório de saída. Verifique se foi copiado corretamente do template."

        command = [
            'pdflatex',
            '-interaction=nonstopmode',
            '-output-directory', diretorio_saida,
            main_tex_filename
        ]

        full_log_output = ""

        # Primeira passada
        print(f"Executando primeira passada do pdflatex em {diretorio_saida}...")
        result_1 = subprocess.run(
            command,
            capture_output=True,
            encoding='latin-1', # Usar latin-1 ou utf-8, dependendo da codificação real da saída do pdflatex
            check=False,
            cwd=diretorio_saida
        )
        full_log_output += result_1.stdout
        if result_1.stderr:
            full_log_output += result_1.stderr

        print("\n--- SAÍDA DO PDFLATEX (PRIMEIRA PASSADA) ---")
        print(result_1.stdout)
        if result_1.stderr:
            print(result_1.stderr)
        print("--- FIM SAÍDA DO PDFLATEX (PRIMEIRA PASSADA) ---\n")

        # Segunda passada
        print(f"Executando segunda passada do pdflatex em {diretorio_saida}...")
        result_2 = subprocess.run(
            command,
            capture_output=True,
            encoding='latin-1',
            check=False,
            cwd=diretorio_saida
        )
        full_log_output += result_2.stdout
        if result_2.stderr:
            full_log_output += result_2.stderr

        print("\n--- SAÍDA DO PDFLATEX (SEGUNDA PASSADA) ---")
        print(result_2.stdout)
        if result_2.stderr:
            print(result_2.stderr)
        print("--- FIM SAÍDA DO PDFLATEX (SEGUNDA PASSADA) ---\n")

        # Análise dos logs para erros específicos
        # Padrões de regex para erros de imagem (sensíveis à saída do pdflatex)
        # Exemplo: `! LaTeX Error: File `assets/images-was/missing-image.png' not found.`
        # Exemplo: `! Package pdftex.def Error: File `assets/images-was/another.png' not found: using draft setting.`
        image_error_pattern = re.compile(
            r"!(?: LaTeX)? Error: (?:File `(?P<filename>[^']+)' not found|Package .+\.def Error: File `(?P<filename>[^']+)' not found)",
            re.IGNORECASE
        )
        
        image_errors = []
        for line in full_log_output.splitlines():
            match = image_error_pattern.search(line)
            if match:
                filename = match.group("filename")
                image_errors.append(filename)

        if image_errors:
            error_message = "Erro de compilação: Imagens não encontradas no relatório LaTeX. Por favor, verifique as seguintes imagens e certifique-se de que estão presentes e com o nome correto: "
            error_message += ", ".join(image_errors)
            return False, error_message

        # Verificação do código de retorno final (se não houver erros específicos de imagem)
        if result_2.returncode != 0:
            return False, f"Erro na compilação LaTeX. Código de retorno: {result_2.returncode}. Verifique os logs do backend para detalhes."
        else:
            pdf_path = Path(diretorio_saida) / main_tex_filename.replace('.tex', '.pdf')
            if not pdf_path.exists():
                return False, f"AVISO: pdflatex retornou 0, mas o PDF '{pdf_path.name}' NÃO foi encontrado em '{diretorio_saida}'. Isso pode indicar um problema de permissão ou compilação inválida."
            else:
                return True, f"PDF compilado com sucesso em: {pdf_path}"

    except FileNotFoundError as fnf_e:
        return False, f"Erro: Comando 'pdflatex' não encontrado. Certifique-se de que o LaTeX está instalado e configurado no PATH do sistema. Detalhes: {fnf_e}"
    except Exception as e:
        return False, f"Erro inesperado durante a compilação LaTeX: {str(e)}"