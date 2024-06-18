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

nome_colunas = None
for arquivo in os.listdir(diretorio_qc):
    if nome_colunas:
        continue
    else:
        caminho_arquivo = os.path.join(diretorio_qc, arquivo)
        with open(caminho_arquivo, 'r') as tabela:
            nome_colunas = tabela.readline().strip()


tabela_temp = None
tabela_oxy = None
tabela_sal = None
dp_temp = None
dp_oxy = None
dp_sal = None



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

def tabela_linha(dir_info, diretorio_csv, tabela_local):

    global tabela_temp
    global tabela_sal
    global tabela_oxy
    global dp_temp
    global dp_oxy
    global dp_sal


    lista_csv = os.listdir(diretorio_csv)
    for nome_arquivo_csv in lista_csv:
        arquivo_csv = os.path.join(diretorio_csv, nome_arquivo_csv)
        with open(arquivo_csv, 'r') as file:
            linhas = file.readlines()
        # Cabeçalho
            head = linhas[1]

        if 'DP_' in arquivo_csv:
            if "Temp_" in arquivo_csv:
                if dp_temp:
                    continue
                else:
                    dp_temp = os.path.join(dir_info, 'Linhas_DP_Temperatura.txt')
                    if not os.path.exists(dp_temp):
                        with open(dp_temp, 'w') as tabela:
                            tabela.write('Arquivo\t\tValores(profundidade)\n')
                            tabela.write(f'{head}\n')
            elif "Sal_" in arquivo_csv:
                if dp_sal:
                    continue
                else:
                    dp_sal = os.path.join(dir_info, 'Linhas_DP_Salinidade.txt')
                    if not os.path.exists(dp_sal):
                        with open(dp_sal, 'w') as tabela:
                            tabela.write('Arquivo\t\tValores(profundidade)\n')
                            tabela.write(f'{head}\n')
            elif "Oxy_" in arquivo_csv:
                if dp_oxy:
                    continue
                else:
                    dp_oxy = os.path.join(dir_info, 'Linhas__DP_Oxigenio.txt')
                    if not os.path.exists(dp_oxy):
                        with open(dp_oxy, 'w') as tabela:
                            tabela.write('Arquivo\t\tValores(profundidade)\n')
                            tabela.write(f'{head}\n')
        elif "Temp_" in arquivo_csv:
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


            for nome_arquivo_csv in lista_csv:
                arquivo_csv = os.path.join(diretorio_csv, nome_arquivo_csv)
           # for arquivo_csv in lista_arquivos_csv:
                if mes in arquivo_csv:
                    head, melhor_linha = encontrar_localizacao_proxima(lat, lon, arquivo_csv)
                    print(f'O mês é {mes}')

                    if "DP_Oxy" in arquivo_csv:
                        with open(dp_oxy, 'a') as tabela:
                            tabela.write(f'{nome_arquivo}\t{melhor_linha}\n')
                    elif "DP_Temp" in arquivo_csv:
                        with open(dp_temp, 'a') as tabela:
                            tabela.write(f'{nome_arquivo}\t{melhor_linha}\n')
                    elif "DP_Sal" in arquivo_csv:
                        with open(dp_sal, 'a') as tabela:
                            tabela.write(f'{nome_arquivo}\t{melhor_linha}\n')
                    elif "Oxy" in arquivo_csv:
                        with open(tabela_oxy, 'a') as tabela:
                            tabela.write(f'{nome_arquivo}\t{melhor_linha}\n')
                    elif "Temp" in arquivo_csv:
                        with open(tabela_temp, 'a') as tabela:
                            tabela.write(f'{nome_arquivo}\t{melhor_linha}\n')
                    elif  "Sal" in arquivo_csv:
                        with open(tabela_sal, 'a') as tabela:
                            tabela.write(f'{nome_arquivo}\t{melhor_linha}\n')

    ref_temp = pegar_dados(tabela_temp)
    ref_sal = pegar_dados(tabela_sal)
    ref_oxy = pegar_dados(tabela_oxy)
    ref_dp_temp = pegar_dados(dp_temp)
    ref_dp_sal = pegar_dados(dp_sal)
    ref_dp_oxy = pegar_dados(dp_oxy)
    print(ref_temp, ref_sal, ref_oxy,ref_dp_temp, ref_dp_sal, ref_dp_oxy)
    return ref_temp, ref_sal, ref_oxy,ref_dp_temp, ref_dp_sal, ref_dp_oxy

