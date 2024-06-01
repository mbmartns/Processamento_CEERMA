import os
import shutil


# Função para ler uma linha de cada arquivo de texto e escrever em um novo arquivo
def ler_linha_de_cada_arquivo(diretorio_origem, diretorio_destino):
    # copia Lista todos os arquivos copiados
    shutil.copytree(diretorio_origem, diretorio_destino)
    arquivos = os.listdir(diretorio_destino)
    
    # Abre o arquivo de destino para escrita
    #with open(os.path.join(diretorio_destino, 'resultado.txt'), 'w') as arquivo_destino:
    # Itera sobre todos os arquivos de texto no diretório de origem
    for arquivo in arquivos:
        print(f'Tratando informações do arquivo {arquivo}')
        if arquivo.endswith('.cnv'):  # Verifica se é um arquivo de texto
            caminho_arquivo = os.path.join(diretorio_destino, arquivo)
            encontrou_indicador = False
            linhas_restantes = []

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

# depois que ler e copiar em um arquivo só, com todos os dados
#faço um novo arquivo chamado de resultado, ou dados tratados...
#nesse novo arquivo, leio o arquivo de todos os dados e, caso a coluna x e z for menor que 0.005, eu copio a linha e colo no arquivo de resultado
#também printo se houver alguma linha em que o numero for maior, ou só indico que foi.
