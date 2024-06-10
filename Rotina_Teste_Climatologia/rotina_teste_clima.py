import os
import re
from web_config import *
import csv
from math import radians, sin, cos, sqrt, atan2


pasta_pos_proc = input('Digite o caminho da pasta de pós-processamento: ')
diretorio_origem = os.path.join(pasta_pos_proc, 'Dados')
diretorio_destino = os.path.join(pasta_pos_proc, 'Dados_Flags')
diretorio_qc = os.path.join(pasta_pos_proc, 'Quality_Control')
diretorio_teste =  os.path.join(pasta_pos_proc, 'Teste_Clima')
dir_flag = os.path.join(diretorio_teste, 'Flags')
dir_qc = os.path.join(diretorio_teste, 'arquivos_qc')
dir_info = os.path.join(diretorio_teste, 'informações')
os.makedirs(diretorio_teste, exist_ok=True)
os.makedirs(dir_flag, exist_ok=True)
os.makedirs(dir_qc, exist_ok=True)
os.makedirs(dir_info, exist_ok=True)


for arquivo in os.listdir(diretorio_destino):
    caminho_arquivo_origem = os.path.join(diretorio_destino, arquivo)
    caminho_arquivo_destino = os.path.join(dir_flag, arquivo)

        # Verifica se é um arquivo
    if os.path.isfile(caminho_arquivo_origem):
            # Copia o arquivo para o diretório de destino
        shutil.copy(caminho_arquivo_origem, caminho_arquivo_destino)

tabela_temp = None
tabela_oxy = None
tabela_sal = None


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

        padrao_mes = re.compile(r'\* NMEA UTC \(Time\) = ([A-Z][a-z]{2}) \d{2} \d{4} \d{2}:\d{2}:\d{2}')
        nomes_colunas = {}
        spans_colunas = {}
        mes = ''

        for linha in linhas:
            resultado = padrao_mes.search(linha)
            if resultado:
                # Adicionar o mês encontrado à lista
                mes = resultado.group(1)

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
            span_depSM_str = f"{span_depSM[0]},{span_depSM[1]}"
        else:
            span_depSM_str = None

        return span_depSM_str, coordenadas, mes


        return span_depSM, coordenadas
            #return span_depSM, span_latitude, span_longitude

def tabela_location(diretorio_origem, dir_info):

    tabela_local = os.path.join(dir_info, 'Tabela_Local.txt')
    linhas_tabela = []

    with open(tabela_local, 'w') as tabela:
        tabela.write('Arquivo\t\t\tLocalização\t\tProfundidade\t\tMês\n')
        valores_tabela = []

        for arquivo in os.listdir(diretorio_origem):
            caminho_arquivo = os.path.join(diretorio_origem, arquivo)
            profundidade, local, mes = capturar_valores_colunas(caminho_arquivo)
            valores = f'{arquivo}\t{local}\t{profundidade}\t\t{mes}'

            valores_tabela.append(valores)

        for valores in valores_tabela:
            tabela.write(f'{valores}\n')
    return tabela_local


# Função para calcular a distância entre duas coordenadas usando a fórmula de Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371.0  # Raio da Terra em km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distancia = R * c
    return distancia

