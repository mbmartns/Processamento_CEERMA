from global_land_mask import globe
import os
import shutil
import datetime
import re
import time



nomes_colunas = None
indice_colunas = {}

def extrair_nomes_colunas(caminho_arquivo):

    indice_colunas = {}
    colunas = '\t'
    
    with open(caminho_arquivo, 'r') as file:
        for linha in file:
            # Verifica se a linha começa com "# name"
            if linha.startswith('# name'):
                # Utiliza regex para capturar o nome da coluna antes do ":"
                match = re.search(r'# name \d+ = ([^:]+):', linha)
                if match:
                    nome_coluna = match.group(1).strip()
                    if nome_coluna == 'latitude':
                        nome_coluna = 'lat'
                    if nome_coluna == 'longitude':
                        nome_coluna = 'long'
                    colunas += f'{nome_coluna}\t'
                partes = linha.split(" = ")
                indice = int(partes[0].split(" ")[2])
                nome = partes[1].strip()
                indice_colunas[indice] = nome
    
    return colunas, indice_colunas


def calcular_julian_days(ano, mes, dia, hora, minuto, segundo):

    # Criar o objeto datetime
    data_hora = datetime.datetime(ano, mes, dia, hora, minuto, segundo, tzinfo=datetime.timezone.utc)    
    # Data e hora base para Julian Day (1 de Janeiro de 4713 a.C.)
    data_base = datetime.datetime(4713, 1, 1, 12, 0, 0, 0, datetime.timezone.utc)
    
    # Calcular a diferença em dias
    delta = data_hora - data_base
    julian_days = delta.days + delta.seconds / 86400
    # Fórmula para calcular Julian Day
    julian_day = data_hora.toordinal() + 1721424.5 + (hora + minuto / 60 + segundo / 3600) / 24
    
    return julian_day

def encontrar_indice_coluna(nome_coluna):
    global indice_colunas
    for indice, nome in indice_colunas.items():
        if nome_coluna in nome:
            return indice


