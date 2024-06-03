from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from baixando_chromedriver import *
from extraindo_arquivo import *
import os
import time


def config_chrome():

    diretorio_destino = './chromedriver'
    os.makedirs(diretorio_destino, exist_ok=True)

    driver_path = obter_caminho_chromedriver(diretorio_destino)

    # Diretório onde os arquivos serão baixados
    download_dir = os.path.abspath('./downloads')
    os.makedirs(download_dir, exist_ok=True)

    options = Options()
    options.add_argument("--headless")  # Executa o Chrome no modo headless (sem interface gráfica)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # Desabilita a GPU (necessário em alguns sistemas)
    prefs = {
        "download.default_directory": download_dir,  # Definir o diretório de download
        "download.prompt_for_download": False,  # Não pedir confirmação para download
        "directory_upgrade": True
    }
    options.add_experimental_option("prefs", prefs)

    # Configuração do serviço do ChromeDriver
    service = Service(driver_path)

    # Iniciar o WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),  options=options)
    return driver

def obter_arquivos(meses, url):

    diretorio_destino = './chromedriver'
    os.makedirs(diretorio_destino, exist_ok=True)

    driver_path = obter_caminho_chromedriver(diretorio_destino)

    # Diretório onde os arquivos serão baixados
    download_dir = os.path.abspath('./downloads')
    os.makedirs(download_dir, exist_ok=True)

    options = Options()
    options.add_argument("--headless")  # Executa o Chrome no modo headless (sem interface gráfica)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # Desabilita a GPU (necessário em alguns sistemas)
    prefs = {
        "download.default_directory": download_dir,  # Definir o diretório de download
        "download.prompt_for_download": False,  # Não pedir confirmação para download
        "directory_upgrade": True
    }
    options.add_experimental_option("prefs", prefs)

    # Configuração do serviço do ChromeDriver
    service = Service(driver_path)

    # Iniciar o WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),  options=options)


    #driver = config_chrome()
    #url = 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23.pl?parameterOption=t'
    driver.get(url)
    time.sleep(2)

    # Encontrar e clicar no botão de opção "1/4°"
    opcao_1_4 = driver.find_element(By.XPATH, '//input[@value="0.25"]')
    opcao_1_4.click()

    # Encontrar e clicar no botão de opção "CSV"
    opcao_csv = driver.find_element(By.XPATH, '//input[@id="inlineRadiocsv"]')
    opcao_csv.click()

    # Encontrar o elemento select para o campo "Available climatological time periods"
    select_time_periods = driver.find_element(By.NAME, 'decadesOption')

    # Selecionar a última opção
    options = select_time_periods.find_elements(By.TAG_NAME, 'option')
    ultima_opcao = options[-1]
    ultima_opcao.click()

        
    # Encontrar o elemento select para o campo "Available fields"
    select_available_fields = driver.find_element(By.NAME, 'climatologyOption')

    # Selecionar a opção "Statistical mean"
    for option in select_available_fields.find_elements(By.TAG_NAME, 'option'):
        if option.text == 'Statistical mean':
            option.click()
            break

    time.sleep(2)

    # Clicar no botão "Update data links"
    update_button = driver.find_element(By.CSS_SELECTOR, "button[name='updatedataLinks']")
    update_button.click()

    time.sleep(6)
    # Encontrar e clicar no link "Annual"
    link_anual = driver.find_element(By.XPATH, '//a[contains(text(), "Annual")]')
    link_anual.click()

     # Esperar pelo link "Annual" ser clicável
    link_anual = WebDriverWait(driver, 20).until(
         EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Annual")]'))
     )
    link_anual.click()

    # Esperar o tempo necessário para o download completar
    time.sleep(15)

    print('all done')

    # Adicionar mais ações conforme necessário...
    driver.quit()

    # Verificar se o arquivo foi baixado
    files = os.listdir(download_dir)
    print("Arquivos baixados:", files)

    for file in files:
        caminho_arquivo = os.path.join(download_dir, file)
        diretorio_destino = './extraido/'
        os.makedirs(diretorio_destino, exist_ok=True)

        # Chama a função para extrair o arquivo .gz
        caminho_arquivo_descompactado = extrair_arquivo_gz(caminho_arquivo, diretorio_destino)

        # Exemplo de uso do arquivo extraído
        if caminho_arquivo_descompactado:
            print(f'O arquivo extraído está em: {caminho_arquivo_descompactado}')
        else:
            print('Falha ao extrair o arquivo.')

if __name__ == "__main__":
    meses = ['Oct', 'Jan', 'Nov']
#obter_arquivos(meses, 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23.pl?parameterOption=t')