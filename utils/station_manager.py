# %% 
import pandas as pd
import geopandas as gpd

# %% uma função pra remover estações e atualizar a tabela.
class StationRemovalError(Exception):
    """Estação importante, não remova ela."""
    pass

def prioritize_station(stations):
    # lista de estações importantes
    pontas = stations.groupby('linha')['estacao'].agg(['first', 'last']).values.flatten().tolist() # ponta de linha
    importantes = stations[(stations['terminal'] == 1) | (stations['intercambio'] == 1)]['estacao'].unique().tolist() # terminal ou intercâmbio
    importantes = list(set(importantes) | set(pontas))
    #importantes.remove('DPE') #  DPE é uma estação de início de linha que não existe mais. Pensar no que faze com a extensão até ela.

    return importantes

def objeto_de_mundanca(lst):
    """Cria um hashmap com chave igual ao índice que vai receber a soma,
    valores iguais aos índices que serão somados."""
    if not lst:
        return []

    lst.sort()
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

def sewing(slice_stations, lista_remover):
    indices = slice_stations[slice_stations['estacao'].isin(lista_remover)].index.tolist()
    dct_indices = objeto_de_mundanca(indices)

    # editar extensao
    for key, value in dct_indices.items():
        slice_stations.loc[key, 'extensao'] += slice_stations.loc[value, 'extensao'].sum()

    # remover linhas
    slice_stations = slice_stations.drop(index=indices).reset_index(drop=True)

    # atualizar sequencia
    slice_stations['sequencia'] = slice_stations.index + 1

    return slice_stations

def remove_stations(stations, lista_remover):

    #print(linhas_sem_remocao)
    linhas_com_remocao = stations[stations['estacao'].isin(lista_remover)]['linha'].unique().tolist()
    # todos os valores de linha em stations que não estão em linhas_com_remocao:
    linhas_sem_remocao = list(set(stations['linha'].unique().tolist()) - set(linhas_com_remocao))

    new_df = stations[stations['linha'].isin(linhas_sem_remocao)].copy()
    
        
    for linha in linhas_com_remocao:
        slice_stations = stations[stations['linha'] == linha].sort_values(by=['linha','sequencia']).reset_index()

        linha_slice = sewing(slice_stations, lista_remover)
        new_df = pd.concat([new_df, linha_slice], ignore_index=True)

    return new_df

def add_station(stations, to_add):

    to_add = pd.DataFrame(to_add)

    stations.loc[
        (stations['linha'] == to_add['linha'][0]) & (stations['sequencia'] >= to_add['sequencia'][0]),
        'sequencia'
    ] += 1

    stations.loc[
        (stations['linha'] == to_add['linha'][0]) & (stations['sequencia'] == to_add['sequencia'][0] + 1),
        'extensao'
    ] -= to_add['extensao'][0]

    stations = pd.concat([stations, to_add], ignore_index=True)
    stations = stations.sort_values(by=['linha', 'sequencia']).reset_index(drop=True)

    return stations