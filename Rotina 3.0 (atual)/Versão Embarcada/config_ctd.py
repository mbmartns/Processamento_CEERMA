import os
import os
from pathlib import Path
import glob
import shutil


def cria_bat(input_range):
    result = []
    allowed_numbers = set(map(str, range(1, 22)))  # Números permitidos de 1 a 21 como strings

    for part in input_range.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(str.strip, part.split('-'))
            for num in range(int(start), int(end) + 1):
                if 1 <= num <= 21:
                    result.append(str(num).zfill(2))
                else:
                    print(f"O número '{num}' fora do intervalo 1-21 não pode ser processado.")
        else:
            if len(part) <= 2 and part in allowed_numbers:
                result.append(part.zfill(2))
            else:
                num = int(part)
                if 1 <= num <= 21:
                    result.append(str(num).zfill(2))
                else:
                    print(f"O número '{num}' fora do intervalo 1-21 não pode ser processado.")

    return result


def proc_bat(lista_bat): # relaciona os números do processo aos nomes
    
        # Criando o dicionário com os números e nomes correspondentes
    numeros_nomes = {
        '01': 'Data Conversion',
        '02': 'Filter',
        '03': 'Align CTD',
        '04': 'Cell Thermal Mass',
        '05': 'Loop Edit',
        '06': 'Derive',
        '07': 'Derive TEOS-10',
        '08': 'Bin Average',
        '09': 'Bottle Summary',
        '10': 'Mark Scan',
        '11': 'Buoyancy',
        '12': 'Wild Edit',
        '13': 'Window Filter',
        '14': 'ASCII In',
        '15': 'ASCII Out',
        '16': 'Section',
        '17': 'Split',
        '18': 'Strip',
        '19': 'Translate',
        '20': 'Sea Plot',
        '21': 'SeaCalc III'
    }
    
    lista_nome = []
    for numero in lista_bat:
        nome = numeros_nomes.get(numero)
        lista_nome.append(nome)
    return lista_nome


# Obter o nome do usuário
nome_usuario = os.getlogin()

# Obter o caminho da área de trabalho
caminho_area_trabalho = os.path.join(os.path.expanduser('~'), 'Desktop')

# Criar o caminho completo para a pasta "PROCESS_CTD"
caminho_process_ctd = os.path.join(caminho_area_trabalho, 'PROCESS_CTD')

# Criar caminhos para as subpastas
caminho_arquivos_config = os.path.join(caminho_process_ctd, 'Arquivos_Config')
caminho_dados = os.path.join(caminho_process_ctd, 'Dados')
caminho_processados = os.path.join(caminho_process_ctd, 'Processados')


# Criar os diretórios
os.makedirs(caminho_process_ctd, exist_ok=True)
os.makedirs(caminho_arquivos_config, exist_ok=True)
os.makedirs(caminho_dados, exist_ok=True)
os.makedirs(caminho_processados, exist_ok=True)

# Criar subpastas dentro de "Arquivos_Config"
caminho_arquivos_psa = os.path.join(caminho_arquivos_config, 'Arquivos_PSA')
caminho_batch_file = os.path.join(caminho_arquivos_config, 'Batch_File')

# Criar subpastas dentro de "Processados"
caminho_relatorio = os.path.join(caminho_processados, 'Relatório')
caminho_arquivos_btl = os.path.join(caminho_processados, 'Arquivos_BTL')
caminho_processamento_seaplot = os.path.join(caminho_processados, 'Processamento_Seaplot')
caminho_processamento_split = os.path.join(caminho_processados, 'Processamento_Split')

# Criar as subpastas
os.makedirs(caminho_arquivos_psa, exist_ok=True)
os.makedirs(caminho_batch_file, exist_ok=True)
os.makedirs(caminho_relatorio, exist_ok=True)
os.makedirs(caminho_arquivos_btl, exist_ok=True)
os.makedirs(caminho_processamento_seaplot, exist_ok=True)
os.makedirs(caminho_processamento_split, exist_ok=True)

