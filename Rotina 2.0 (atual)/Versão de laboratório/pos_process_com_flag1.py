import os
import shutil


# Função para ler uma linha de cada arquivo de texto e escrever em um novo arquivo
def ler_linha_de_cada_arquivo(diretorio_origem, diretorio_destino):
    # copia Lista todos os arquivos copiados
    #shutil.copytree(diretorio_origem, diretorio_destino)
    #arquivos = os.listdir(diretorio_destino)

    for arquivo in os.listdir(diretorio_origem):
        caminho_arquivo_origem = os.path.join(diretorio_origem, arquivo)
        caminho_arquivo_destino = os.path.join(diretorio_destino, arquivo)

        # Verifica se é um arquivo
        if os.path.isfile(caminho_arquivo_origem):
            # Copia o arquivo para o diretório de destino
            shutil.copy(caminho_arquivo_origem, caminho_arquivo_destino)
            #print(f'Arquivo "{arquivo}" copiado para "{diretorio_destino}".')

    arquivos = os.listdir(diretorio_destino)

        # Abre o arquivo de destino para escrita
    #with open(os.path.join(diretorio_destino, 'resultado.txt'), 'w') as arquivo_destino:
    # Itera sobre todos os arquivos de texto no diretório de origem
    for arquivo in arquivos:
        if arquivo.endswith('.cnv'):  # Verifica se é um arquivo de texto
            caminho_arquivo = os.path.join(diretorio_destino, arquivo)
            encontrou_indicador = False
            linhas_restantes = []
            print(f'Tratando informações do arquivo {arquivo}')


            # Abre cada arquivo de texto
            with open(caminho_arquivo, 'r') as arquivo_origem:

                # Lê cada linha do arquivo
                for linha in arquivo_origem:
                        # Se encontrarmos o indicador, definimos a variável de controle como True
                    if linha.strip() == '*END*':
                        encontrou_indicador = True
                    # Se encontramos o indicador e a linha não é o próprio indicador, escrevemos no arquivo de destino
                    elif encontrou_indicador:
                        linhas_restantes.append(linha)

                            #arquivo_destino.write(linha)
                        # Se não encontramos o indicador, continuamos para a próxima linha
                    else:
                        continue
                # Escreve as linhas restantes no arquivo original
            with open(caminho_arquivo, 'w') as arquivo_origem:
                for linha in linhas_restantes:
                    arquivo_origem.write(linha)

def conferir_dados(diretorio_destino):
#def encontrar_valores_maiores_que_0_005(caminho_arquivo):
    with open(os.path.join(diretorio_destino, 'resultado.txt'), 'w') as arquivo_destino:
        arquivo_destino.write('Arquivo\t\t\tT>0.005\t\tC>0.005\n')

    arquivos = os.listdir(diretorio_destino)
    for arquivo in arquivos:
        linhas_validas = []

        valores_temp_maior = []
        valores_cond_maior = []

        caminho_arquivo = os.path.join(diretorio_destino, arquivo)
        
        if arquivo.endswith('.cnv'):  # Verifica se é um arquivo de texto

            # Abre o arquivo e lê linha por linha
            with open(caminho_arquivo, 'r') as cnv_tratado:

                for linha in cnv_tratado:
                    # Divide a linha em colunas usando espaços como delimitador
                    colunas = linha.split()

                    # Verifica se existem pelo menos 10 colunas e se a décima coluna é um número
                    if len(colunas) >= 10 and colunas[10].replace('.', '').isdigit():
                        valor_temp = float(colunas[10])
                        valor_cond = float(colunas[16])
                        #print(valor_cond)
                        # Verifica se o valor é maior que 0.005
                        if valor_temp > 0.005:
                            #print(valor)
                            valores_temp_maior.append(valor_temp)
                        if valor_cond > 0.005:
                            #print(valor_cond)
                            valores_cond_maior.append(valor_cond)
                    # Verifica se o valor é maior que 0.005
                        if valor_temp <= 0.005 and valor_cond <= 0.005:
                        # Se não for, adiciona a linha à lista de linhas válidas
                            linhas_validas.append(linha)
            # Reescreve o arquivo apenas com as linhas válidas
            with open(caminho_arquivo, 'w') as cnv_tratado:
                for linha in linhas_validas:
                    cnv_tratado.write(linha)
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

       # return valores_maiores_que_0_005




novo_pos_processamento = input('Já possui a pasta de pré-processamento? (s/n)').lower()
#print(novo_pos_processamento)
if novo_pos_processamento == 's':
    pasta_pos_proc = input('Digite o caminho da pasta de pós-processamento: ')
    diretorio_origem = os.path.join(pasta_pos_proc, 'Dados')
    diretorio_destino = os.path.join(pasta_pos_proc, 'Dados_Tratados')

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
    diretorio_destino = os.path.join(pasta_pos_proc, 'Dados_Tratados')
    # Criar os diretórios
    os.makedirs(pasta_pos_proc, exist_ok=True)
    os.makedirs(diretorio_origem, exist_ok=True)
    os.makedirs(diretorio_destino, exist_ok=True)

input('Por favor, confira que todos os dados que quer tratar estejam na pasta de "Dados".\nPressione Enter após conferência.')
ler_linha_de_cada_arquivo(diretorio_origem, diretorio_destino)
conferir_dados(diretorio_destino)

# depois que ler e copiar em um arquivo só, com todos os dados
#faço um novo arquivo chamado de resultado, ou dados tratados...
#nesse novo arquivo, leio o arquivo de todos os dados e, caso a coluna x e z for menor que 0.005, eu copio a linha e colo no arquivo de resultado
#também printo se houver alguma linha em que o numero for maior, ou só indico que foi.
