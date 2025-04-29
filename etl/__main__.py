#%% 
from sqlalchemy import create_engine, text
import pandas as pd
import os
#%%
# Extract the data:

def create_mssql_engine(server, database):
    """Constroi o motor de conexão ao banco de dados 
    por meio da autenticação do sistema operacional."""

    connection_string = (
        f"mssql+pyodbc://{server}/{database}?"
        "trusted_connection=yes&"
        "driver=ODBC+Driver+17+for+SQL+Server")

    return create_engine(connection_string)

def execute_queries(engine, path_dict):
    """Recebe o motor e o dicionário que mapeia o nome dos dataframes
    com o path de suas queries no projeto."""
    tables = {}
    with engine.connect() as connection:
        for query_name, path in path_dict.items():
            with open(path, 'r') as file:
                query = text(file.read())
                result = connection.execute(query)
                tables[query_name] = pd.DataFrame(result.fetchall(), columns=result.keys())
    return tables


def extract_data(server_name, db_name, path_dict):
    engine = create_mssql_engine(server_name, db_name)
    return execute_queries(engine, path_dict)


# %%
# Transformações que ocorreram e não estão na query
def transform_data(data_dict):
    """Realiza as transformações que não puderam ser realizadas na query."""
    
    # Tratando valores vazions no campo SiglaFerrovia
    stations = data_dict['stations']

    # Caso particular de Variante do Paraopeba (parte da MRS, parte FCA)
    stations.loc[(stations['SiglaFerrovia'].isna()) & (stations['CodigoTresLetrasEstacao']=='FBO'), 'SiglaFerrovia'] = 'FCA'
    # Diferenciar a linha Variante do Paraopeba de posse da FCA:
    stations.loc[stations[(stations['NomeLinha']=='Variante do Paraopeba') & (stations['SiglaFerrovia']=='FCA')].index,'NomeLinha']  = 'Variante do Paraopeba - FCA'

    # pesquisa em outras estações da mesma linha se tem a informação da ferrovia:
    stations['SiglaFerrovia'] = stations.groupby('NomeLinha')['SiglaFerrovia'].transform(lambda x: x.fillna(x.mode()[0] if not x.mode().empty else x))

    # se a linha é toda vazia no campo ferrovia. Spoiler: todas são da FCA
    linhas_fca = [
        'Centro-Sul', 'Porto de Pirapora',
        'Ramal Casa Branca - Casa Branca Velha',
        'Ramal Complexo Mineral de Araxá', 'Ramal CSN',
        'Ramal da Fábrica de Cimento Nassau',
        'Ramal da Fábrica Fertilizantes Nitroferti',
        'Ramal de Pará de Minas',
        'Ramal do Complexo Petroquímico Camaçari',
        'Ramal do Porto de Aratu', 'Ramal Industrial de Mogi-Guaçu',
        'Ramal Industrial de Uberlândia', 'Ramal Industrial Fosfértil',
        'Ramal Industrial Ituverava', 'Ramal Industrial Replan Jaguariúna',
        'Ramal Industrial São João da Barra',
        'Ramal Pool Petróleo - Ribeirão Preto']
    stations.loc[stations['SiglaFerrovia'].isna() & stations['NomeLinha'].isin(linhas_fca), 'SiglaFerrovia'] = 'FCA'

    # alterar distancias
    distance_updates = {
        'ZXX': 8.053,
        'ZZB': 2.202,
        'ATQ': 2.000
    }

    #for estacao, extensao in distance_updates.items():
        #stations.loc[stations['CodigoTresLetrasEstacao'] == estacao, 'NumeroExtensao'] = extensao

    # Ordenar e salvar no dicionário
    data_dict['stations'] = stations.sort_values(by=['SiglaFerrovia', 'NomeLinha', 'NumeroSequencia'])

    return data_dict

def load_data(data_dict, engine_path):
    """Load the transformed data into a SQLite database."""
    engine = create_engine(engine_path, echo=False)

    for key, value in data_dict.items():
        value.to_sql(key, con=engine, index=False, if_exists='replace')

    return

# %%
if __name__ == '__main__':
    # Obtém o diretório onde está o script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Define os caminhos absolutos para os arquivos SQL
    path_dict_ = {
        "stations": os.path.join(BASE_DIR, "stations_query.sql"),
        "fluxos": os.path.join(BASE_DIR, "fluxos_intermed_query.sql"),
        "intermed": os.path.join(BASE_DIR, "intermed_query.sql"),
        "fluxos_ocorrencias": os.path.join(BASE_DIR, "fluxos_ocorrencias_query.sql"),
        "acidentes": os.path.join(BASE_DIR, "acidentes_query.sql"),
        "trem_formado": os.path.join(BASE_DIR, "trem_formado_query.sql"),
    }
    
    data_dict = extract_data(server_name='ANTTLSTPRD01',
                    db_name='BD_SAFF',
                    path_dict=path_dict_)
    
    data_dict_transformed = transform_data(data_dict)
    
    load_data(data_dict_transformed, r'sqlite:///./data/processed/feature_store.db')

# %%
