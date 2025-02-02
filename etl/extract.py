#%% 
import pandas as pd
import geopandas as gpd

#%%

# this will be the function that load all the different dataframes, and return a dictionary with all the dataframes
def extract_data(file_paths):
    """Carrega os dataframes, filtra as colunas e as renomeia."""

    # Load and process lines DataFrame
    lines = (gpd.read_file(file_paths['lines'])
                 .loc[:, ['CodigoLinh','CodigoLi_1','CodigoEsta', 'NumeroSequ', 'CodigoFerr','NumeroExte', 'geometry']]
                 .rename(columns={
                                    'CodigoLinh': 'id',
                                    'NumeroExte': 'extensao',
                                    'CodigoLi_1': 'linha',
                                    'CodigoEsta': 'CodigoEstacao',
                                    'NumeroSequ': 'sequencia',
                                    'CodigoFerr': 'ferrovia'}) )
    


    points = (gpd.read_file(file_paths['points'])
                .loc[:, ['CodigoEsta', 'CodigoTres','NomeEstaca', 'CodigoMuni','IndicadorT', 'IndicadorF', 'geometry']]
                .rename(columns={
                                'NomeEstaca': 'NomeEstacao',
                                'IndicadorT': 'terminal',
                                'IndicadorF': 'intercambio',
                                'geometry': 'points_geometry'
                }))
    
    municipio = (gpd.read_file(file_paths['municipio'])
            .loc[:, ['CodigoMuni', 'CodigoUF', 'NomeMunici']])
    
    map_station = pd.read_excel(file_paths['map_station'])
    map_rail = pd.read_excel(file_paths['map_rail'])
    map_line = pd.read_excel(file_paths['map_line'])
    map_flux = (pd.read_excel(file_paths['map_flux'])
                .loc[:, ['CodigoFluxoTransporte','CodigoFerrovia','CodigoFluxoTransporteFerrovia']]
                )

    fluxos = (pd.read_csv(file_paths['fluxos'], sep='|', encoding='windows-1252', dtype={'NumeroCNPJ': str})
            .assign(DataReferencia=lambda df: pd.to_datetime(df['DataReferencia'], format='%m/%d/%Y %H:%M:%S').dt.strftime('%Y-%m'),
                    id=lambda df: df['CodigoFluxoTransporteFerrovia'] + df['SiglaFerrovia'])
            .rename(columns={
                'DataReferencia': 'data',
                'SiglaFerrovia': 'ferrovia',
                'NomeMercadoria': 'mercadoria',
                'RazaoSocialClientePessoaJuridica': 'cliente',
                'CodigoTresLetrasEstacaoDe': 'origem',
                'CodigoTresLetrasEstacaoPara': 'destino',
                'ValorTU': 'TU',
                'DistanciaItinerario': 'dist_media',
                'CodigoFluxoTransporteFerrovia': 'cod_flux',
                'NumeroCNPJ': 'cnpj'
            })
            #.reindex(columns=['id','data', 'ferrovia', 'mercadoria', 'cliente', 'origem', 'destino', 'TU', 'dist_media', 'cod_flux', 'cnpj'])
            .pipe(lambda df: df[~df['data'].isnull()])
            .pipe(lambda df: df[df['dist_media'] > 0.000].reset_index(drop=True))
            )

    intermed_mid4 = (
        pd.read_excel(file_paths['intermed_mid4']) # path
        .sort_values(by=['CodigoFluxoTransporte', 'NumeroSequencia']) # ordenar
        .assign(DistanciaItinerario=lambda df: df['DistanciaItinerario'].str.replace(',', '.').astype(float)) # converter distancia pra float
        .loc[lambda df: df['DistanciaItinerario'] != 0.0] # remover distancias = 0
        .rename(columns={
                        'CodigoFerroviaTransito': 'malha',
                        'NumeroSequencia': 'seq',
                        'CodigoEstacaoOrigem': 'origem',
                        'CodigoEstacaoIntermediaria1': 'mid_a',
                        'CodigoEstacaoIntermediaria2': 'mid_b',
                        'CodigoEstacaoIntermediaria3': 'mid_c',
                        'CodigoEstacaoIntermediaria4': 'mid_d',
                        'CodigoEstacaoDestino': 'destino',
                        'DistanciaItinerario': 'Dist_SAFF'
        })
        .reset_index(drop=True)

    )

   
    intermed_cafen = (pd.read_csv(file_paths['intermed_cafen'], encoding='ISO-8859-1', sep='\t')
        .sort_values(by=['Código', 'Nº', 'Seq.'])
        .reset_index(drop=True)
        .assign(id=lambda df: df['Código'] + df['Ferrovia'])
        [['id', 'Origem Sigla', 'Destino Sigla', 'Distância (km)']]
        .assign(len_Dijkstra=0)
    )


    return {'lines': lines,
            'map_station': map_station,
            'map_rail': map_rail,
            'map_line': map_line, 
            'points': points, 
            'fluxos': fluxos,
            'intermed_mid4': intermed_mid4,
            'map_flux': map_flux,
            'municipio': municipio,
            'intermed_cafen': intermed_cafen
            }

if __name__ == '__main__':
    data_dict = extract_data(file_paths = {
        'lines': r'../data/raw/shapefiles/Linha2024.shp',
        'map_station': r'../data/raw/tblEstacao.xlsx',
        'map_rail': r'../data/raw/mapa_ferrovia.xlsx',
        'map_line': r'../data/raw/tblLinha.xlsx',
        'points': r"../data/raw/shapefiles/Estação2024.shp",
        'fluxos': r"../data/raw/ArqSIADEFluxoTransporteRealizado_03_02_2025.csv",
        'intermed_mid4': r'./data/raw/tblFluxoTransporteTrecho.xlsx',
        'map_flux': r'../data/raw/tblFluxoTransporte.xlsx',
        'municipio': r'../data/raw/shapefiles/Municipio2024.shp',
        'intermed_cafen': r'../data/raw/TrechoFerrovia.csv'
    })
