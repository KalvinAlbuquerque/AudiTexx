import pandas as pd
import matplotlib.pyplot as plt
import os # Importar os para usar os.makedirs

def gerar_Grafico_Quantitativo_Vulnerabilidades_Por_Site(input_file: str, graph_output_path: str, ordem: str = "descendente"):
    """
    Gera um gráfico de barras do quantitativo de vulnerabilidades por site e salva em um arquivo PNG.

    Args:
        input_file (str): Caminho do arquivo de entrada CSV (vulnerabilidades_agrupadas_por_site.csv).
        graph_output_path (str): Caminho para salvar o arquivo PNG do gráfico.
        ordem (str): Ordem de classificação ('descendente' ou 'crescente').
    """
    try:
        # Carrega os dados do CSV em um DataFrame
        df = pd.read_csv(input_file)

        # Define se a ordenação será crescente ou decrescente
        ordem_crescente = True if ordem.lower() == "crescente" else False

        # Ordena os dados pela coluna 'Total' conforme especificado
        df_sorted = df.sort_values(by='Total', ascending=ordem_crescente)

        # Cria o diretório de saída se não existir
        output_dir = os.path.dirname(graph_output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Configura o gráfico
        plt.figure(figsize=(20, 10))
        plt.bar(df_sorted['Site'], df_sorted['Total'], color='skyblue')

        # Adiciona títulos e rótulos
        plt.title('Quantitativo de Vulnerabilidades por Site', fontsize=18)
        plt.xlabel('Sites', fontsize=16)
        plt.ylabel('Total de Vulnerabilidades', fontsize=16)

        plt.xticks(rotation=45, ha='right', fontsize=13)  # Rótulos a 45 graus e alinhamento à direita
        plt.yticks(fontsize=15)

        # Ajusta o layout para evitar cortes
        plt.tight_layout()

        # Salva o gráfico como arquivo PNG
        plt.savefig(graph_output_path)
        plt.close() # Fecha a figura para liberar memória
        print(f"Gráfico salvo em: {graph_output_path}")
    except Exception as e:
        print(f"Erro ao gerar o gráfico de quantitativo de vulnerabilidades por site: {e}")
    
    
def gerar_grafico_donut(vulnerabilidades: dict, output_path: str): # Adicionado output_path
    """
    Gera um gráfico de pizza com buraco (donut) para as vulnerabilidades por tipo e salva em um arquivo PNG.

    Args:
        vulnerabilidades (dict): Dicionário com as contagens das vulnerabilidades por tipo.
        output_path (str): Caminho para salvar o arquivo PNG do gráfico.
    """
    data = []
    # Usar .get() para evitar KeyError se a chave não existir
    if vulnerabilidades.get('critical', 0) > 0:
        data.append(('Critical', vulnerabilidades['critical'], '#8B0000'))
    if vulnerabilidades.get('high', 0) > 0:
        data.append(('High', vulnerabilidades['high'], '#FF3030'))
    if vulnerabilidades.get('medium', 0) > 0:
        data.append(('Medium', vulnerabilidades['medium'], '#FFE066'))
    if vulnerabilidades.get('low', 0) > 0:
        data.append(('Low', vulnerabilidades['low'], '#87F1FF'))

    # If no data, exit the function to avoid an empty chart
    if not data:
        print("Nenhuma vulnerabilidade para exibir no gráfico donut.")
        # Se não houver dados, criar um gráfico vazio com uma mensagem ou um placeholder.
        # Ou simplesmente não gerar o arquivo. Por agora, vamos não gerar.
        return False # Indica que o gráfico não foi gerado com sucesso

    labels = [item[0] for item in data]
    sizes = [item[1] for item in data]
    colors = [item[2] for item in data]
    explode = (0,) * len(labels) # Explode tuple should match the number of labels

    # Function to return the absolute value
    def mostrar_valor(pct, allvals):
        absolute = int(round(pct / 100. * sum(allvals)))
        return f"{absolute}"

    # Criar gráfico de rosca
    fig, ax = plt.subplots(figsize=(8, 8)) # Aumenta o tamanho da figura
    wedges, texts, autotexts = ax.pie(
        sizes,
        colors=colors,
        explode=explode,
        startangle=90,
        wedgeprops=dict(width=0.4),
        autopct=lambda pct: mostrar_valor(pct, sizes), # Valores dentro da fatia
        pctdistance=0.85 # Posiciona os números mais próximos do centro da fatia
    )

    for autotext in autotexts: # Valores dentro da fatia
        autotext.set_fontsize(14) # AUMENTADO: Tamanho da fonte dos números
        autotext.set_color('black') # Garante que o número seja visível

    # Posicionamento da legenda
    plt.legend(wedges, labels, title="Severidade", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    # Formatar como círculo
    ax.axis('equal')

    # Cria o diretório de saída se não existir
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Ajusta o layout para evitar que a legenda se sobreponha ao gráfico
    plt.tight_layout()

    plt.savefig(output_path) # Salva o gráfico
    plt.close() # Fecha a figura para liberar memória
    print(f"Gráfico donut salvo em: {output_path}")
    return True # Indica que o gráfico foi gerado com sucesso


def gerar_grafico_donut_webapp(vulnerabilidades: dict, output_path: str): # NOVO FUNÇÃO
    """
    Gera um gráfico de pizza com buraco (donut) para as vulnerabilidades de WebApp por tipo e salva em um arquivo PNG.

    Args:
        vulnerabilidades (dict): Dicionário com as contagens das vulnerabilidades por tipo (Critical, High, Medium, Low).
        output_path (str): Caminho para salvar o arquivo PNG do gráfico.
    """
    data = []
    # Usar .get() para evitar KeyError se a chave não existir
    if vulnerabilidades.get('Critical', 0) > 0:
        data.append(('Critical', vulnerabilidades['Critical'], '#8B0000'))
    if vulnerabilidades.get('High', 0) > 0:
        data.append(('High', vulnerabilidades['High'], '#FF3030'))
    if vulnerabilidades.get('Medium', 0) > 0:
        data.append(('Medium', vulnerabilidades['Medium'], '#FFE066'))
    if vulnerabilidades.get('Low', 0) > 0:
        data.append(('Low', vulnerabilidades['Low'], '#87F1FF'))

    if not data:
        print("Nenhuma vulnerabilidade de WebApp para exibir no gráfico donut.")
        return False

    labels = [item[0] for item in data]
    sizes = [item[1] for item in data]
    colors = [item[2] for item in data]
    explode = (0,) * len(labels)

    def mostrar_valor(pct, allvals):
        absolute = int(round(pct / 100. * sum(allvals)))
        return f"{absolute}"

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        sizes,
        colors=colors,
        explode=explode,
        startangle=90,
        wedgeprops=dict(width=0.4),
        autopct=lambda pct: mostrar_valor(pct, sizes),
        pctdistance=0.85
    )

    for autotext in autotexts:
        autotext.set_fontsize(14)
        autotext.set_color('black')

    plt.legend(wedges, labels, title="Severidade", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    ax.axis('equal')

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Gráfico donut de WebApp salvo em: {output_path}")
    return True