def pegar_dados(tabela_referencia):
    dados_referencia = {}
    with open(tabela_referencia, 'r') as file:
        linhas = file.readlines()
        # Cabeçalhos
        header = linhas[0].strip().split('\t')
        profundidades = list(map(float, linhas[1].strip().split(':')[1].split(',')))

        for linha in linhas[3:]:
            partes = linha.strip().split('\t')
            nome_arquivo = partes[0]
            valores = [float(v) if v else None for v in partes[1].split(',')]
            dados_referencia[nome_arquivo] = dict(zip(profundidades, valores))
    
    return dados_referencia

# Função para mapear profundidades para as referências corretas
def map_depth_to_reference(depth):
    depth_intervals = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95,
                       100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475,
                       500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200,
                       1250, 1300, 1350, 1400, 1450, 1500]

    if depth <= 100:
        return (depth // 5) * 5
    elif depth <= 500:
        return ((depth - 100) // 25) * 25 + 100
    else:
        return ((depth - 500) // 50) * 50 + 500

# Função para obter a referência interpolada
def obter_referencia_interpolada(profundidade, referencias):
    ref_depth = map_depth_to_reference(profundidade)
    return referencias.get(ref_depth, None)

# Função para aplicar o teste
def aplicar_teste(valor, referencia, desvio_padrao):
    if referencia is None or desvio_padrao is None:
        #print('olha so deu 2')
        return '2'  # Se não houver referência ou desvio padrão, consideramos como 2
    if abs(valor - referencia) >  abs(desvio_padrao):
       # print('olha so deu erro!')
        return '4'
        
    return '1'

# Função para processar uma linha
def processar_linha(colunas, referencia_temp, referencia_sal, referencia_oxy, referencia_dp_temp, referencia_dp_sal, referencia_dp_oxy):
    valor_temp = float(colunas[8])
    valor_sal = float(colunas[17])
    valor_profundidade = float(colunas[7])
    valor_oxy = float(colunas[22])

    ref_temp = obter_referencia_interpolada(valor_profundidade, referencia_temp)
    ref_sal = obter_referencia_interpolada(valor_profundidade, referencia_sal)
    ref_oxy = obter_referencia_interpolada(valor_profundidade, referencia_oxy)
    dp_temp = obter_referencia_interpolada(valor_profundidade, referencia_dp_temp)
    dp_sal = obter_referencia_interpolada(valor_profundidade, referencia_dp_sal)
    dp_oxy = obter_referencia_interpolada(valor_profundidade, referencia_dp_oxy)

    #print(f'valor temp:{valor_temp}, valor ref: {ref_temp}, desvio: {dp_temp}')
    resultado_temp = aplicar_teste(valor_temp, ref_temp, dp_temp)
    resultado_sal = aplicar_teste(valor_sal, ref_sal, dp_sal)
    resultado_oxy = aplicar_teste(valor_oxy, ref_oxy, dp_oxy)
    #if resultado_oxy == '4':
     #   print(f'valor oxy:{valor_oxy}, valor ref: {ref_oxy}, desvio: {dp_oxy}')
    #if resultado_sal == '4':
    #    print(f'valor sal:{valor_sal}, valor ref: {ref_sal}, desvio: {dp_sal}')
   # if resultado_temp == '4':
    #    print(f'dif temp:{abs(valor_temp - ref_temp)}, desvio: {abs(dp_temp)}')


        #print()

    return resultado_temp, resultado_sal, resultado_oxy


def ler_e_comparar(dir_flag, dir_info, tabela_local, diretorio_csv, dir_qc):

    #ref_temp, ref_sal, ref_oxy, ref_dp_temp, ref_dp_sal, ref_dp_oxy = tabela_linha(dir_info, diretorio_csv, tabela_local)
    global ref_temp
    global ref_sal
    global ref_oxy
    global ref_dp_temp
    global ref_dp_sal
    global ref_dp_oxy
    erros_sal = 0
    erros_temp = 0
    erros_oxy = 0
    total_linhas = 0

    arquivos = os.listdir(dir_flag)
    for arquivo in arquivos:
        caminho_arquivo = os.path.join(dir_flag, arquivo)
        if arquivo.endswith('.cnv'):  # Verifica se é um arquivo cnv
            with open(caminho_arquivo, 'r+') as cnv_tratado:
                print(arquivo)
                # Lê cada linha do arquivo e armazena em uma lista
                linhas = cnv_tratado.readlines()
                linhas_limpas = []
                # Retorna ao início do arquivo
                cnv_tratado.seek(0)

                # Obtém as referências correspondentes para o arquivo atual
                referencia_temp = ref_temp.get(arquivo, {})
                referencia_sal = ref_sal.get(arquivo, {})
                referencia_oxy = ref_oxy.get(arquivo, {})
                referencia_dp_temp = ref_dp_temp.get(arquivo, {})
                referencia_dp_sal = ref_dp_sal.get(arquivo, {})
                referencia_dp_oxy = ref_dp_oxy.get(arquivo, {})


                    # Iterar sobre as linhas do arquivo
                for i in range(len(linhas)):
                    linha = str(linhas[i])
                    # Verifica se a linha começa com "Test"
                    if linha.startswith("Test") or linha.startswith("Flags"):
                    # Se começar com "Test", pule esta linha
                        if linha.startswith("Test 8"):
                            cnv_tratado.write(linha.rstrip('\n'))
                            cnv_tratado.write('\nTest 9 => Climatology test for Temperature')
                            cnv_tratado.write('\nTest 10 => Climatology test for Salinity')
                            cnv_tratado.write('\nTest 11 => Climatology test for Oxygen\n')
                        else:
                            cnv_tratado.write(linha)
                        continue

                    # Divide a linha em colunas usando espaços como delimitador
                    colunas = linha.split()
                    resultado_temp = '\t'
                    resultado_sal = '\t'
                    resultado_oxy = '\t'

                    qc_remove = False
                    
                    if len(colunas) >= 19: 

                        resultado_temp, resultado_sal, resultado_oxy = processar_linha(
                            colunas, referencia_temp, referencia_sal, referencia_oxy, 
                            referencia_dp_temp, referencia_dp_sal, referencia_dp_oxy
                        )

                        if resultado_temp == '4':
                            erros_temp += 1
                            qc_remove = True

                        if resultado_oxy == '4':
                            erros_oxy += 1
                            qc_remove = True

                        if resultado_sal == '4':
                            erros_sal += 1
                            qc_remove = True

                        linha = linha.rstrip('\n') + f'\t{resultado_temp}\t{resultado_sal}\t{resultado_oxy}\n'
                        total_linhas += 1
                        if qc_remove == False:
                            linhas_limpas.append(linha)

                    
                    
                    cnv_tratado.write(linha)
            criar_arquivo_qc(linhas_limpas, dir_qc, arquivo)

    print(f'total de linhas avaliadas: {total_linhas}')
    print(f'total de erros de temperatura: {erros_temp}')
    print(f'total de erros de salinidade: {erros_sal}')
    print(f'total de erros de oxigenio: {erros_oxy}')


def criar_arquivo_qc(linhas_limpas, dir_qc, arquivo):

    global nome_colunas  

    caminho_arquivo = os.path.join(dir_qc, arquivo)
    with open(caminho_arquivo, 'w') as novo_arquivo:
        novo_arquivo.write(f'{nome_colunas}' + f'\tTest 9\tTest 10\tTest 11\n')
        for linha in linhas_limpas:
            novo_arquivo.write(linha)


dp_temp = os.path.join(dir_info, 'Linhas_DP_Temperatura.txt')
dp_sal = os.path.join(dir_info, 'Linhas_DP_Salinidade.txt')
dp_oxy = os.path.join(dir_info, 'Linhas__DP_Oxigenio.txt')
tabela_temp = os.path.join(dir_info, 'Linhas_Temperatura.txt')
tabela_sal = os.path.join(dir_info, 'Linhas_Salinidade.txt')
tabela_oxy = os.path.join(dir_info, 'Linhas_Oxigenio.txt')


ref_temp = pegar_dados(tabela_temp)
ref_sal = pegar_dados(tabela_sal)
ref_oxy = pegar_dados(tabela_oxy)
ref_dp_temp = pegar_dados(dp_temp)
ref_dp_sal = pegar_dados(dp_sal)
ref_dp_oxy = pegar_dados(dp_oxy)

# Obter os meses únicos
meses = meses(diretorio_destino)
print("Meses únicos:", meses)
tabela_local = tabela_location(diretorio_origem, dir_info)

#temperatura = obter_arquivos("Temp_", meses, 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23.pl?parameterOption=t')
#salinidade = obter_arquivos("Sal_", meses, 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23.pl?parameterOption=s')
#oxigenio = obter_arquivos("Oxy_", meses, 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23oxnu.pl?parameterOption=o')

diretorio_csv = './extraido/'

#tabela_linha(dir_info, diretorio_csv, tabela_local)

ler_e_comparar(dir_flag, dir_info, tabela_local, diretorio_csv, dir_qc)
