import netCDF4 as nc

netcdf = 'C:\\Users\\comet\\Desktop\\Processamento_CEERMA\\NetCDF\\OS_OCEANO-TESTS_CTD.nc'

# Abrir o arquivo NetCDF em modo de leitura
with nc.Dataset(netcdf, 'r') as arquivo:
    # Listar as variáveis disponíveis no arquivo
    print("Variáveis no arquivo:")
    print(arquivo.variables)

    # Acessar uma variável específica
    variavel = arquivo.variables['nome_da_variavel']

    # Ler os dados da variável
    dados = variavel[:]

    # Obter informações sobre a variável
    print("Informações sobre a variável:")
    print(variavel)
