#%% import the scr scripts
# scripts/run_etl.py
from .extract import extract_data
from .transform import transform_data
from .load import load_data

def run_etl():
    data_raw = extract_data()
    data = transform_data(data_raw)
    load_data(data)

if __name__ == "__main__":
    run_etl()
