import os
from pathlib import Path
import glob
import shutil
import re
import lxml
import sys
from lxml import etree
import simplekml
from collections import defaultdict
import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.lines import Line2D


# Lista para armazenar os dados das estações
def cria_tabela(pasta_processados):
    
    # Padrões de expressões regulares para extrair informações
    padrao_numero_estacao = re.compile(r'_(\d{3}[a-zA-Z]*)\.cnv')
    padrao_latitude = re.compile(r'\* NMEA Latitude = (\d{2} \d+\.\d+ [NS])')
    padrao_longitude = re.compile(r'\* NMEA Longitude = (\d{3} \d+\.\d+ [EW])')
    padrao_data_hora = re.compile(r'\* NMEA UTC \(Time\) = ([A-Za-z]{3} \d{2} \d{4} \d{2}:\d{2}:\d{2})')
    
    # Lista para armazenar os dados das estações
    dados_estacoes = []

    for arquivo_cnv in os.listdir(pasta_processados):
        if arquivo_cnv.endswith('.cnv'):
            numero_estacao = padrao_numero_estacao.search(arquivo_cnv).group(1)
            
            arq_ler = os.path.join(pasta_processados, arquivo_cnv)
            with open(arq_ler, 'r', encoding='latin-1') as arquivo:
                conteudo = arquivo.read()

                latitude_match = padrao_latitude.search(conteudo)
                longitude_match = padrao_longitude.search(conteudo)
                data_hora_match = padrao_data_hora.search(conteudo)
            
            if latitude_match and longitude_match and data_hora_match:
                latitude = latitude_match.group(1)
                longitude = longitude_match.group(1)
                data_hora = data_hora_match.group(1)
                
                dados_estacoes.append((numero_estacao, data_hora, latitude, longitude))
                
    return dados_estacoes

#lista de quais estações vão ser processadas
def process_range(input_range):
    result = []

    # Divide a entrada em partes separadas por vírgulas
    parts = input_range.split(',')

    for part in parts:
        part = part.strip()

        # Verifica se a parte contém um intervalo (por exemplo, "001-010")
        if '-' in part:
            start, end = map(str.strip, part.split('-'))
            
            # Verifica se o início e o fim são compostos apenas por dígitos ou dígitos seguidos de letras
            if re.match(r'^\d+[a-zA-Z]*$', start) and re.match(r'^\d+[a-zA-Z]*$', end):
                result.extend(f"{num:03}" for num in range(int(start), int(end) + 1))
        
        # Verifica se a parte é composta apenas por dígitos ou dígitos seguidos de letras
        elif re.match(r'^\d+[a-zA-Z]*$', part):
            result.append(f"{(part):03}")

    return result

def obter_estacoes_disponiveis(pasta_copia):
    estacoes = set()
    
    # Expressão regular para extrair o número da estação
    expressao = r'(\d{3}[a-zA-Z]*)'  # Procura 3 dígitos seguidos por zero ou mais letras

    # Iterar pelos nomes dos arquivos .hex
    arquivos_hex = [arquivo for arquivo in os.listdir(pasta_copia) if arquivo.endswith('.hex')]
    for arquivo in arquivos_hex:
        # Use a expressão regular para encontrar o número da estação e a versão
        matches = re.findall(expressao, arquivo)
        if matches:
            estacao = matches[0]
            estacoes.add(estacao)
    
    return estacoes

def input_valido(input_string, estacoes_disponiveis):
    input_list = input_string.split(',')
    
    for item in input_list:
        item = item.strip()
        
        if '-' in item:
            start, end = map(str.strip, item.split('-'))
            
            if not (re.match(r'^\d+[a-zA-Z]*$', start) and re.match(r'^\d+[a-zA-Z]*$', end)):
                return False
        elif not (re.match(r'^\d+[a-zA-Z]*$', item) and item in estacoes_disponiveis):
            return False
    
    return True

def obter_numero_scan(arq_mrk):

    # Lê o arquivo de texto como um arquivo CSV, pulando a primeira linha
    df = pd.read_csv(arq_mrk, delimiter=r'\s*,\s*', skiprows=1, engine='python')

    # Encontra o índice onde o texto contém a palavra "Scan"
    indice_scan = df.columns[df.columns.str.contains('Scan')][0]

    # Obtém o valor da quarta linha no índice "Scan"
    valor_scan = int(df.loc[1, 'Scan'])

    #print(f'O valor de "Scan" é: {valor_scan}') 
    return valor_scan