# Função para encontrar a localização mais próxima em um arquivo CSV
def encontrar_localizacao_proxima(lat_alvo, lon_alvo, caminho_arquivo_csv):
    melhor_distancia = float('inf')
    melhor_localizacao = None

    with open(caminho_arquivo_csv, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Pula o cabeçalho
        head = next(reader)  # Pula o cabeçalho

        for row in reader:
            lat = float(row[0])
            lon = float(row[1])

            # Calcula a distância
            distancia = calcular_distancia(lat_alvo, lon_alvo, lat, lon)

            # Atualiza a melhor localização encontrada até agora
            if distancia < melhor_distancia:
                melhor_distancia = distancia
                melhor_localizacao = (lat, lon)
                melhor_linha = ','.join(row[2:])  # Converte a lista de volta para uma string

    #print(f'O cabeçalho é {head}\n\nOs valores na coordenada {melhor_localizacao} são: {melhor_linha}')

    return head, melhor_linha

def tabela_linha(dir_info, lista_arquivos_csv, tabela_local):

    global tabela_temp
    global tabela_sal
    global tabela_oxy

    for arquivo_csv in lista_arquivos_csv: #para saber de onde é o teste
        with open(arquivo_csv, 'r') as file:
            linhas = file.readlines()
        # Cabeçalho
            head = linhas[1]
        if "Temp_" in arquivo_csv:
            if tabela_temp:
                continue
            else:
                tabela_temp = os.path.join(dir_info, 'Linhas_Temperatura.txt')
                if not os.path.exists(tabela_temp):
                    with open(tabela_temp, 'w') as tabela:
                        tabela.write('Arquivo\t\tValores(profundidade)\n')
                        tabela.write(f'{head}\n')
        elif "Sal_" in arquivo_csv:
            if tabela_sal:
                continue
            else:
                tabela_sal = os.path.join(dir_info, 'Linhas_Salinidade.txt')
                if not os.path.exists(tabela_sal):
                    with open(tabela_sal, 'w') as tabela:
                        tabela.write('Arquivo\t\tValores(profundidade)\n')
                        tabela.write(f'{head}\n')
        elif "Oxy_" in arquivo_csv:
            if tabela_oxy:
                continue
            else:
                tabela_oxy = os.path.join(dir_info, 'Linhas_Oxigenio.txt')
                if not os.path.exists(tabela_oxy):
                    with open(tabela_oxy, 'w') as tabela:
                        tabela.write('Arquivo\t\tValores(profundidade)\n')
                        tabela.write(f'{head}\n')


    with open(tabela_local, 'r') as arquivo:
        next(arquivo)  # Pular o cabeçalho
        for linha in arquivo:
            partes = linha.split()
            nome_arquivo = partes[0]
            localizacao = partes[1]
            profundidade = partes[2]
            mes = partes[3]
            lat, lon = map(float, localizacao.split(','))
            for arquivo_csv in lista_arquivos_csv:
                if mes in arquivo_csv:
                    head, melhor_linha = encontrar_localizacao_proxima(lat, lon, arquivo_csv)
                if "Oxy" in arquivo_csv:
                    with open(tabela_oxy, 'a') as tabela:
                        tabela.write(f'{nome_arquivo}\t{melhor_linha}\n')
                elif "Temp" in arquivo_csv:
                    with open(tabela_temp, 'a') as tabela:
                        tabela.write(f'{nome_arquivo}\t{melhor_linha}\n')
                elif  "Sal_" in arquivo_csv:
                    with open(tabela_sal, 'a') as tabela:
                        tabela.write(f'{nome_arquivo}\t{melhor_linha}\n')

    ref_temp = pegar_dados(tabela_temp)
    ref_sal = pegar_dados(tabela_sal)
    ref_oxy = pegar_dados(tabela_oxy)
    return ref_temp, ref_sal, ref_oxy


def pegar_dados(tabela_referencia):
    dados_referencia = {}
    with open(tabela_referencia, 'r') as file:
        linhas = file.readlines()
        # Cabeçalhos
        header = linhas[0].strip().split('\t')
        profundidades = list(map(float, linhas[1].strip().split(':')[1].split(',')))

        for linha in linhas[2:]:
            partes = linha.strip().split('\t')
            nome_arquivo = partes[0]
            valores = [float(v) if v else None for v in partes[1].split(',')]
            dados_referencia[nome_arquivo] = dict(zip(profundidades, valores))
    
    return dados_referencia

def ler_e_comparar(dir_flag, diretorio_destino, caminho_dados, lista_arquivos_csv, limite_proximidade=150):

    ref_temp, ref_sal, ref_oxy = tabela_linha(dir_info, lista_arquivos_csv, tabela_local)

    resultados_comparacao = []
    arquivos = os.listdir(dir_flag)
    for arquivo in arquivos:
        linhas_validas = []
        caminho_arquivo = os.path.join(dir_flag, arquivo)
        if arquivo.endswith('.cnv'):  # Verifica se é um arquivo cnv
            with open(caminho_arquivo, 'r+') as cnv_tratado:
                # Lê cada linha do arquivo e armazena em uma lista
                linhas = cnv_tratado.readlines()
                linhas_limpas = []
                # Retorna ao início do arquivo
                cnv_tratado.seek(0)

                referencia_temp = ref_temp[arquivo].items()
                referencia_sal = ref_sal[arquivo].items()
                referencia_oxy = ref_oxy[arquivo].items()

                    # Iterar sobre as linhas do arquivo
                for i in range(len(linhas)):
                    linha = str(linhas[i])
                    # Verifica se a linha começa com "Test"
                    if linha.startswith("Test") or linha.startswith("Flags"):
                    # Se começar com "Test", pule esta linha
                        cnv_tratado.write(linha)
                        continue

                    # Divide a linha em colunas usando espaços como delimitador
                    colunas = linha.split()
                    resultado_temp = '\t'
                    resultado_sal = '\t'
                    resultado_oxy = '\t'

                    qc_remove = False
                    
                    if len(colunas) >= 19: #and colunas[10].replace('.', '').isdigit():

                        valor_temp = float(colunas[8])
                        valor_sal = float(colunas[17])
                        valor_profundidade = float(colunas[7])
                        valor_oxy = float(colunas[19])

                        valor = float(row[valor_idx])

                        resultado_temperatura = aplicar_teste(valor_profundidade, valor_temp, referencia_temp, limite_proximidade)
                        resultado_salinidade = aplicar_teste(valor_profundidade, valor_sal, referencia_sal, limite_proximidade)
                        resultado_oxigenio = aplicar_teste(valor_profundidade, valor_oxy, referencia_oxy, limite_proximidade)





                        if valor_temp == valor_sal:
                            resultado_5 += '4'
                            qc_remove = True



                        linha = linha.rstrip('\n') + resultado_temp + resultado_sal + resultado_oxy + '\n'

                        if qc_remove == False:
                            linhas_limpas.append(linha)

                    # Escreve a linha modificada de volta no arquivo
                    cnv_tratado.write(linha)


def aplicar_teste(valor_profundidade, valor_teste, dados_referencia, limite_proximidade):
    resultados_comparacao = []
    # Encontre a profundidade de referência mais próxima
    valores_proximos = []
    for prof_ref, valor_ref in dados_referencia.items():
        if abs(valor_profundidade - prof_ref) <= limite_proximidade:
            valores_proximos.append((prof_ref, valor_ref))

    if valores_proximos:
        prof_proxima, valor_ref_proximo = min(valores_proximos, key=lambda x: abs(x[0] - valor_profundidade))
        resultados_comparacao.append((valor_profundidade, valor_teste, prof_proxima, valor_ref_proximo))
    else:
        resultados_comparacao.append((valor_profundidade, valor_teste, None, None))





# Obter os meses únicos
meses = meses(diretorio_destino)
#print("Meses únicos:", meses)
tabela_local = tabela_location(diretorio_origem, dir_info)

temperatura = obter_arquivos("Temp_", meses, 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23.pl?parameterOption=t')
#salinidade = obter_arquivos("Sal_", meses, 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23.pl?parameterOption=s')
#oxigenio = obter_arquivos("Oxy_", meses, 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23oxnu.pl?parameterOption=o')


#ref_temperatura = tabela_linha(dir_info, temperatura, tabela_local)
#ref_salinidade = tabela_linha(dir_info, salinidade, tabela_local)
#ref_oxigenio = tabela_linha(dir_info, oxigenio, tabela_local)


#span_depSM, coordenadas = capturar_valores_colunas(diretorio_origem)

#print("Span para depSM:", span_depSM)
#print("Coordenadas (latitude, longitude):", coordenadas)



