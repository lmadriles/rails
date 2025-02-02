import networkx as nx
import pandas as pd
import geopandas as gpd
from itertools import pairwise


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

# %%
# Origem e destino para caminho:
def must_pass(G, points, return_route=True):
    """Rota precisa passar por mais de um ponto específico.
    
    Args:
        G (networkx.Graph): O grafo representando o mapa.
        points (list): Lista de pontos que a rota deve passar.
        return_route (bool): Se True, retorna a rota completa junto com a distância total.
                            Se False, retorna apenas a distância total.
    
    Returns:
        Se return_route for True, retorna uma tupla (total_dist, total_route).
        Se return_route for False, retorna apenas total_dist.
    """
    total_dist = 0
    total_route = []

    for i in range(len(points)-1):
        if return_route:
            dist_mid, route_mid = nx.single_source_dijkstra(G, source=points[i], target=points[i+1], weight='weight')
            total_route.extend(route_mid[:-1])
        else:
            dist_mid = nx.dijkstra_path_length(G, source=points[i], target=points[i+1], weight='weight')
        total_dist += dist_mid

    if return_route:
        total_route.append(route_mid[-1])  # adiciona ultimo ponto na rota
        return total_dist, total_route
    else:
        return total_dist


# %%
# Projeções:
def get_entrepatios(train, rail, sentido=False):
    main_list = train.split()
    main_list_ep = list(pairwise(main_list))
    rail_ep = list(pairwise(rail))

    if sentido:
        #print("Flag ativada: o sentido de rail vai ser levado em consideração.")
        return [item for item in main_list_ep if item in rail_ep] # interseçao

    else: # sentido is False
        crescente = list(pairwise(rail))
        decrescente = list(pairwise(rail[::-1]))

        intersec_crescente = [item for item in main_list_ep if item in crescente]
        intersec_decrescente = [item for item in main_list_ep if item in decrescente]

        return intersec_crescente + intersec_decrescente # união das duas interseccoes
    
def find_edge(G, entrepatio, operator):
    try:
        if G.edges[entrepatio]['ferrovia']==operator:
            return G.edges[entrepatio]['weight']
        else:
            return 0
    except:
        return 0

def train_on_rail(G, train, rail, tu, operator, valor_retorno='tku', sentido=False):
    """Esta função exige que as estações estejam sequenciadas e sem buracos. 
    Uma forma de garantir é utilizar o must_pass ou não eliminar duplicatas."""
    km = 0
    entrepatios = get_entrepatios(train, rail, sentido)

    for par in entrepatios:
        if find_edge(G, par, operator) is None:
            print('Aresta não encontrada: ' + par + ' de ' + operator)

        km += find_edge(G, par, operator)
    
    if valor_retorno == "dist":
        return km
    elif valor_retorno == "tku":
        return km * tu
    elif valor_retorno == "bool":
        return bool(km)
    elif valor_retorno == "tu":
        return bool(km)*tu
    else:
        raise ValueError("Opção inválida para 'valor_retorno'. Use 'dist', 'tku' ou 'bool' ou 'tu'.")



# %%

def must_pass_dist(G, points):
    """Rota precisa passar por mais de um ponto específico"""
    total_dist = 0

    for i in range(len(points)-1):
        dist_mid, _ = nx.single_source_dijkstra(G, source=points[i], target=points[i+1], weight='weight')
        total_dist += dist_mid

    return total_dist

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


def find_edge_v2(G, a, b, malha):
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
        if find_edge_v2(G,stations[i], stations[i+1], malha) is None:
            print(stations[i], stations[i+1], malha)

        km += find_edge_v2(G,stations[i], stations[i+1], malha)

    tku = km * tu
    return tku


def find_tu(G, main_string, path, tu, malha):
    found = 0
    stations = get_projection(main_string, path)
    for i in range(len(stations)-1):
        if find_edge_v2(G,stations[i], stations[i+1], malha) is None:
            print(stations[i], stations[i+1], malha)

        found = bool(find_edge_v2(G,stations[i], stations[i+1], malha))
        if found:
            break

    return found * tu


def find_dist(G, main_string, path, malha):
    km = 0
    stations = get_projection(main_string, path)
    for i in range(len(stations)-1):
        if find_edge_v2(G,stations[i], stations[i+1], malha) is None:
            print(stations[i], stations[i+1], malha)

        km += find_edge_v2(G,stations[i], stations[i+1], malha)

    return km
