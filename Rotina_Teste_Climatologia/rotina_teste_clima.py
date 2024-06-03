import os
import re

from web_config import obter_arquivos

pasta_pos_proc = input('Digite o caminho da pasta de pós-processamento: ')
diretorio_origem = os.path.join(pasta_pos_proc, 'Dados')
diretorio_destino = os.path.join(pasta_pos_proc, 'Dados_Flags')
diretorio_qc = os.path.join(pasta_pos_proc, 'Quality_Control')
diretorio_teste =  os.path.join(pasta_pos_proc, 'Teste_Clima')
os.makedirs(diretorio_teste, exist_ok=True)


def meses(diretorio_destino):

    arquivo_jd = os.path.join(diretorio_destino, 'Julian_Days.txt')

    with open(arquivo_jd, 'r') as arquivo_jd:
        linhas = arquivo_jd.readlines()

    # Inicializar um conjunto para armazenar meses únicos
    meses_unicos = set() 

    # Regex para capturar o mês
    padrao_mes = re.compile(r'\b([A-Z][a-z]{2})\b')

    # Iterar sobre as linhas a partir da segunda linha (ignorando o cabeçalho)
    for linha in linhas[1:]:
        # Procurar o mês na linha
        match = padrao_mes.search(linha)
        if match:
            # Adicionar o mês ao conjunto
            meses_unicos.add(match.group(1))

    # Retornar a lista de meses únicos
    return list(meses_unicos)

def capturar_valores_colunas(caminho_arquivo):

        with open(caminho_arquivo, 'r') as file:
            linhas = file.readlines()

        nomes_colunas = {}
        spans_colunas = {}

        for linha in linhas:
            # Verificar linhas que contêm "name"
            if linha.startswith("# name"):
                partes = linha.split(" = ")
                indice = int(partes[0].split(" ")[2])
                nome = partes[1].strip()
                nomes_colunas[indice] = nome
            # Verificar linhas que contêm "span"
            elif linha.startswith("# span"):
                partes = linha.split(" = ")
                indice = int(partes[0].split(" ")[2])
                span_valores = partes[1].split(",")
                span_inicial = float(span_valores[0].strip())
                span_final = float(span_valores[1].strip())
                spans_colunas[indice] = (span_inicial, span_final)

        # Função para encontrar o valor do span para uma coluna específica
        def encontrar_span_para_coluna(nome_coluna):
            for indice, nome in nomes_colunas.items():
                if nome_coluna in nome:
                    return spans_colunas.get(indice)
            return None

        # Procurar os valores dos spans para "depSM", "latitude" e "longitude"
        span_depSM = encontrar_span_para_coluna("depSM")
        span_latitude = encontrar_span_para_coluna("latitude")
        span_longitude = encontrar_span_para_coluna("longitude")

        # Formatar os valores para saída
        if span_latitude and span_longitude:
            coordenadas = f"{span_latitude[0]},{span_longitude[0]}"
        else:
            coordenadas = None
        # Formatar o span do depSM
        if span_depSM:
            span_depSM_str = f"{span_depSM[0]}, {span_depSM[1]}"
        else:
            span_depSM_str = None

        return span_depSM_str, coordenadas


        return span_depSM, coordenadas
            #return span_depSM, span_latitude, span_longitude

def tabela_location(diretorio_origem, diretorio_teste):

    tabela_local = os.path.join(diretorio_teste, 'Tabela_Local.txt')
    linhas_tabela = []
    with open(tabela_local, 'w') as tabela:
        tabela.write('Arquivo\t\t\tLocalização\t\t\tProfundidade\n')
        valores_tabela = []

        for arquivo in os.listdir(diretorio_origem):
            caminho_arquivo = os.path.join(diretorio_origem, arquivo)
            profundidade, local = capturar_valores_colunas(caminho_arquivo)
            valores = f'{arquivo}\t{local}\t{profundidade}'

            valores_tabela.append(valores)
        for valores in valores_tabela:
            tabela.write(f'{valores}\n')

def ler_csv(arquivo_csv):


    pass
            

# Obter os meses únicos
meses = meses(diretorio_destino)
print("Meses únicos:", meses)
tabela_location(diretorio_origem, diretorio_teste)

#span_depSM, coordenadas = capturar_valores_colunas(diretorio_origem)

#print("Span para depSM:", span_depSM)
#print("Coordenadas (latitude, longitude):", coordenadas)



