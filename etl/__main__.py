from .extract import extract_data
from .transform import transform_data
from .load import load_data

def run_etl():
    data_raw = extract_data(file_paths = {
        'lines': r'./data/raw/shapefiles/Linha2024.shp',  #  EditorSQL-20231002-151029.xlsx
        'map_station': r'./data/raw/tblEstacao.xlsx', # mapa query_mapa_estacao.xlsx
        'map_rail': r'./data/raw/mapa_ferrovia.xlsx', # tblFerrovia.xlsx
        'map_line': r'./data/raw/tblLinha.xlsx', # tblLinha.xlsx
        'points': r"./data/raw/shapefiles/Estação2024.shp", # tblDREstacao.shp
        'fluxos': r"./data/raw/ArqSIADEFluxoTransporteRealizado_07_01_25.csv", # ArqSIADEFluxoTransporteRealizado.csv
        'intermed_mid4': r'./data/raw/tblFluxoTransporteTrecho.xlsx', # tblFluxoTransporteTrecho.xlsx
        'map_flux': r'./data/raw/tblFluxoTransporte.xlsx', # tblFluxoTransporte.xlsx
        'municipio': r'./data/raw/shapefiles/Municipio2024.shp',
        'intermed_cafen': r'./data/raw/TrechoFerrovia.csv' # dados extraídos do saff (essa info não está mais lá, não deletar esse arquivo)
    })
    data = transform_data(data_raw)
    load_data(data,
              engine_path='sqlite:///./data/processed/database.db',
              shapefile_path='./data/processed/')

if __name__ == "__main__":
    run_etl()