# Criar arquivos de texto em "Relatório"
caminho_txt_relatorio = os.path.join(caminho_relatorio, 'Relatório_de_processamento.txt')
caminho_tabela_relatorio = os.path.join(caminho_relatorio, 'Tabela_de_posição.txt')

# Criar arquivos de texto
with open(caminho_txt_relatorio, 'w') as arquivo_relatorio:
    arquivo_relatorio.write('RELATÓRIO DE DADOS E PROCESSAMENTO\n')
    arquivo_relatorio.write('O relatório presente fornece todas as informações obtidas a partir dos dados brutos.')
    arquivo_relatorio.write('\nPor favor, cheque todas as informações e adicione o que achar relevante para o processamento dos dados.\n')


with open(caminho_tabela_relatorio, 'w') as arquivo_tabela_posicao:
    arquivo_tabela_posicao.write('Nº ESTAÇÃO\tData e Hora\tLatitude\tLongitude\n')


print("Estrutura de pastas criada com sucesso.")



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

# *************************************************************************************************************************************************
print('Por favor, coloque todos os arquivos PSAs necessários para o processamento na pasta Arquivos_PSA que se encontra na pasta "Arquivos_Config"')
print('Confira que os arquivos PSA estão nomeados segundo a nomenclatura padrão do SBEDataProcessing')
input('Pressione Enter após terminar...')


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
# Configurando o Batch   


