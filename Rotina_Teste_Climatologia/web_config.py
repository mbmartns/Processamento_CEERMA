from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
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

def obter_arquivos(nome_teste, meses, url):

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
    driver.get(url)
    time.sleep(2)
    caminhos_arquivos = [] #lista com os caminhos de todos os arquivos extraídos

    # Função para clicar nos links dos meses fornecidos
    def clicar_links_meses(meses, nome_teste):
        mes_map = {
            'Jan': 'January',
            'Feb': 'February',
            'Mar': 'March',
            'Apr': 'April',
            'May': 'May',
            'Jun': 'June',
            'Jul': 'July',
            'Aug': 'August',
            'Sep': 'September',
            'Oct': 'October',
            'Nov': 'November',
            'Dec': 'December'
        }
        for mes_abreviado in meses:

            mes_completo = mes_map[mes_abreviado]
            link_mes = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, f'//a[contains(text(), "Monthly - {mes_completo}")]'))
            )
            link_mes.click()
            #time.sleep(2)  # Esperar um pouco antes de clicar no próximo link
                # Esperar o tempo necessário para o download completar
            time.sleep(15)

            # Verificar se o arquivo foi baixado

            files = os.listdir(download_dir)
            print("Arquivos baixado:", files)

            if files:
                caminho_arquivo = os.path.join(download_dir, files[0])  # Pegue o primeiro arquivo na lista

                #caminho_arquivo = os.path.join(download_dir, file)
                diretorio_destino = './extraido/'
                os.makedirs(diretorio_destino, exist_ok=True)

                    # Chama a função para extrair o arquivo .gz
                caminho_arquivo_descompactado = extrair_arquivo_gz(caminho_arquivo, diretorio_destino, nome_teste, mes_abreviado)
                
                time.sleep(15)

                # Deleta o arquivo baixado após extração
                os.remove(caminho_arquivo)

                caminhos_arquivos.append(caminho_arquivo_descompactado)

    try:
        # Tenta encontrar e clicar na opção "1/4°"
        opcao_1_4 = driver.find_element(By.XPATH, '//input[@value="0.25"]')
        opcao_1_4.click()
        print("Opção 1/4° selecionada.")
    except NoSuchElementException:
        try:
            # Se não encontrar a opção "1/4°", tenta encontrar a opção "1°"
            opcao_1 = driver.find_element(By.XPATH, '//input[@value="1.00"]')
            opcao_1.click()
            print("Opção 1° selecionada.")
        except NoSuchElementException:
            pass

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
        if option.text == 'Objectively analyzed standard deviation':
           # Standard deviations
           #Objectively analyzed standard deviation
            option.click()
            break

    time.sleep(2)

    # Clicar no botão "Update data links"
    update_button = driver.find_element(By.CSS_SELECTOR, "button[name='updatedataLinks']")
    update_button.click()

    time.sleep(6)
    clicar_links_meses(meses, nome_teste)
    return caminhos_arquivos

    # Encontrar e clicar no link "Annual"
    #link_anual = driver.find_element(By.XPATH, '//a[contains(text(), "Annual")]')
    #link_anual.click()

     # Esperar pelo link "Annual" ser clicável
    #link_anual = WebDriverWait(driver, 20).until(
    #     EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Annual")]'))
    # )
    #link_anual.click()


    print('all done')

    # Adicionar mais ações conforme necessário...
    driver.quit()



if __name__ == "__main__":
    meses = ['Oct', 'Jan', 'Nov']
    obter_arquivos("Tempe_oasd", meses, 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23.pl?parameterOption=t')
    #obter_arquivos("Sali_", meses, 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23.pl?parameterOption=s')