def mrk(replace, num, pasta_copia, arq_dat):
    nome_arq = f'{replace}{num}.mrk'
    arq_mrk = os.path.join(pasta_copia, nome_arq)

    if os.path.exists(arq_mrk):
            numero_mark = obter_numero_scan(arq_mrk)
    
    with open(arq_dat, 'r', encoding='utf-8') as arquivo_dat:
        conteudo_dat = arquivo_dat.read()

        # Parse do conteúdo do arquivo .dat
        tree = ET.ElementTree(ET.fromstring(conteudo_dat))
        root = tree.getroot()

        # Encontre o elemento <ScansToSkip> no XML
        scans_to_skip_element = root.find('.//ScansToSkip')

        # Se o elemento existir, substitua o valor
        if scans_to_skip_element is not None:
            scans_to_skip_element.set('value', str(numero_mark))

        # Salve as modificações no arquivo .dat
        tree.write(arq_dat, encoding='utf-8', xml_declaration=True)

        print(f'Valor de Mark Scan foi atualizado para: {numero_mark}')
        return numero_mark

def escreve_scan(estacoes_versoes, replace, pasta_copia, tabela_mrk):
    
    with open(tabela_mrk, 'w') as tabela_scan:
         tabela_scan.write('Nº ESTAÇÃO\tMark Scan\n')                    

    for estacao in estacoes_versoes.items():
        nome_arq = f'{replace}{estacao[0]}.mrk'
        arq_mrk = os.path.join(pasta_copia, nome_arq)
        if os.path.exists(arq_mrk):
            mark_scan = obter_numero_scan(arq_mrk)

            # Adiciona as informações da lista à tabela
        with open(tabela_mrk, 'a') as tabela_scan:
            tabela_scan.write(f'{estacao[0]}\t\t{mark_scan}\n')           

def process(bat, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes, replace, arq_dat): #processa os dados
    # Obtenha a lista de estações disponíveis
    estacoes_disponiveis = obter_estacoes_disponiveis(pasta_copia)
    
    while True:
        input_string = input('Em quais estações irá processar os dados? (Escreva uma lista com 3 dígitos. Ex.: 001-010, 020\nCaso a estação tenha letras após o número, por favor, escreva, exemplo: 001ABC)\nCaso queira processar todas as estações, escreva "tudo".')
        
        if input_string == 'tudo':
            input_list = []
            for estacao in estacoes_versoes.items():
                mark_scan = mrk(replace, estacao[0], pasta_copia, arq_dat)
                cmd = f'sbebatch {bat} {estacao[0]}'
                input_list.append(estacao[0])
                os.system(cmd)
               
                    
            estacoes_registradas = set()
            try:
                with open(tabela, 'r') as arquivo_tabela:
                    for linha in arquivo_tabela:
                        estacao, *_ = linha.split('\t')
                        estacoes_registradas.add(estacao)
            except FileNotFoundError:
                pass  # O arquivo da tabela ainda não existe
            # Escrever os dados em um arquivo de texto em formato de tabela
            dados_estacoes = cria_tabela(pasta_processados)

            # Ordene a lista de dados apenas pelo número da estação
            dados_estacoes.sort(key=lambda x: x[0])

            with open(tabela, 'a') as arquivo_saida:
                for dados in dados_estacoes:
                    estacao = dados[0]
                    if estacao not in estacoes_registradas:
                        estacoes_registradas.add(estacao)
                        arquivo_saida.write(',\t'.join(dados) + '\n')

            with open(relatorio, 'a') as arquivo:
                arquivo.write('\n\nForam processadas as seguintes estações:')
                for num in input_list:
                    arquivo.write('\nEstação ' + num)
            break
        
        else:
            input_list = process_range(input_string)
            estacoes_invalidas = []
    
            for estacao in input_list:
                if estacao not in estacoes_disponiveis:
                    estacoes_invalidas.append(estacao)
                    
            if estacoes_invalidas:
                print(f'As seguintes estações não estão disponíveis: {", ".join(estacoes_invalidas)}')
                print('Por favor, revise quais estações gostaria de processar e escreva corretamente.')
                continue  # Refaz a pergunta se houver estações inválidas
            
            if input_valido(input_string, estacoes_disponiveis) == False:
                print('Por favor, revise quais estações gostaria de processar e escreva corretamente.')
                continue  # Refaz a pergunta se houver estações inválidas
            
            # Todas as estações são válidas, prossiga com o processamento
            for num in input_list:
                mark_scan = mrk(replace, num, pasta_copia, arq_dat)
                cmd = ('sbebatch ' + str(bat) + ' ' + num)                
                os.system(cmd)    
             
            with open(tabela, 'w') as arquivo_saida:
                arquivo_saida.write('Nº ESTAÇÃO,\tData e Hora,\tLatitude,\tLongitude\n')
                    
            estacoes_registradas = set()
            try:
                with open(tabela, 'r') as arquivo_tabela:
                    for linha in arquivo_tabela:
                        estacao, *_ = linha.split('\t')
                        estacoes_registradas.add(estacao)
            except FileNotFoundError:
                pass  # O arquivo da tabela ainda não existe
            # Escrever os dados em um arquivo de texto em formato de tabela
            dados_estacoes = cria_tabela(pasta_processados)

            # Ordene a lista de dados apenas pelo número da estação
            dados_estacoes.sort(key=lambda x: x[0])

            with open(tabela, 'a') as arquivo_saida:
                for dados in dados_estacoes:
                    estacao = dados[0]
                    if estacao not in estacoes_registradas:
                        estacoes_registradas.add(estacao)
                        arquivo_saida.write(',\t'.join(dados) + '\n')


            with open(relatorio, 'a') as arquivo:
                arquivo.write('\n\nForam processadas as seguintes estações:')
                for num in input_list:
                    arquivo.write('\nEstação ' + num)
            break
  
