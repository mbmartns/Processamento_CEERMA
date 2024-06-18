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
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
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

    def verificar_download_completo(filepath):
        while True:
            if not os.path.exists(filepath):
                time.sleep(1)
                continue
            if not filepath.endswith('.crdownload'):
                break
            time.sleep(1)

    def clicar_e_baixar(mes_completo, nome_teste, mes_abreviado, opcao_text):
        try:
            # Selecionar a opção especificada (ex: 'Standard error of the analysis' ou 'Objectively analyzed mean')
            select_available_fields = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, 'climatologyOption'))
            )
            for option in select_available_fields.find_elements(By.TAG_NAME, 'option'):
                if option.text == opcao_text:
                    option.click()
                    break

            # Clicar no botão "Update data links"
            update_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name='updatedataLinks']"))
            )
            update_button.click()
            time.sleep(2) #esperar o update funcionar


            link_mes = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, f'//a[contains(text(), "Monthly - {mes_completo}")]'))
            )
            link_mes.click()

            # Esperar até que o arquivo esteja disponível para extração
            while True:
                files = os.listdir(download_dir)
                if files:
                    caminho_arquivo = os.path.join(download_dir, files[0])  # Pegue o primeiro arquivo na lista
                    if not caminho_arquivo.endswith('.crdownload'):
                        break
                time.sleep(1)

            verificar_download_completo(caminho_arquivo)

                # Chama a função para extrair o arquivo .gz
            diretorio_destino = './extraido/'
            os.makedirs(diretorio_destino, exist_ok=True)
            caminho_arquivo_descompactado = extrair_arquivo_gz(caminho_arquivo, diretorio_destino, nome_teste, mes_abreviado)

                # Deleta o arquivo baixado após extração
            #try:
         #       shutil.rmtree(download_dir)
         #   except Exception as e:
            #    print(f'Falha ao deletar {download_dir}. Razão: {e}')
            try:
                os.remove(caminho_arquivo)
            except:
                print('erro ao remover')

            return caminho_arquivo_descompactado
        except StaleElementReferenceException:
            print(f'Elemento não encontrado para o mês {mes_completo}')
        return None


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

        # Baixar e extrair arquivo da média analisada
            caminho_arquivo_teste = clicar_e_baixar(mes_completo, nome_teste, mes_abreviado, 'Objectively analyzed mean')
            if caminho_arquivo_teste:
                caminhos_arquivos.append(caminho_arquivo_teste)

            # Baixar e extrair arquivo de desvio padrão
            caminho_arquivo_dp = clicar_e_baixar(mes_completo, f'DP_{nome_teste}', mes_abreviado, 'Standard error of the analysis')
            if caminho_arquivo_dp:
                caminhos_arquivos.append(caminho_arquivo_dp)

                        # Deleta o arquivo baixado após extração
        try:
            shutil.rmtree(download_dir)
        except Exception as e:
            print(f'Falha ao deletar {download_dir}. Razão: {e}')


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
   # print(f'Os dados são de {options[-1]}')


    #time.sleep(6)
    clicar_links_meses(meses, nome_teste)
    print('all done')

    driver.quit()
    return caminhos_arquivos

if __name__ == "__main__":
    meses = ['Oct', 'Jan', 'Nov']
    obter_arquivos("Test_", meses, 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23.pl?parameterOption=t')
    #obter_arquivos("Sali_", meses, 'https://www.ncei.noaa.gov/access/world-ocean-atlas-2023/bin/woa23.pl?parameterOption=s')