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

def buscar_localizacao_proxima_em_csv(filename, lat_alvo, lon_alvo):
    with open(filename, 'rb') as f:
        f.seek(0, 2)  # Move o ponteiro para o final do arquivo
        file_size = f.tell()
        
        low = 0
        high = file_size

        melhor_distancia = float('inf')
        melhor_linha = None

        while low <= high:
            mid = (low + high) // 2
            
            f.seek(mid)

            # Ajustar para o início da linha
            if mid != 0:
                f.readline()

            line_start_pos = f.tell()
            line = f.readline().decode('utf-8').strip()
            
            if not line:
                break

            # Usar o csv.reader para analisar a linha
            reader = csv.reader([line])
            row = next(reader)
            
            try:
                lat_meio = float(row[0])
                lon_meio = float(row[1])
            except (IndexError, ValueError):
                break

            distancia = calcular_distancia(lat_alvo, lon_alvo, lat_meio, lon_meio)

            if distancia < melhor_distancia:
                melhor_distancia = distancia
                melhor_linha = line

            # Comparar as coordenadas para ajustar a busca binária
            if (lat_meio, lon_meio) < (lat_alvo, lon_alvo):
                low = line_start_pos + len(line) + 1
            else:
                high = mid - 1

    return melhor_linha

# Exemplo de uso
caminho_arquivo_csv = 'C:\\Users\\comet\\Desktop\\Processamento_CEERMA\\extraido\\Jan.csv'
lat_alvo = -36.44988
lon_alvo = -52.89136

linha_proxima = buscar_localizacao_proxima_em_csv(caminho_arquivo_csv, lat_alvo, lon_alvo)
if linha_proxima:
    print(f'A linha mais próxima é: {linha_proxima}')
else:
    print('Nenhuma localização próxima encontrada.')