def proc_finais(pasta_processados, tabela, pasta_relatorio):
    while True:
        processos = input('Digite "0" caso queira criar apenas um arquivo KML\n"1" se quiser criar apenas um Mapa PNG\n"2" para criar ambos\nou "3" caso não queira criar nenhum"').lower()
        
        if processos == '0':
            cria_kml(pasta_processados, tabela)
            break
        
        elif processos == '1':
            grafico_1(tabela, pasta_relatorio)
            break

        elif processos == '2':
            grafico_1(tabela, pasta_relatorio)
            cria_kml(pasta_processados, tabela)
            break
        
        elif processos == '3':
            break
            
        else:
            print('Resposta inválida. Por favor, responda com um input válido.')

def end(bat, pasta_split, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes, replace, arq_dat, pasta_relatorio): #conferir se o processamento terminou
    while True:
        terminar = input('Deseja terminar o processamento? (s/n)').lower()
        if terminar == 's':
            print('Processamento concluído!')
            print('Obrigado por utilizar nosso sistema!')
            break
        elif terminar == 'n':
            process(bat, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes, replace, arq_dat)
            split(pasta_split)
            proc_finais(pasta_processados, tabela, pasta_relatorio)
        else:
            print('Resposta inválida. Por favor, responda com "s" para sim ou "n" para não.')
                       
def split(pasta_split): # separa os arquivos de subida e de descida
    while True:
        conferir = input('Deseja separar os arquivos de subida e descida? (s/n)').lower()
        if conferir == 's':
            pasta_up = os.path.join(pasta_split, 'up')
            pasta_down = os.path.join(pasta_split, 'down')

            if not os.path.exists(pasta_up):
                os.makedirs(pasta_up)

            if not os.path.exists(pasta_down):
                os.makedirs(pasta_down)
            arquivos_cnv = [arquivo for arquivo in os.listdir(pasta_split) if arquivo.endswith('.cnv')]

            for arquivo in arquivos_cnv:
                caminho_origem = os.path.join(pasta_split, arquivo)
                primeira_letra = arquivo[0].lower()
                        
                if primeira_letra == 'd':
                    caminho_destino = os.path.join(pasta_down, arquivo)
                elif primeira_letra == 'u':
                    caminho_destino = os.path.join(pasta_up, arquivo)
                        
                shutil.move(caminho_origem, caminho_destino)
            break
        if conferir == 'n':
            break
        else:
            print('Resposta inválida. Por favor, responda com "s" para sim ou "n" para não.')

