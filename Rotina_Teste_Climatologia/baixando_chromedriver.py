import os
import zipfile
import requests

def baixar_chromedriver(url, destino):
    try:
        # Faz o download do arquivo zip
        response = requests.get(url)
        with open('chromedriver.zip', 'wb') as f:
            f.write(response.content)
        
        # Extrai o arquivo zip
        with zipfile.ZipFile('chromedriver.zip', 'r') as zip_ref:
            zip_ref.extractall(destino)
        
        # Remove o arquivo zip após extração
        os.remove('chromedriver.zip')
        
        print(f'ChromeDriver baixado e extraído com sucesso em: {destino}')
    except Exception as e:
        print(f'Erro ao baixar e extrair o ChromeDriver: {e}')



def obter_caminho_chromedriver(diretorio_destino):
    # Verifica se o ChromeDriver já está presente no diretório de destino
    chromedriver_path = os.path.join(diretorio_destino, 'chromedriver.exe')
    if os.path.exists(chromedriver_path):
        return chromedriver_path
    else:
        # Se o ChromeDriver não estiver presente, baixa automaticamente
        url_chromedriver = 'https://chromedriver.storage.googleapis.com/94.0.4606.61/chromedriver_win32.zip'
        baixar_chromedriver(url_chromedriver, diretorio_destino)
        return chromedriver_path


# Diretório onde o ChromeDriver será salvo
#diretorio_destino = './chromedriver'

# Obter o caminho do ChromeDriver
#driver_path = obter_caminho_chromedriver(diretorio_destino)

