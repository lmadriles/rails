# %% 
import pandas as pd
import geopandas as gpd

# %% uma função pra remover estações e atualizar a tabela.
def objeto_de_mundanca(lst):
    """Cria um hashmap com chave igual ao índice que vai receber a soma,
    valores iguais aos índices com valores que serão somados."""
    if not lst:
        return {}

    lst = sorted(lst)
    current_sequence = [lst[0]]
    dct = {}

    for i in range(1, len(lst)):
        if lst[i] == lst[i - 1] + 1:
            current_sequence.append(lst[i])
        else:
            dct[lst[i - 1] + 1] = current_sequence
            current_sequence = [lst[i]]
            
    dct[lst[-1] + 1] = current_sequence

    return dct

def sewing(slice_stations, indices_remover):
    """Remove estações pelo índice inserido e
    reajusta os demais registros para desconsiderar as estações removidas."""
    # quais indices da lista estão neste slice:
    indices = list(set(indices_remover) & set(slice_stations.index))
    dct_indices = objeto_de_mundanca(indices)

    # editar extensão (adicionar extensão das estações removidas ao registro seguinte):
    for key, value in dct_indices.items():
        if key in slice_stations.index: # adicionei esse filtro mas não sei se vai remover corretamente as estações
            slice_stations.at[key, 'NumeroExtensao'] += slice_stations.loc[value, 'NumeroExtensao'].sum()

    # remover as estações e reajusta as sequencias:
    slice_stations = slice_stations.drop(index=indices).reset_index(drop=True)
    slice_stations['NumeroSequencia'] = slice_stations.index + 1

    return slice_stations

# remover estações
def remove_stations(stations, indices_remover):

    # Tira da lista índices que não estão no DataFrame:
    indices_remover = set(indices_remover) & set(stations.index)
    linhas_afetadas = stations.loc[stations.index.isin(indices_remover), 'NomeLinha'].unique()
    nao_alterar = stations[~stations['NomeLinha'].isin(linhas_afetadas)].copy()

    # Processa cada conjunto de estações afetadas
    ajustes = []
    for linha in linhas_afetadas:
        slice_stations = stations[stations['NomeLinha'] == linha].sort_values(by='NumeroSequencia')
        ajustes.append(sewing(slice_stations, indices_remover))

    # Concatena tudo e retorna o DataFrame ajustado
    return pd.concat([nao_alterar] + ajustes, ignore_index=True)


def nodes_to_edges(df):

    # Verificar monotonicidade em cada grupo
    for name, group in df.groupby('NomeLinha'):
        if not group['NumeroSequencia'].is_monotonic_increasing:
            print(f'Sequencia not increasing in Linha {name}')
            return None
    
    edges = df.copy()
    edges['estacao_anterior'] = edges['CodigoTresLetrasEstacao'].shift()
    edges['geometry_anterior'] = edges['geometry'].shift() # essa tem que ser a point_geometry
    edges = edges[edges['NumeroSequencia'] != 1].reset_index(drop=True)
    edges['NumeroSequencia'] -= 1

    return edges