def converter_coordenadas(coordenada): # muda as coordenadas que estão na tabela, mas não muda na tabela
    graus, minutos, direcao = coordenada.split()
    graus = float(graus)
    minutos = float(minutos)
    decimal = graus + minutos / 60.0
    
    if direcao in ["S", "W"]:
        decimal = -decimal
        
    return decimal

def grafico_1(tabela, pasta_relatorio):
    
    # Leia o arquivo de texto
    estacao = []
    latitude = []
    longitude = []

    coordenadas_dict = {}

    with open(tabela, 'r') as arquivo:
        next(arquivo)

        for linha in arquivo:
            colunas = linha.strip().split(',\t')

            # Obter o número da estação, latitude e longitude
            estacao = int(colunas[0])
            
            lat = colunas[2].strip()
            long = colunas[3].strip()

            # Converter as coordenadas para graus decimais
            converted_latitude = converter_coordenadas(lat)
            converted_longitude = converter_coordenadas(long)
            # Armazenar as coordenadas no dicionário
            coordenadas_dict[estacao] = (converted_latitude, converted_longitude)

            # Processar a coluna de Latitude
            lat_str = colunas[2].strip()
            latitude.append(lat_str)

            # Processar a coluna de Longitude
            lon_str = colunas[3].strip()
            longitude.append(lon_str)


    # Converter as latitudes e longitudes para graus decimais
    converted_latitudes = [converter_coordenadas(lat) for lat in latitude]
    converted_longitudes = [converter_coordenadas(lon) for lon in longitude]

    # Definir as latitudes e longitudes mínimas e máximas
    lat_min = min(converted_latitudes) - 2
    lat_max = max(converted_latitudes) + 2
    lon_min = min(converted_longitudes) - 3
    lon_max = max(converted_longitudes) + 3

    # Criar um mapa usando a biblioteca Basemap com as latitudes e longitudes convertidas
    m = Basemap(
        projection='merc',
        llcrnrlat=min(converted_latitudes) - 2,
        urcrnrlat=max(converted_latitudes) + 2,
        llcrnrlon=min(converted_longitudes) - 3,
        urcrnrlon=max(converted_longitudes) + 3,
        resolution='l'
    )

    # Criar uma figura e um eixo para o mapa
    fig, ax2 = plt.subplots(figsize=(15, 10))

    # Definir a cor do oceano como azul e a cor da terra como cinza
    m.drawmapboundary(fill_color='#99CCFF')
    m.fillcontinents(color='lightgrey', lake_color='#99CCFF')

    # Desenhar a costa e os limites do mapa
    m.drawcoastlines()
    m.drawcountries()

    # Adicionar estilo de linha para cada meridiano
    parallels = range(int(lat_min), int(lat_max) + 1)
    meridians = range(int(lon_min), int(lon_max) + 1)
    m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10, linewidth=1)
    m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10, linewidth=1)
        

    # Plotar os pontos no mapa com base nas coordenadas das estações
    for estacao, coordenadas in coordenadas_dict.items():
        latitude, longitude = coordenadas
        x, y = m(longitude, latitude)
        m.plot(x, y, 'ro', markersize=5)

        x_offset = 3500  # Ajuste o valor conforme necessário
        ax2.annotate(str(estacao), xy=(x + x_offset, y), xytext=(x + x_offset, y),
                    color='black', fontsize=12,
                    ha='left', va='bottom')
                    

    # Adicionar rótulos de paralelos e meridianos
    parallels = range(int(lat_min), int(lat_max) + 1)
    meridians = range(int(lon_min), int(lon_max) + 1)
    m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10, linewidth=0.5)
    m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10, linewidth=0.5)

    # Adicionar título e legendas
    map_name = input('Digite o nome do seu mapa: ')
    ax2.set_title(map_name)

    ax2.legend()

    # Criar um marcador personalizado para a legenda
    marker = Line2D([0], [0], marker='o', color='red', linestyle='None', label='Estações')

    # Adicionar o marcador personalizado à legenda
    ax2.legend(handles=[marker], loc='upper right')

    plt.savefig(os.path.join(str(pasta_relatorio) + map_name + '.png'), dpi=300)

    # Exibir o mapa
    plt.show()
    