# Função para ler uma linha de cada arquivo de texto e escrever em um novo arquivo
def ler_linha_de_cada_arquivo(diretorio_origem, diretorio_destino):

    global nomes_colunas  # Indica que vamos usar a variável global
    global indice_colunas

    # copia Lista todos os arquivos copiados
    valores_jd = []

    for arquivo in os.listdir(diretorio_origem):
        caminho_arquivo_origem = os.path.join(diretorio_origem, arquivo)
        caminho_arquivo_destino = os.path.join(diretorio_destino, arquivo)

        # Verifica se é um arquivo
        if os.path.isfile(caminho_arquivo_origem):
            # Copia o arquivo para o diretório de destino
            shutil.copy(caminho_arquivo_origem, caminho_arquivo_destino)

    arquivos = os.listdir(diretorio_destino)

        # Abre o arquivo de destino para escrita
    # Itera sobre todos os arquivos de texto no diretório de origem
    for arquivo in arquivos:
        if arquivo.endswith('.cnv'):  # Verifica se é um arquivo de texto
            caminho_arquivo = os.path.join(diretorio_destino, arquivo)
            encontrou_indicador = False
            linhas_restantes = []
            print(f'Tratando informações do arquivo {arquivo}')

            if nomes_colunas == None:
                nomes_colunas, indice_colunas = extrair_nomes_colunas(caminho_arquivo)


            # Abre cada arquivo de texto
            with open(caminho_arquivo, 'r') as arquivo_origem:

                # Lê cada linha do arquivo
                for linha in arquivo_origem:

                    if linha.startswith("* NMEA UTC (Time) = "):
                        # Extrair a parte da data e hora da linha
                        data_hora_str = linha.split('= ')[1].strip()
                        #print(data_hora_str)
                        # Converter a string para um objeto datetime
                        data_hora = datetime.datetime.strptime(data_hora_str, '%b %d %Y %H:%M:%S')
                        #print(data_hora)
                        
                        # Extrair ano, mês, dia, hora, minuto e segundo
                        ano = data_hora.year
                        mes = data_hora.month
                        dia = data_hora.day
                        hora = data_hora.hour
                        minuto = data_hora.minute
                        segundo = data_hora.second

                        julian_days = calcular_julian_days(ano, mes, dia, hora, minuto, segundo)
                        valores = f'{arquivo}\t\t\t\t\t{julian_days}\t\t\t\t\t{data_hora_str}'

                        valores_jd.append(valores)

                        # Se encontrarmos o indicador, definimos a variável de controle como True
                    if linha.strip() == '*END*':
                        encontrou_indicador = True
                    # Se encontramos o indicador e a linha não é o próprio indicador, escrevemos no arquivo de destino
                    elif encontrou_indicador:
                        linhas_restantes.append(linha)

                        # Se não encontramos o indicador, continuamos para a próxima linha
                    else:
                        continue
                # Escreve as linhas restantes no arquivo original
            with open(caminho_arquivo, 'w') as arquivo_origem:
                arquivo_origem.write('Test 1 => T2-T190C: Temperature Difference, 2 - 1 [ITS-90, deg C] < 0.005\nTest 2 => C2-C1S/m: Conductivity Difference, 2 - 1 [S/m] < 0.005' + 
                                     '\nTest 3 => Impossible Locations Test (-90 <= lat <= 90) & (-180 <= long <= 180)' +
                                     '\nTest 4 => Position on land Test' +
                                     '\nTest 5 => Stuck Value Test' +
                                     '\nTest 6 => Global Range Test' +
                                     '\nTest 7 => Spike Test for Temperature' +
                                     '\nTest 8 => Spike Test for Salinity\n' +
                                     "\nFlags: '1' - Good Data     '2' - Probably Good Data    '3' - Probably Bad Data     '4' - Bad Data\n\n\n")
               
               #precisa ser injetada pra baixo!!!!
                for linha in linhas_restantes:
                    arquivo_origem.write(linha)
    with open(os.path.join(diretorio_destino, 'Julian_Days.txt'), 'w') as arquivo_jd:
        arquivo_jd.write('Arquivo\t\t\t\t\t\t\tJulian Day\t\t\t\t\t\tNMEA UTC (Time)\n')
        for valores in valores_jd:
            arquivo_jd.write(f'{valores}\n')
            


