import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt

arquivo_netcdf = 'C:\\Users\\comet\\Desktop\\Processamento_CEERMA\\NetCDF\\OS_OCEANO-TESTS_CTD.nc'


# Função para listar variáveis no arquivo NetCDF
def listar_variaveis(nc_file):
    dataset = nc.Dataset(nc_file)
    print("Variáveis no arquivo:")
    for var in dataset.variables:
        print(var)
    dataset.close()

# Função para plotar gráfico de profundidade vs oxigênio
def plot(nc_file):
    dataset = nc.Dataset(nc_file)
    
    # Substitua 'profundidade' e 'oxigenio' pelos nomes reais das variáveis no seu arquivo
    profundidade = dataset.variables['DEPTH'][:]
    temperatura = dataset.variables['TEMP'][:]
    
    plt.figure(figsize=(10, 6))
    plt.plot(temperatura, profundidade, marker='o')
    plt.gca().invert_yaxis()  # Inverte o eixo Y para que profundidade aumente para baixo
    plt.xlabel('Temperatura')
    plt.ylabel('Profundidade')
    plt.title('Perfil de Profundidade vs Temperatura')
    plt.grid()
    plt.show()
    
    dataset.close()

def plot_de_perfil(nc_file, perfil=None):
    dataset = nc.Dataset(nc_file)
    
    profundidade = dataset.variables['DEPTH'][:]
    temperatura = dataset.variables['TEMP'][:]
    
    num_perfis = profundidade.shape[0]
    
    if perfil is not None:
        # Se um perfil específico é fornecido, verificar se é válido
        if perfil >= num_perfis:
            print(f"Perfil {perfil} não é válido. Existem apenas {num_perfis} perfis.")
            return
        perfis_a_plotar = [perfil]
    else:
        # Se nenhum perfil específico é fornecido, plotar todos os perfis
        perfis_a_plotar = range(num_perfis)
    
    for p in perfis_a_plotar:
        plt.figure(figsize=(10, 6))
        plt.plot(temperatura[p, :], profundidade[p, :], marker='o')
        plt.gca().invert_yaxis()  # Inverte o eixo Y para que profundidade aumente para baixo
        plt.xlabel('Temperatura (°C)')
        plt.ylabel('Profundidade (m)')
        plt.title(f'Perfil de Profundidade vs Temperatura - Estação {(p + 1)}')
        plt.grid()
        plt.savefig(f'Plot_DEPTHvsTEMP_Estacao_{(p + 1)}.png')  # Salva a figura com o nome e extensão especificados
        plt.show()
    
    dataset.close()


# Abrir o arquivo NetCDF em modo de leitura
with nc.Dataset(arquivo_netcdf, 'r') as arquivo:
    # Listar as variáveis disponíveis no arquivo
    print("Variáveis no arquivo:")
    #print(arquivo.variables)

    # Acessar uma variável específica
    #variavel = arquivo.variables['PROFILE']

    # Ler os dados da variável
    #dados = variavel[:]

    # Obter informações sobre a variável
    #print("Informações sobre a variável: profile")
    #print(variavel)

    # Acessar VARIÁVEIS
    profile = arquivo.variables['PROFILE']
    time = arquivo.variables['TIME']
    latitude = arquivo.variables['LATITUDE']
    longitude = arquivo.variables['LONGITUDE']
    profundidade = arquivo.variables['DEPTH']
    salinidade = arquivo.variables['PSAL']
    temperatura = arquivo.variables['TEMP']
    pressai = arquivo.variables['PRES']



    # Exibir informações sobre a variável PROFILE
    print("\nInformações sobre a variável TEMP:")
    print(temperatura)

        # Se você precisar acessar os dados da variável PROFILE
    dados_profile = profile[:]
    dados_profundidade = profundidade[:]
    dados_temperatura = temperatura[:]
    print("\nDados da variável TEMP:")
    print(dados_temperatura)


    # Fechar o arquivo
   # arquivo.close()


# Listar variáveis no arquivo NetCDF
#listar_variaveis(arquivo_netcdf)

# Plotar gráfico de profundidade vs oxigênio
#plot(arquivo_netcdf)

plot_de_perfil(arquivo_netcdf)