def criar_arquivo_kml(nome_arquivo, lista_coordenadas, caminho_fotos):
    kml = simplekml.Kml()

    style = simplekml.Style()
    style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png'

    for estacao, coordenadas in lista_coordenadas.items():
        latitude, longitude = coordenadas
        ponto = kml.newpoint(name=estacao, coords=[(longitude, latitude)])
        ponto.style = style
        
        fotos_estacao = [arquivo for arquivo in os.listdir(caminho_fotos) if arquivo.endswith(f"{estacao}.jpg") or arquivo.endswith(f"{estacao}-ts.jpg")]

        if fotos_estacao:
            description_html = etree.Element("div")
            for foto in fotos_estacao:
                caminho_foto = os.path.join(caminho_fotos, foto)
                imagem_url = "file:///" + caminho_foto.replace('\\', '/')
                img_tag = etree.Element("img", style="max-width:500px;", src=imagem_url)
                description_html.append(img_tag)
            
            ponto.description = etree.tostring(description_html, pretty_print=True, encoding="unicode")

    kml.save(nome_arquivo)

def cria_kml(pasta_processados, tabela):
    
    caminho_tabela = tabela
    caminho_fotos = os.path.join(pasta_processados, 'Processamento_seaplot')
            
    coordenadas_dict = {}
    with open(caminho_tabela, "r") as arquivo:
        linhas = arquivo.readlines()[1:]
        for linha in linhas:
            campos = linha.split(",\t")
            estacao = campos[0]
            latitude = campos[2]
            longitude = campos[3]
                    
            latitude_convertida = converter_coordenadas(latitude)
            longitude_convertida = converter_coordenadas(longitude)

            coordenadas_dict[estacao] = (latitude_convertida, longitude_convertida)
                    
    nome_kml = input('Digite o nome do seu arquivo KML: ')
    criar_arquivo_kml(os.path.join(pasta_processados, 'Relatório', nome_kml + '.kml'), coordenadas_dict, caminho_fotos)

lista_print = [] #armazena as strings do relatório
def list_print(message):
    lista_print.append(message)
    
def list_print_custom(lst, prefix=''):
    print(prefix + '\n'.join(lst))


# Obter o nome do usuário
nome_usuario = os.getlogin()

# Obter o caminho da área de trabalho
caminho_area_trabalho = os.path.join(os.path.expanduser('~'), 'Desktop')

# Achou a pasta "PROCESS_CTD", equivalente a pasta anterior a dos dados
caminho_process_ctd = os.path.join(caminho_area_trabalho, 'PROCESS_CTD')

caminho_arquivos_config = os.path.join(caminho_process_ctd, 'Arquivos_Config')
caminho_dados = os.path.join(caminho_process_ctd, 'Dados')
caminho_processados = os.path.join(caminho_process_ctd, 'Processados')

caminho_arquivos_psa = os.path.join(caminho_arquivos_config, 'Arquivos_PSA')
caminho_batch_file = os.path.join(caminho_arquivos_config, 'Batch_File')

caminho_relatorio = os.path.join(caminho_processados, 'Relatório')
caminho_arquivos_btl = os.path.join(caminho_processados, 'Arquivos_BTL')
caminho_processamento_seaplot = os.path.join(caminho_processados, 'Processamento_Seaplot')
caminho_processamento_split = os.path.join(caminho_processados, 'Processamento_Split')

# Criar arquivos de texto em "Relatório"
caminho_txt_relatorio = os.path.join(caminho_relatorio, 'Relatório_de_processamento.txt')
caminho_tabela_relatorio = os.path.join(caminho_relatorio, 'Tabela_de_posição.txt')
caminho_mrk = os.path.join(caminho_relatorio, 'Tabela_Scan.txt')

# Criar arquivos de texto

with open(caminho_tabela_relatorio, 'w') as arquivo_tabela_posicao:
    arquivo_tabela_posicao.write('Nº ESTAÇÃO,\tData e Hora,\tLatitude,\tLongitude\n')
    
