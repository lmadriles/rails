import networkx as nx
import pandas as pd
import geopandas as gpd


def nodes_to_edges(df):

    # Verificar monotonicidade em cada grupo
    for name, group in df.groupby('linha'):
        if not group['sequencia'].is_monotonic_increasing:
            print(f'sequencia not increasing in linha {name}')
            return None
    
    edges = df.copy()
    edges['estacao_anterior'] = edges['estacao'].shift()
    edges['geometry_anterior'] = edges['geometry'].shift() # essa tem que ser a point_geometry
    edges = edges[edges['sequencia'] != 1].reset_index(drop=True)
    edges['sequencia'] -= 1


    return edges



def generate_graph(gdf):
    """Generate the NetworkX graph."""


    nodes = gdf.drop_duplicates(subset=['estacao'], keep='first') # remover as duplicatas do query_stations

    # eliminar a necessidade de importar edges:
    edges = nodes_to_edges(gdf)

    G = nx.Graph()
    G.add_nodes_from(nodes['estacao']) # nodes
    node_attributes = nodes[['estacao', 'geometry']].set_index('estacao').to_dict(orient='index')
    nx.set_node_attributes(G, node_attributes) # atributo do nó

    

    # Edges
    for index, row in edges.iterrows():
        source = row['estacao_anterior']
        target = row['estacao']
        metadata = {'weight': row['extensao'],'ferrovia': row['ferrovia'],'linha': row['linha'],'sequencia': row['sequencia']} 

        # Verifica se o nó existe antes de adicioná-lo: 
        if source in G.nodes and target in G.nodes:
            G.add_edge(source, target, **metadata)
        else:
            print(source,target)

    return G

def must_pass_dist(G, points):
    """Rota precisa passar por mais de um ponto específico"""
    total_dist = 0

    for i in range(len(points)-1):
        dist_mid, _ = nx.single_source_dijkstra(G, source=points[i], target=points[i+1], weight='weight')
        total_dist += dist_mid

    return total_dist

def must_pass(G, points):
    """Rota precisa passar por mais de um ponto específico"""
    total_dist = 0
    total_route = []

    for i in range(len(points)-1):
        dist_mid, route_mid = nx.single_source_dijkstra(G, source=points[i], target=points[i+1], weight='weight')
        total_dist += dist_mid
        total_route += route_mid[:-1]

    total_route += [route_mid[-1]] # adiciona ultimo ponto na rota

    return total_dist, total_route

# %% Remover essa célula depois de testar as funções:
# TKU no trecho:
def get_projection_old(main_string, path):
    path_set = set(path)
    return [x for x in main_string.split() if x in path_set]

def find_edge_old(G, a, b, malha):
    try:
        if G.edges[(a,b)]['ferrovia']==malha:
            return G.edges[(a,b)]['weight']
        else:
            return 0
    except:
        return 0

def find_tku_old(G, main_string, path, tu, malha):
    km = 0
    stations = get_projection_old(main_string, path)
    for i in range(len(stations)-1):
        if find_edge_old(G,stations[i], stations[i+1], malha) is None:
            print(stations[i], stations[i+1], malha)

        km += find_edge_old(G,stations[i], stations[i+1], malha)

    tku = km * tu
    return tku

# %%
# modify the get_projection function to not find edge if the two stations are not connected:

def get_projection(main_string, path):
    path_set = set(path)
    main_list = main_string.split()
    result = []
    prev = None

    for i, station in enumerate(main_list):
        if station in path_set:
            if prev is not None and (i == 0 or main_list[i-1] != prev):
                result.append("|")
            result.append(station)
            prev = station

    return result


def find_edge(G, a, b, malha):
    try:
        if G.edges[(a,b)]['ferrovia']==malha:
            return G.edges[(a,b)]['weight']
        else:
            return 0
    except:
        return 0

def find_tku(G, main_string, path, tu, malha):
    km = 0
    stations = get_projection(main_string, path)
    for i in range(len(stations)-1):
        if find_edge(G,stations[i], stations[i+1], malha) is None:
            print(stations[i], stations[i+1], malha)

        km += find_edge(G,stations[i], stations[i+1], malha)

    tku = km * tu
    return tku


def find_tu(G, main_string, path, tu, malha):
    found = 0
    stations = get_projection(main_string, path)
    for i in range(len(stations)-1):
        if find_edge(G,stations[i], stations[i+1], malha) is None:
            print(stations[i], stations[i+1], malha)

        found = bool(find_edge(G,stations[i], stations[i+1], malha))
        if found:
            break

    return found * tu


def find_dist(G, main_string, path, malha):
    km = 0
    stations = get_projection(main_string, path)
    for i in range(len(stations)-1):
        if find_edge(G,stations[i], stations[i+1], malha) is None:
            print(stations[i], stations[i+1], malha)

        km += find_edge(G,stations[i], stations[i+1], malha)

    return km