def conferir_dados(diretorio_destino, diretorio_qc):

    with open(os.path.join(diretorio_destino, 'resultado.txt'), 'w') as arquivo_destino:
        arquivo_destino.write('Arquivo\t\t\tT>0.005\t\tC>0.005\n')


    arquivos = os.listdir(diretorio_destino)
    for arquivo in arquivos:
        linhas_validas = []

        valores_temp_maior = []
        valores_cond_maior = []

        caminho_arquivo = os.path.join(diretorio_destino, arquivo)
        
        if arquivo.endswith('.cnv'):  # Verifica se é um arquivo de texto


            with open(caminho_arquivo, 'r+') as cnv_tratado:


                # Lê cada linha do arquivo e armazena em uma lista
                linhas = cnv_tratado.readlines()
                linhas_limpas = []


                # Retorna ao início do arquivo
                cnv_tratado.seek(0)

                spike_t1 = None
                spike_t2 = None
                spike_t3 = None
                spike_s1 = None
                spike_s2 = None
                spike_s3 = None


                    # Iterar sobre as linhas do arquivo
                for i in range(len(linhas)):
                    linha = str(linhas[i])


                # Percorre cada linha armazenada

                            # Verifica se a linha começa com "Test"
                    if linha.startswith("Test") or linha.startswith("Flags"):
                    # Se começar com "Test", pule esta linha
                        cnv_tratado.write(linha)

                        continue

                    # Divide a linha em colunas usando espaços como delimitador
                    colunas = linha.split()
                    resultado_impossible = '\t'
                    resultado_1 = '\t'
                    resultado_2 = '\t'
                    resultado_4 = '\t'
                    resultado_5 = '\t'
                    resultado_6 = '\t'
                    resultado_7 = '\t'
                    resultado_8 = '\t'

                    qc_remove = False
                    
                    if len(colunas) >= 16: #and colunas[10].replace('.', '').isdigit():

                        valor_temp = float(colunas[10])
                        valor_cond = float(colunas[16])
                        valor_temp = abs(valor_temp)
                        valor_cond = abs(valor_cond)


                        valor_sal = float(colunas[17])
                        valor_pres = float(colunas[6])


                        valor_lat = float(colunas[2])
                        valor_long = float(colunas[3])
                        valor_lat = valor_lat
                        valor_long = valor_long


                        resultado_1 = '\t'
                        resultado_2 = '\t'
                        resultado_impossible = '\t'
                        resultado_4 = '\t'
                        resultado_5 = '\t'
                        resultado_6 = '\t'
                        resultado_7 = '\t'
                        resultado_8 = '\t'

                        if (spike_t1 == None):
                            spike_t1 = float(colunas[8])
                            spike_s1 = float(colunas[17])
                            resultado_7 += '2'
                            resultado_8 += '2'


                        else:
                            if i < (len(linhas) - 1):
                                linha_posterior = str(linhas[i + 1])
                                colunas_post = linha_posterior.split()

                                spike_t2 = float(colunas[8])
                                spike_t3 = float(colunas_post[8])
                                spike_test = abs(spike_t2 - (spike_t3 + spike_t1)/2) - abs((spike_t3 - spike_t1)/2)
                                spike_t1 = spike_t2

                                spike_s2 = float(colunas[17])
                                spike_s3 = float(colunas_post[17])
                                spike_test_sal = abs(spike_s2 - (spike_s3 + spike_s1)/2) - abs((spike_s3 - spike_s1)/2)
                                spike_s1 = spike_s2
                                if valor_pres < 500:
                                    if spike_test > 6:
                                        resultado_7 += '4'
                                        qc_remove = True

                                    else:
                                        resultado_7 += '1'

                                    if spike_test_sal > 0.9:
                                        resultado_8 += '4'
                                        qc_remove = True
                                    else:
                                        resultado_8 += '1'

                                else:
                                    if spike_test > 2:
                                        resultado_7 += '4'
                                        qc_remove = True
                                    else:
                                        resultado_7 += '1'


                                    if spike_test_sal > 0.3:
                                        resultado_8 += '4'
                                        qc_remove = True

                                    else:
                                        resultado_8 += '1'

                            else:
                                resultado_7 += '2'
                                resultado_8 += '2'



                                
                        if (valor_pres < -5):
                            resultado_6 += '4'
                            qc_remove = True
                        elif -5 < valor_pres < -2.4:
                            resultado_6 += '3'
                            qc_remove = True
                        elif (2 < valor_sal < 41.0) and (-2.5 <= valor_temp <= 40):
                            resultado_6 += '1'
                        

                        if valor_temp == valor_sal:
                            resultado_5 += '4'
                            qc_remove = True
                        else:
                            resultado_5 += '1'
                        
                        if globe.is_land(valor_lat, valor_long):
                            resultado_4 += '4'
                            qc_remove = True
                        else:
                            resultado_4 += '1'



                        if -90 <= valor_lat <= 90 and -180 <= valor_long <= 180:

                            resultado_impossible += '1'
                        else:
                            resultado_impossible += '4'
                            qc_remove = True

                        # Verifica se o valor é maior que 0.005 e atualiza a linha
                        if valor_temp > 0.005:
                            valores_temp_maior.append(valor_temp)

                            resultado_1 += '4'
                            qc_remove = True

                        else:
                            resultado_1 += '1'


                        if valor_cond > 0.005:
                            valores_cond_maior.append(valor_cond)
                            resultado_2 += '4'
                            qc_remove = True

                        else:
                            resultado_2 += '1'

                        linha = linha.rstrip('\n') + resultado_1 + resultado_2 + resultado_impossible + resultado_4 + resultado_5 + resultado_6 + resultado_7 + resultado_8 + '\n'

                        if qc_remove == False:
                            linhas_limpas.append(linha)

                    # Escreve a linha modificada de volta no arquivo
                    cnv_tratado.write(linha)

            
            criar_arquivo_qc(linhas_limpas, diretorio_qc, arquivo)



        qtt_temp = len(valores_temp_maior)
        qtt_cond = len(valores_cond_maior)
        
        if qtt_temp > 0 or qtt_cond > 0:

            with open(os.path.join(diretorio_destino, 'resultado.txt'), 'a') as arquivo_destino:
                arquivo_destino.write(f'{arquivo}\t\t{qtt_temp}\t\t{qtt_cond}\n')
                if qtt_temp > 0 and qtt_cond > 0:
                    arquivo_destino.write(f'Valores de temperatura > 0.005 = {valores_temp_maior}\n')
                    arquivo_destino.write(f'Valores de condutividade > 0.005 = {valores_cond_maior}\n')
                elif qtt_temp > 0:
                    arquivo_destino.write(f'Valores de temperatura > 0.005 = {valores_temp_maior}\n')
                elif qtt_cond > 0:
                    arquivo_destino.write(f'Valores de condutividade > 0.005 = {valores_cond_maior}\n')