with open(caminho_mrk, 'w') as arquivo_tabela_posicao:
    arquivo_tabela_posicao.write('Tabela Criada!\n')



# Identificar as pastas
pasta_origem = Path(caminho_process_ctd)
pasta_relatorio = Path(caminho_relatorio)
relatorio = caminho_txt_relatorio
tabela = caminho_tabela_relatorio
pasta_processados = Path(caminho_processados)
caminho_bat = Path(caminho_batch_file)
caminho_garrafa = Path(caminho_arquivos_btl)
pasta_split = Path(caminho_processamento_split)
pasta_plot = Path(caminho_processamento_seaplot)
pasta_copia = Path(caminho_dados)
caminho_psa = Path(caminho_arquivos_psa)
tabela_mrk = Path(caminho_mrk)
#caminho_tabela = os.path.join(caminho_relatorio, 'Tabela_csv.txt')


# configurações iniciais realizadas *******************************************************************************************

lista_arquivos = os.listdir(pasta_copia)
            # Padrão de expressão regular para encontrar a parte do número da estação no nome do arquivo
padrao_numero_estacao = re.compile(r'(.+?)(\d{3}[a-zA-Z]*)(\..*$)')


for file in lista_arquivos:
                # Use a expressão regular para encontrar o número da estação
    match = padrao_numero_estacao.search(file)

    if match:
        parte_anterior = match.group(1)
        numero_estacao = match.group(2)
        extensao_arquivo = match.group(3)
    else:
                    # Se não encontrar um número de estação, deixe tudo em branco
        parte_anterior = ''
        numero_estacao = ''
        extensao_arquivo = ''
replace = parte_anterior
if not replace.endswith('_'):
    replace += '_'


            # Contagem de arquivos e tipos
arquivos = glob.glob(os.path.join(pasta_copia, '*'))
counter = len(arquivos)
n_hex = len(list(pasta_copia.glob('*.hex')))
n_bl = len(list(pasta_copia.glob('*.bl')))
n_hdr = len(list(pasta_copia.glob('*.hdr')))
n_mrk = len(list(pasta_copia.glob('*.mrk')))
n_xmlcon = len(list(pasta_copia.glob('*.XMLCON')))
n_con = len(list(pasta_copia.glob('*.con')))
other = counter - (n_hex + n_bl + n_hdr + n_mrk + n_xmlcon + n_con)

#list_print(f'Foram copiados {counter} arquivos.')
list_print(f'Há {n_hex} arquivos do tipo HEX')
list_print(f'{n_bl} arquivos do tipo BL')
list_print(f'{n_hdr} arquivos do tipo HDR')
list_print(f'{n_mrk} arquivos do tipo MRK')
list_print(f'{n_xmlcon} arquivos do tipo XMLCON')
list_print(f'{n_con} arquivos do tipo CON')
            
if other > 0:
                
                # Lista para armazenar os nomes dos arquivos que não são .ros ou outros tipos específicos
    list_print(f'Há {other} outros tipos de arquivos:')
    for arquivo in arquivos:
        extensao = Path(arquivo).suffix 
        if extensao not in ['.hex', '.bl', '.hdr', '.mrk', '.XMLCON', '.con', '.CON']:
            list_print(arquivo)
                        

            # Conjunto para manter um registro único de estações
estacoes = set()


arquivos_hex = [arquivo for arquivo in os.listdir(pasta_copia) if arquivo.endswith('.hex')]
            
            # Dicionário para rastrear as estações e suas versões
estacoes_versoes = defaultdict(set)

            # Expressão regular para extrair o número da estação e a versão
expressao = r'(\d{3}[a-zA-Z]*)'  # Procura 3 dígitos seguidos por zero ou mais letras

            # Iterar pelos nomes dos arquivos .hex
for arquivo in arquivos_hex:
                # Use a expressão regular para encontrar o número da estação e a versão
    matches = re.findall(expressao, arquivo)
    if matches:
        estacao = matches[0]
        versao = matches[1] if len(matches) > 1 else 'Versão Padrão'
                    # Adicione esta estação e versão ao dicionário
        estacoes_versoes[estacao].add(versao)
        for match in matches:
            estacoes.add(match)

