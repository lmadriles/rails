#%% 
import pandas as pd

#%%

# Funções auxiliares: trocar a ordem dessas funções
def decode_df(df, column_to_decode, code_serie, decode_serie):
    """Reverte o encoding dos dataframes de acordo com o mapa fornecido."""

    map_dict = {key: value for key, value in zip(code_serie, decode_serie)}  
    df[column_to_decode] = df[column_to_decode].replace(map_dict)
    return df

def concat_siglas(group):
    """Junta estações (inicial, intermediárias e final) de um mesmo fluxo em uma lista."""
    lista = [group['Origem Sigla'].iloc[0]] + group['Destino Sigla'].tolist()
    return " ".join(lista)

def concat_siglas_intermed(group):
    lista =  [group['origem'].iloc[0]] + group['destino'].tolist()
    return " ".join(lista)

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

# Funções principais
def transform_stations(data_dict):
    """Transforma dados de stations para formato adequado para uso do algoritmo."""
    lines = data_dict['lines']
    points = data_dict['points']
    municipio = data_dict['municipio']
    map_rail = data_dict['map_rail']
    map_line = data_dict['map_line']

    # ordenar estações por linha e sequencia:
    lines = lines.sort_values(by=['linha', 'sequencia']).reset_index(drop=True) 

    # merging:
    points = (points.merge(municipio, on='CodigoMuni', how='left').drop(columns=['CodigoMuni']))
    stations = (lines.merge(points, left_on='CodigoEstacao', right_on='CodigoEsta', how='outer').drop(columns=['CodigoEstacao','CodigoEsta']))


    # decodes
    stations['ferrovia'] = stations['ferrovia'].map(map_rail.set_index('CodigoFerrovia')['SiglaFerrovia'])
    stations['linha'] = stations['linha'].map(map_line.set_index('CodigoLinha')['NomeLinha'])

    # hardfixes: preenchendo NaNs em ferrovia. 
    stations.loc[(stations['ferrovia'].isna()) & (stations['CodigoTres']=='FBO'), 'ferrovia'] = 'FCA'
    stations.loc[stations[stations['linha']=='Ramal Complexo Mineral de Araxá'].index,'ferrovia']  = 'FCA' # todas as estações da linha estão sem essa info
    #stations['ferrovia'] = stations.groupby('linha')['ferrovia'].transform(lambda x: x.fillna(method='ffill'))
    stations['ferrovia'] = stations.groupby('linha')['ferrovia'].transform(lambda x: x.fillna(x.mode()[0] if not x.mode().empty else x))
        # agrupa por linha, pegando o valor de ferrovia, transforma, preenchendo ons nans com o valor anterior mais proximo
    # diferenciar variante do paraopeba
    stations.loc[stations[(stations['linha']=='Variante do Paraopeba') & (stations['ferrovia']=='FCA')].index,'linha']  = 'Variante do Paraopeba - FCA'


    #################################### ALTERAR AS DISTÂNCIAS ENTRE ESTAÇÕES ####################################
    distance_updates = {
        'ZXX': 8.053,
        'ZZB': 2.202,
        'ATQ': 2.000
    }

    for estacao, extensao in distance_updates.items():
        stations.loc[stations['CodigoTres'] == estacao, 'extensao'] = extensao


    # adicionar estação (atualização da rede):
    to_add = {'id': ['9999'],
          'ferrovia': ['EFVM'],
          'linha': ['Costa Lacerda - Capitão Eduardo'],
          'CodigoTres': ['VTB'],
          'NomeEstacao': ['Barão de Cocais'],
          'sequencia': [7],
          'extensao': [3.693],
          'terminal': [1],
          'intercambio': [0]}
    
    stations = add_station(stations, to_add)

    to_add2 = {'id': ['9998'],
          'ferrovia': ['FTL'],
          'linha': ['Tronco São Luis'],
          'CodigoTres': ['ACN'],
          'NomeEstacao': ['Catanhede Novo'],
          'sequencia': [11],
          'extensao': [28.644],
          'terminal': [1],
          'intercambio': [0]}
    
    stations = add_station(stations, to_add2)

    # remover linhas sem estações:
    remover_linhas = ['Miguel Burnier - General Carneiro (Linha do Centro)']
    stations = stations[~stations['linha'].isin(remover_linhas)]
    stations = stations[['id','ferrovia', 'linha', 'CodigoTres','NomeEstacao', 'sequencia','extensao', 'terminal',
                         'intercambio', 'points_geometry', 'geometry']].rename(columns={'CodigoTres': 'estacao','NomeMunici': 'municipio'})
    data_dict['stations'] = stations

    return stations


