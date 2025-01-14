# %%
import pandas as pd
import geopandas as gpd
import sqlalchemy
from utils import graph_utils
from utils import station_manager

# %%
def extracts(path):
    stations = gpd.read_file(path)
    stations = stations.sort_values(by=['linha', 'sequencia']).reset_index(drop=True)

    return stations


def select_criteria(stations):
    """Retorna lista das estações a serem deletadas."""
    remover = stations[stations['points_geometry'].isna()]['estacao'].unique().tolist()
    importantes = station_manager.prioritize_station(stations)
    #print([x for x in remover if x in importantes])
    remover = [x for x in remover if x not in importantes]
    remover.remove('V77')
      
    return remover


def connect_to_db(path):
    return sqlalchemy.create_engine(path)


def import_query(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# %%

def create_route(G, fluxos_df):
     
    for index, row in fluxos_df.iterrows():
        try:
            intermeds = row['intermed'].split()
            dist, rota = graph_utils.must_pass(G, intermeds)
            fluxos_df.at[index, 'len_Dijkstra'] = dist
            fluxos_df.at[index, 'rota'] = " ".join(rota)

        except Exception as e:
            if pd.isna(row['intermed']):
                dist, rota = graph_utils.must_pass(G, [row['origem'], row['destino']])
                #diferenca = round(abs(dist - row['dist_media']),3)
                fluxos_df.at[index, 'len_Dijkstra'] = dist
                fluxos_df.at[index, 'rota'] = " ".join(rota)
                #fluxos_df.at[index, 'diferenca'] = diferenca
                continue
                

            print(f"Erro {e} em {row['id']}")
            continue

    return fluxos_df


def Routes():
    stations = extracts('./data/processed/stations.gpkg')
    remover = select_criteria(stations)
    stations = station_manager.remove_stations(stations, remover)
    G = graph_utils.generate_graph(stations)

    origin_engine = connect_to_db('sqlite:///./data/processed/database.db')
    
    query = import_query('./routes/query_to_routes.sql')
    query_fmt = query.format(date='2017-01-01')
    fluxos_routes = pd.read_sql(query_fmt, origin_engine)
    
    fluxos_routes = create_route(G, fluxos_routes)
    # salve o fluxos_df no feature_store.db
    fluxos_routes.to_sql('fluxos_rotas_2017', origin_engine, if_exists='replace', index=False)
