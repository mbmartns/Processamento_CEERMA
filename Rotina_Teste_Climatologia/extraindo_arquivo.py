import gzip
import shutil
import os

def extrair_arquivo_gz(caminho_arquivo, diretorio_destino, mes_abreviado):
    try:
        # Obtém o nome base do arquivo (sem o diretório)
        nome_arquivo = os.path.basename(caminho_arquivo)

        # Remove a extensão .gz para obter o nome do arquivo descompactado
        nome_arquivo_descompactado = nome_arquivo.replace('.gz', '')
        caminho_arquivo_descompactado = os.path.join(diretorio_destino, nome_arquivo_descompactado)

        # Abre o arquivo .gz e o arquivo de saída
        with gzip.open(caminho_arquivo, 'rb') as f_in:
            with open(caminho_arquivo_descompactado, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f'Arquivo extraído com sucesso para {caminho_arquivo_descompactado}')

            # Renomeia o arquivo descompactado para o nome do mês abreviado
        novo_caminho_arquivo = os.path.join(diretorio_destino, f"{mes_abreviado}.csv")
        os.rename(caminho_arquivo_descompactado, novo_caminho_arquivo)


        return novo_caminho_arquivo
    except FileNotFoundError:
        print('Erro: Arquivo ou diretório não encontrado.')
    except PermissionError:
        print('Erro: Permissão negada.')
    except Exception as e:
        print(f'Erro inesperado ao extrair o arquivo: {e}')
        return None
    
    
if __name__ == "__main__":
    diretorio_destino = './extraido/'
    extrair_arquivo_gz(f'C:\\Users\\comet\\Desktop\\Processamento_CEERMA\\downloads\\woa23_B5C2_t01mn04.csv.gz', diretorio_destino )