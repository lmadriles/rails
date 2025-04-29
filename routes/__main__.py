# %%
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
from utils import graph_utils, station_manager
import os
#from shapely import wkt

# %%
def load_queries(engine, path_dict):
    """
    Carrega consultas SQL a partir de arquivos e executa no banco de dados.
    Retorna um dicionário com DataFrames e um GeoDataFrame específico.
    
    :param engine: SQLAlchemy engine para conexão com o banco.
    :param path_dict: Dicionário com nomes das queries e seus respectivos caminhos.
    :return: Dicionário com DataFrames, exceto "stations_query" que retorna um GeoDataFrame.
    """
    results = {}
    
    for key, path in path_dict.items():
        with open(path, 'r', encoding='utf-8') as file:
            query = file.read()
        
        results[key] = pd.read_sql(query, engine)
    
    return results

def create_route(G, fluxos_df):
     
    for index, row in fluxos_df.iterrows():
        try:
            intermeds = row['concatenated_siglas'].split()
            dist, rota = graph_utils.must_pass(G, intermeds)
            fluxos_df.at[index, 'len_Dijkstra'] = dist
            fluxos_df.at[index, 'rota'] = " ".join(rota)

        except Exception as e:
            print(f"Erro {e} em {row['id']}")
            continue

    return fluxos_df

# %%
if __name__ == '__main__':
    feature_engine = create_engine('sqlite:///./data/processed/feature_store.db')
        # 'sqlite:///../data/processed/feature_store.db' se executado diretamente

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path_dict = {
        "fluxos_intermed": os.path.join(BASE_DIR, "fluxos_intermed_query.sql"),
        "fluxos_ocorrencias_intermed": os.path.join(BASE_DIR, "fluxos_ocorrencias_intermed_query.sql"),
        "stations": os.path.join(BASE_DIR, "stations_query.sql")
        }

    # Carrega os dataframes
    data_dict = load_queries(feature_engine, path_dict)
    fluxos_intermed = data_dict['fluxos_intermed']
    fluxos_ocorrencias_intermed = data_dict['fluxos_ocorrencias_intermed']
    stations = data_dict['stations']
    
    # Remove as linhas que dão problema nos fluxos mais recentes (devolvida)
    stations = station_manager.remove_stations(stations, stations[stations['NomeLinha']=='Miguel Burnier - General Carneiro (Linha do Centro)'].index)

    # converte pra geodataframe: não necessário nesta etapa
    #stations['geometry'] = stations['points'].apply(wkt.loads)
    #stations_gdf = gpd.GeoDataFrame(stations, geometry='geometry')

    # cria o grafo
    G = graph_utils.generate_graph(stations)

    # cria a coluna rotas:
    fluxos_rotas = create_route(G, fluxos_intermed)

    # salva fluxos_rotas no banco de dados
    fluxos_rotas.to_sql('fluxos_rotas', con=feature_engine, index=False, if_exists='replace')

# %%