#**********************************************************************************************************

            # Dicionário para rastrear os tipos de arquivo associados a cada estação e versão
estacoes_tipos_arquivo = defaultdict(dict)
            

            # Imprimir informações sobre os tipos de arquivo para cada estação e versão
            
estações_completas = True
tipos_arquivos = {'.hex', '.bl', '.hdr', '.mrk'}
tipos_faltando = set()
arq_configu = None

for estacao, versoes in estacoes_versoes.items():
    station_files = [f'{estacao}{ext}' for ext in tipos_arquivos]
    missing_files = [file for file in station_files if not any(file in os.path.basename(arq) for arq in arquivos)]

                # Inicialize as variáveis
    con_presente = False
    xmlcon_presente = False

                # Verifique se pelo menos um dos arquivos .con ou .XMLCON está presente na estação
    if n_con > 0:
        con_presente = True
        arq_configu = True
                    
                    
    elif n_xmlcon > 0:
        xmlcon_presente = True
        arq_configu = True
                    
                    
    else:
        estações_completas = False
                                    
    if missing_files:
        estações_completas = False
        tipos_faltando.update([Path(file).suffix for file in missing_files])

    if xmlcon_presente:
        arq_configu =  '%1.XMLCON'
    elif con_presente:
        arq_configu =  '%1.CON'
lista_arquivos = os.listdir(pasta_copia)



            # Lista todos os arquivos na pasta arq_psa
arquivos = os.listdir(caminho_psa)
confere_seaplot = False
confere_teos = False
arquivos_psa = glob.glob(os.path.join(caminho_psa, '*.psa'))

for arquivo in arquivos_psa:
    nome_arquivo = os.path.basename(arquivo)
    termo = nome_arquivo.split('.')[-2].lower() + '.psa'  # Converte o termo para letras minúsculas
    if termo == 'alignctd.psa':
        arq_align = arquivo
    elif termo == 'binavg.psa':
        arq_bin = arquivo
    elif termo == 'bottlesum.psa':
        arq_sum = arquivo
    elif termo == 'celltm.psa':
        arq_cell = arquivo
    elif termo == 'datcnv.psa':
        arq_dat = arquivo
    elif termo == 'derive.psa':
        arq_derive = arquivo
    elif termo == 'deriveteos10' or termo == 'deriveteos_10.psa':
        confere_teos = True
        arq_teos = arquivo
    elif termo == 'filter.psa':
        arq_filter = arquivo
    elif termo == 'loopedit.psa':
        arq_loop = arquivo
    elif termo == 'seaplot.psa' or termo == 'seaplot_autoscale1.psa':
        arq_sea = arquivo
    elif termo == 'seaplot_ts.psa':
        confere_seaplot = True
        arq_ts = arquivo
    elif termo == 'split.psa':
        arq_split = arquivo
    elif termo == 'wildedit.psa':
        arq_wild = arquivo
    elif termo == 'markscan.psa':
        arq_scan = arquivo
    elif termo == 'buoyancy.psa':
        arq_buoy = arquivo
    elif termo == 'w_filter.psa':
        arq_wf = arquivo
    elif termo == 'section.psa':
        arq_section = arquivo
    elif termo == 'strip.psa':
        arq_strip = arquivo
    elif termo == 'trans.psa':
        arq_trans = arquivo

# ***************************************************************************************************
# iniciando o processamento

arquivos_na_pasta = os.listdir(caminho_bat)
        
if len(arquivos_na_pasta) != 1 or not arquivos_na_pasta[0].endswith('.txt'):
    print('Não foi possível determinar o Batch file na pasta.')
    sys.exit()
bat = os.path.join(caminho_bat, arquivos_na_pasta[0])


#input('Por favor, antes de realizar o processamento, confira todas as informações no arquivo de relatório e adicione o que achar necessário. \nPressione Enter quando estiver pronto para realizar o processamento.')

escreve_scan(estacoes_versoes, replace, pasta_copia, tabela_mrk)

process(bat, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes, replace, arq_dat)
split(pasta_split)
proc_finais(pasta_processados, tabela, pasta_relatorio)
end(bat, pasta_split, pasta_processados, tabela, relatorio, pasta_copia, estacoes_versoes, replace, arq_dat, pasta_relatorio)
                    