def criar_arquivo_qc(linhas_limpas, diretorio_qc, arquivo):

    global nomes_colunas  # Indica que vamos usar a variável global

    caminho_arquivo = os.path.join(diretorio_qc, arquivo)
    with open(caminho_arquivo, 'w') as novo_arquivo:
        novo_arquivo.write(f'{nomes_colunas}' + f'Test 1\tTest 2\tTest 3\tTest 4\tTest 5\tTest 6\tTest 7\tTest 8\n')
        for linha in linhas_limpas:
            novo_arquivo.write(linha)  # Você pode escrever algum conteúdo se desejar



novo_pos_processamento = input('Já possui a pasta de pós-processamento? (s/n)').lower()

if novo_pos_processamento == 's':
    pasta_pos_proc = input('Digite o caminho da pasta de pós-processamento: ')
    diretorio_origem = os.path.join(pasta_pos_proc, 'Dados')
    diretorio_destino = os.path.join(pasta_pos_proc, 'Dados_Flags')
    diretorio_qc = os.path.join(pasta_pos_proc, 'Quality_Control')

    # Criar os diretórios
    os.makedirs(diretorio_origem, exist_ok=True)
    os.makedirs(diretorio_destino, exist_ok=True)
    os.makedirs(diretorio_qc, exist_ok=True)


elif novo_pos_processamento == 'n':

    nome_pos_proc = input('Digite o nome da pasta de pós-processamento: ')
    # Obter o nome do usuário
    nome_usuario = os.getlogin()
    # Obter o caminho da área de trabalho
    caminho_area_trabalho = os.path.join(os.path.expanduser('~'), 'Desktop')
    print(caminho_area_trabalho)
    # Criar o caminho completo para a pasta
    pasta_pos_proc = os.path.join(caminho_area_trabalho, nome_pos_proc)
    diretorio_origem = os.path.join(pasta_pos_proc, 'Dados')
    diretorio_destino = os.path.join(pasta_pos_proc, 'Dados_Flags')
    diretorio_qc = os.path.join(pasta_pos_proc, 'Quality_Control')

    # Criar os diretórios
    os.makedirs(pasta_pos_proc, exist_ok=True)
    os.makedirs(diretorio_origem, exist_ok=True)
    os.makedirs(diretorio_destino, exist_ok=True)
    os.makedirs(diretorio_qc, exist_ok=True)

input('Por favor, confira que todos os dados que quer tratar estejam na pasta de "Dados".\nPressione Enter após conferência.')
ler_linha_de_cada_arquivo(diretorio_origem, diretorio_destino)
conferir_dados(diretorio_destino, diretorio_qc)

# depois que ler e copiar em um arquivo só, com todos os dados
#faço um novo arquivo chamado de resultado, ou dados tratados...
#nesse novo arquivo, leio o arquivo de todos os dados e, caso a coluna x e z for menor que 0.005, eu copio a linha e colo no arquivo de resultado
#também printo se houver alguma linha em que o numero for maior, ou só indico que foi.