def transform_fluxos(data_dict):

    fluxos = data_dict['fluxos']
    fluxos['data'] = pd.to_datetime(fluxos['data'])
    fluxos['data'] = pd.to_datetime(fluxos['data'].dt.strftime('%Y-%m'))

    # sort fluxos by date 
    fluxos = fluxos.sort_values(by='data').reset_index(drop=True)

    fluxos_columns = ["id","ferrovia","cliente","mercadoria","origem","destino","dist_media",
    "NomeClientePessoaFisica","NumeroCPF","NomeFantasiaClientePessoaJuridica","cnpj","DescricaoTipoEmpresa",
    "IndicadorProdutoPerigoso","NomeGrupoMercadoria","NomeSubGrupoMercadoria","SiglaUnidadeTarifaria","cod_flux",
    "NomeEstacaoDe","NomeMunicipioEstacaoDe","SiglaUFEstacaoDe","WKTEstacaoDe","NomeEstacaoPara",
    "NomeMunicipioEstacaoPara","SiglaUFEstacaoPara","WKTEstPara"]

    # colunas descritivas da ocorrencia
    ocorrencia_columns = ["data","id","TU","ValorTKU","ValorReceitaLiquida","ValorTarifa","ValorManobra",
    "ValorCargaDescarga","ValorTransbordo","ValorOutros","ValorPontaRodoviaria","ValorFreteRodoviario",
    "NumeroDistanciaFreteRodoviario","NumeroVagaoKmVazio","NumeroCarregamentos","NumeroTempoMedio","QtdeConteiner",
    "QtdeMetroCubico"]

    # divide fluxos em fluxos e ocorrencias
    ocorrencias = fluxos.filter(items=ocorrencia_columns).reset_index(drop=True).copy()
    fluxos = fluxos.filter(items=fluxos_columns).copy()

    # drop every line duplicated, keep the last

    fluxos = fluxos.drop_duplicates().reset_index(drop=True)

    return ocorrencias, fluxos

def transform_intermed(data_dict):
    intermed_cafen = data_dict['intermed_cafen']
    intermed_mid4 = data_dict['intermed_mid4']
    map_flux = data_dict['map_flux']
    map_station = data_dict['map_station']
    map_rail = data_dict['map_rail']
    fluxos = data_dict['fluxos']

    # changes
    # Função para concatenar as siglas
    # Sumarizar as informações de intermed_cafen
    cafen_summary = intermed_cafen.groupby('id', group_keys=False).apply(concat_siglas).reset_index() 
    cafen_summary = cafen_summary.rename(columns={0: 'intermed'})  # Renomear a coluna

    # decodes de intermed_mid4
    intermed_mid4 = pd.merge(intermed_mid4, map_flux, on='CodigoFluxoTransporte', how='left')

    intermed_mid4 = decode_df(intermed_mid4,
                            ['origem', 'destino', 'mid_a','mid_b', 'mid_c','mid_d'],
                            map_station['CodigoEstacao'],
                            map_station['CodigoTresLetrasEstacao'])

    intermed_mid4 = decode_df(intermed_mid4,
                            ['malha', 'CodigoFerrovia'],
                            map_rail['CodigoFerrovia'],
                            map_rail['SiglaFerrovia'])

    
    # alterando colunas:
    intermed_mid4['id'] = intermed_mid4['CodigoFluxoTransporteFerrovia'] + intermed_mid4['CodigoFerrovia']

    # slicing
    intermed_mid4 = intermed_mid4[['id','CodigoFluxoTransporteFerrovia', 'CodigoFerrovia','malha',
                                     'seq','origem', 'mid_a','mid_b', 'mid_c','mid_d', 'destino', 'Dist_SAFF']]
    intermed_mid4 = intermed_mid4[~intermed_mid4['id'].isin(intermed_cafen['id'])].reset_index(drop=True)
    intermed_mid4 = intermed_mid4[intermed_mid4['id'].isin(fluxos['id'])].reset_index(drop=True)


    # sumarizar as informações de intermed_mid4 (precisa não ter estações mid)
    if intermed_mid4['mid_a'].isna().all() & intermed_mid4['mid_b'].isna().all() & intermed_mid4['mid_c'].isna().all() & intermed_mid4['mid_d'].isna().all():
        mid4_summary = intermed_mid4.groupby('id', group_keys=False).apply(concat_siglas_intermed).reset_index() 
        mid4_summary = mid4_summary.rename(columns={0: 'intermed'})

        intermed_summary = pd.concat([cafen_summary, mid4_summary], ignore_index=True)

    return intermed_summary


def transform_data(data_dict):

    stations = transform_stations(data_dict)
    ocorrencias, fluxos = transform_fluxos(data_dict)
    intermed = transform_intermed(data_dict)




    return {'stations': stations,
            'ocorrencias': ocorrencias,
            'fluxos': fluxos,
            'intermed': intermed
            }


#%%
from .extract import extract_data

if __name__=='__main__':
    data_dict = extract_data(file_paths = {
        'lines': r'../data/raw/shapefiles/Linha2024.shp',  #  EditorSQL-20231002-151029.xlsx
        'map_station': r'../data/raw/tblEstacao.xlsx', # mapa query_mapa_estacao.xlsx
        'map_rail': r'../data/raw/mapa_ferrovia.xlsx', # tblFerrovia.xlsx
        'map_line': r'../data/raw/tblLinha.xlsx', # tblLinha.xlsx
        'points': r"../data/raw/shapefiles/Estação2024.shp", # tblDREstacao.shp
        'fluxos': r"../data/raw/ArqSIADEFluxoTransporteRealizado_07_01_25.csv", # ArqSIADEFluxoTransporteRealizado.csv
        'intermed_mid4': r'../data/raw/tblFluxoTransporteTrecho.xlsx', # tblFluxoTransporteTrecho.xlsx
        'map_flux': r'../data/raw/tblFluxoTransporte.xlsx', # tblFluxoTransporte.xlsx
        'municipio': r'../data/raw/shapefiles/Municipio2024.shp',
        'intermed_cafen': r'../data/raw/TrechoFerrovia.csv' # dados extraídos do saff (essa info não está mais lá, não deletar esse arquivo)
        })
    data_transformed = transform_data(data_dict)
