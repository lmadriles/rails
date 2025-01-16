# %%
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import matplotlib.pyplot as plt
from shapely.wkt import loads

# %%

def enline_geometry(path, stations): # essa função é muito lenta.
    """Transforma uma lista de pontos em uma linha"""

    path_linestring = []
    for i in path:
        if not stations[stations['estacao']==i]['points_geometry'].iloc[0]==None:
            path_linestring.append(stations[stations['estacao']==i]['points_geometry'].iloc[0])
            coordinates = [loads(point).coords[0] for point in path_linestring]
        else:
            print(i)

    return LineString(coordinates)


def string_to_geometry(string):

    path = string.split(' ')
    return enline_geometry(path)

# %%

def view_path(map, printable_df, linestring=None, slice_stations=None):
    """Visualiza a rota"""

    ax = map.plot(color='#F1EFEA', edgecolor='#CEC4CC', linewidth=0.5, alpha=0.7) # map
    printable_df.plot(ax=ax,  linewidth=6, label=printable_df['OD'], cmap='plasma') # fluxo
    # Trecho específico:
    line_x, line_y = linestring.xy
    ax.plot(line_x, line_y, color='#2722D0', linewidth=2.5, label='LineString')

    # estaçoes:
    slice_stations.plot(ax=ax, color='black', markersize= 10, label='estacao')
    for x, y, label in zip(slice_stations.geometry.x, slice_stations.geometry.y, slice_stations['estacao']):
        ax.annotate(label, xy=(x, y), xytext=(0, 5), textcoords="offset points")

    ax.set_axis_off() # Hide the axes
    fig = plt.gcf()
    fig.set_size_inches(30, 18)  # 20 inches wide, 12 inches tall

    plt.show()
    #plt.savefig(r"data\final\\"  + nome +".png")
	#plt.close()


    return


# %%
