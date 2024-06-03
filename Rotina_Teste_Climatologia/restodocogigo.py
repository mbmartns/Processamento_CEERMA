


    
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



# Encontrar e clicar no link "Annual"
link_anual = driver.find_element(By.XPATH, '//a[contains(text(), "Annual")]')
link_anual.click()






# Selecionar o formato CSV
select_format = Select(driver.find_element(By.NAME, 'format'))
select_format.select_by_visible_text('CSV')

# Selecionar a resolução de grade 1/4°
select_grid = Select(driver.find_element(By.NAME, 'grid'))
select_grid.select_by_visible_text('1/4°')

# Submeter o formulário (se necessário)
submit_button = driver.find_element(By.XPATH, '//input[@type="submit"]')
submit_button.click()

# Esperar a página carregar e gerar o link de download
time.sleep(5)

# Encontre o link de download do arquivo CSV
download_link = driver.find_element(By.PARTIAL_LINK_TEXT, 'csv.gz')
file_url = download_link.get_attribute('href')

# Baixar o arquivo
import requests

response = requests.get(file_url)
download_dir = './baixados'
file_name = 'woa23_B5C2_t11mn04.csv.gz'
file_path = f"{download_dir}/{file_name}"

# Certifique-se de que o diretório de destino existe
os.makedirs(download_dir, exist_ok=True)

with open(file_path, 'wb') as file:
    file.write(response.content)

print(f'Arquivo baixado com sucesso: {file_path}')

# Fechar o WebDriver
driver.quit()