#def bat(caminho_bat, caminho_psa, relatorio, pasta_processados )        
while True:
    confere_bat = input('Você já possui um Batch File para realizar esse processamento? (s/n)').lower()

    if confere_bat == 's':
        print('Por favor, coloque seu arquivo Batch na pasta Batch_File que se encontra em "Arquivos_Config".')
        print('Faça todas as modificações necessárias e pressione Enter após terminar.')
        input('Pressione Enter para continuar...')
        arquivos_bat = glob.glob(os.path.join(caminho_bat, '*.txt'))
        if not arquivos_bat:
            print('Nenhum arquivo Batch foi encontrado na pasta Batch_file.')
            print('Certifique-se de ter colocado seu arquivo Batch lá.')
            continue 
        else:
                            # Se houver pelo menos um arquivo Batch, assuma que o primeiro é o arquivo personalizado
            bat = arquivos_bat[0]
            print('Por favor, confira se o seu bat está apropriado para o processamento')
            voltar = input('Se estiver tudo certo, pressione Enter. Se deseja refazer o bat, escreva "v" para voltar' )
            if voltar == 'v':
                continue
            else:
                with open(relatorio, 'a') as arq:
                    arq.write('\nDurante o processamento foi utilizado um Batch File já existente.')
                break
            
    if confere_bat == 'n':
        nome_bat = input('Dê nome ao seu batch file (sugestão: batch_nome_do_programa): ') + '.txt'
        bat = os.path.join(caminho_bat, nome_bat)
        os.makedirs(caminho_bat, exist_ok=True)  # Criar diretório Batch_file, se não existir
        name_dir = str(pasta_copia) + '//'
        name_psa = str(caminho_psa) + '//'
        print('Informe quais os números que correspondem aos processamentos que quer realizar')
        print('Exemplo: 01  -  para processar o DatCnv')
        print('Escreva na ordem que achar mais apropriado para seu processamentos')
        input_string = input('Quais processamentos você deseja realizar?')

        lista_bat = cria_bat(input_string)
        lista_nomes = proc_bat(lista_bat)
        replace = input('Digite o nome das estações da operação que serão processadas (da forma que estará na pasta)\nNão inclua o "_": ') + '_'
        print('O arquivo de configuração poderá ser no formato "xmlcon" ou "con"')
        while True:
            configuracao = input('Por favor, digite "1" se caso for xmlcon e "2" para se for con ')
            if configuracao == '1':
                arq_configu =  '%1.XMLCON'
                break
            elif configuracao == '2':
                arq_configu =  '%1.CON'
                break
            else:
                print('Resposta inválida ')

        with open(relatorio, 'a') as arq:
            arq.write(f'\n\nDurante o processamento foi criado um novo Batch File, chamado {nome_bat}.\n')
            arq.write('O Batch File utilizado está configurado para realizar os seguintes processamentos:\n')
            for i in lista_nomes:
                arq.write('\n' + i)
                
        dat_cnv = False
        
        for i in lista_bat:
            if i == '01':
                with open(bat, 'w') as arquivo:
                    arquivo.write('datcnv  /i' + str(name_dir) + str(replace) + '%1.hex' + ' ' + '/p' + str(name_psa) + 'datcnv.psa' + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + arq_configu )
                dat_cnv = True
            if i == '02':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nfilter  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'filter.psa' + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
            if i == '03':   
                with open(bat, 'a') as arquivo: 
                    arquivo.write('\nalignctd  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'alignctd.psa' + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
            if i == '04':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\ncelltm  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'celltm.psa'  + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
            if i == '05':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nloopedit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'loopedit.psa' + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
            if i == '06':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nderive  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'derive.psa' + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + arq_configu )
            if i == '07':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nDeriveTEOS10  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'deriveteos_10.psa' + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados) + ' /c' + str(name_dir + replace) + arq_configu )
            if i == '08':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nbinavg  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'binavg.psa' +  ' /f' + replace + '%1.cnv' + ' /o' + str(pasta_processados))
            if i == '10':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nmarkscan /i' + str(name_dir) + str(replace) + '%1.mrk' + ' ' + '/p' + str(name_psa) + 'markscan.psa' + ' /f' + replace + '%1.bsr' + ' /o' +  str(pasta_processados))
            if i == '11':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nbuoyancy  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'buoyancy.psa' + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
            if i == '13':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nwfilter  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'w_filter.psa' +  ' /f' + replace + '%1.cnv' + ' /o' + str(pasta_processados))
            if i == '12':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nwildedit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'wildedit.psa' + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
            if i == '17':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nsplit  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'split.psa' +  ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_split))
            if i == '18':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nstrip  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'strip.psa' + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
            if i == '19':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\ntrans  /i' + str(pasta_processados) + '//' + str(replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'trans.psa' + ' /f' + replace + '%1.cnv' + ' /o' +  str(pasta_processados))
            if i == '20':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nseaplot  /i' + str(pasta_split) + '//' + str('d'+replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'seaplot.psa' + ' /f' + replace + '%1.jpg' + ' /o' +  str(pasta_plot))
                confere_seaplot = input('Você gostaria de fazer o processamento do seaplot_ts? (s/n)\nCaso sua escolha for "s", coloque o seaplot_ts.psa, dessa forma, nos Arquivos_PSA.').lower()
                if confere_seaplot == 's':
                    with open(bat, 'a') as arquivo:
                        arquivo.write('\nseaplot  /i' + str(pasta_split) + '//' + str('d'+replace) + '%1.cnv' + ' ' + '/p' + str(name_psa) + 'seaplot_ts.psa' + ' /f' + replace + '%1.jpg' + ' /o' +  str(pasta_plot))
            if i == '09':
                with open(bat, 'a') as arquivo:
                    arquivo.write('\nbottlesum  /i' + str(pasta_processados) + '//' + str(replace) + '%1.ros' + ' ' + '/p' + str(name_psa) + 'bottlesum.psa' + ' /f' + replace + '%1.BTL' + ' /o' + str(caminho_garrafa) + ' /c' + str(name_dir + replace) + arq_configu)
        break
    else:
        print('Resposta inválida. Por favor, responda com "s" para sim ou "n" para não.')
  
  
print("Configuração do Batch concluído com sucesso.")
print("Sua estrutura está pronta para realizar o processamento.")
print('Por favor, antes de processar, coloque os Dados na pasta de dados e confira todos os PSAs')

  
#  def confere_psa()           passo adicional