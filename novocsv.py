import csv
from math import radians, sin, cos, sqrt, atan2

# Função para calcular a distância entre duas coordenadas usando a fórmula de Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371.0  # Raio da Terra em km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distancia = R * c
    return distancia

# Função para encontrar a localização mais próxima em um arquivo CSV
def encontrar_localizacao_proxima(lat_alvo, lon_alvo, caminho_arquivo_csv):
    melhor_distancia = float('inf')
    melhor_localizacao = None

    with open(caminho_arquivo_csv, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Pula o cabeçalho
        next(reader)  # Pula o cabeçalho

        for row in reader:
            lat = float(row[0])
            lon = float(row[1])

            # Calcula a distância
            distancia = calcular_distancia(lat_alvo, lon_alvo, lat, lon)

            # Atualiza a melhor localização encontrada até agora
            if distancia < melhor_distancia:
                melhor_distancia = distancia
                melhor_localizacao = (lat, lon)
                melhor_linha = row[2:]

    return melhor_linha


# Exemplo de uso
caminho_arquivo_csv = 'C:\\Users\\comet\\Desktop\\Processamento_CEERMA\\extraido\\Jan.csv'
lat_alvo = -36.44988
lon_alvo = -52.89136

localizacao_proxima = encontrar_localizacao_proxima(lat_alvo, lon_alvo, caminho_arquivo_csv)
if localizacao_proxima:
    print(f'Os valores nessa coordenada são: {localizacao_proxima}')
else:
    print('Nenhuma localização próxima encontrada.')
