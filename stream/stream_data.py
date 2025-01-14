# %%
import pandas as pd
import sqlalchemy

# %%
def connect_to_db(path):
    return sqlalchemy.create_engine(path)


def import_query(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def yaml_to_intermed(df, dict):  # o nome dessa função é pra ser alterado
    """Converte um dicionário em um DataFrame.
    - Alterar futuramente pra esse dicionários ser importado como metadado 
    (metadado precisa estar fora do código)"""

    for key, value in dict.items():
        df.loc[df['id'] == key, 'intermed'] = value

    return df

def infer_intermed(row, mapping):
    """Preenche os valores ausentes usando mapeamento (pegando valores de fluxos semelhantes)."""
    if pd.isna(row['intermed']):
        key = (row['origem'], row['destino'], row['dist_media'])
        return mapping.get(key, row['intermed'])
    return row['intermed']


def fill_intermed(fluxos_ocorrencias, hard_intermed):
    """Insere nos fluxos estações intermediárias quando não é possível inferir."""

    fluxos_ocorrencias = yaml_to_intermed(fluxos_ocorrencias, hard_intermed) # hardcode

    # segunda etapa: inferência
    mapping = fluxos_ocorrencias.dropna(subset=['intermed']).set_index(['origem', 'destino', 'dist_media'])['intermed'].to_dict() 
    fluxos_ocorrencias['intermed'] = fluxos_ocorrencias.apply(lambda row: infer_intermed(row, mapping), axis=1)
     
    return fluxos_ocorrencias

# %%
def StreamData():

    origin_engine = connect_to_db('sqlite:///./data/processed/database.db') # conecta com os bancos de dados
    #target_engine = connect_to_db('sqlite:///./data/processed/feature_store.db') # conecta com os bancos de dados
    query = import_query('./stream/query_to_stream.sql') # importa a query
    fluxos_ocorrencias = pd.read_sql(query, origin_engine) # realiza a query
    
    #### Insira aqui a importação 


    # %%
    hard_intermed = {'37677MRS': 'HIT FBA FQS FSD FBP FCA',
                'J0430FCA': 'ZBL ZCB ZUB EIA EGS ECL VWI',
                '35865MRS': 'IEF FBP FQC FDM FBO EFR EEL',
                '24629MRS': 'IIP OBR IEF FBP FQC FDM FBO EFR EEL',
                'H8697FCA': 'EPO EAU ZUB ZCB ZBL ZKE ZEV ZPG ICB ISN',
                'K0503FCA': 'EBJ EAU ZUB ZCB ZBL ZKE ZEV ZPG ICB ISN',
                '36928MRS': 'FFL FBP FQC EMP ELF',
                '38942MRS': 'FSE FBP FQC EMP ELF',
                '75799RMN': 'TCS TMI ZTO ZOI ZIQ ZBV ZQB ZKE ZEV ZPG IAA IPG IBA',
                '89108RMP': 'ZFN ZTO ZOI ZIQ ZBV ZQB ZKE ZEV ZPG ICB',
                '77225RMC': 'PPN POS ZRL ZTO ZOI ZIQ ZBV ZQB ZKE ZEV ZPG ICB ISN',
                '77232RMC': 'PPN POS ZRL ZTO ZOI ZIQ ZBV ZQB ZKE ZEV ZPG ICB',
                '89198RMP': 'ISN ICB ZPG ZEV ZKE ZQB ZBV ZIQ ZOI ZTO TMI TRO',
                '37125MRS': 'FBA FQS FQC FDM FBO EFR EEL EYB',
                'K0355FCA': 'ELC EGN EAU ZUB ZVF',
                'K0441FCA': 'ZZB ZUB EIA EGS ECL VWI VCS VDD V03 VTU',
                'I56720EFVM': 'VME VCS VDD VIC',
                '37668MRS': 'EPM ECE VWI ECL EFR FBO FJR FJC FSE FBP FDT',
                '37151MRS': 'EPM ECE VWI ECL EFR FBO FJR FJC FSE FBP FBF FPM',
                '37141MRS': 'FJC FSE FBP FDT',
                'K1140FCA': 'ZZB ZCB ZBL ZKE ZEV ZPG IAA IPG IBA',
                'K0823FCA': 'ZZB ZCB ZBL ZKE ZEV ZPG IAA IPG ICZ',
                'K0693FCA': 'IUF IPG IAA ZPG ZEV ZKE ZBL ZCB ZUB EAU EGN EYC',
                'K0917FCA': 'IUF IPG IAA ZPG ZEV ZKE ZBL ZCB ZUB EAU',
                'K1100FCA': 'ZZB ZCB ZBL ZKE ZEV ZPG ICB ISN',
                '89260RMC': 'IUF IPG IAA ZPG ZEV ZKE ZQB ZBV ZIQ ZOI ZTO ZRL PRV',
                'K1173FCA': 'IUF IPG IAA ZPG ZEV ZKE ZBL ZCB ZVF',
                'J0124FCA': 'ZGU ZCB ZBL ZKE ZEV ZPG IAA IPG IUF',
                'K0758FCA': 'ZGU ZCB ZBL ZKE ZEV ZPG IAA IPG ICZ',
                '89227RMC': 'ISN ICB ZPG ZEV ZKE ZQB ZBV ZIQ ZOI ZTO ZRL PRV',
                'K0893FCA': 'ZRP ZCB ZBL ZKE ZEV ZPG ICB ISN',
                'K1150FCA': 'ZGU ZCB ZBL ZKE ZEV ZPG ICB ISN'
                }

    fluxos_intermed = fill_intermed(fluxos_ocorrencias, hard_intermed)

    # salve o fluxos_ocorrencias no feature_store.db
    fluxos_intermed.to_sql('fluxos_intermed', origin_engine, if_exists='replace', index=False)
