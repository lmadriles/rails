#%%
from sqlalchemy import create_engine
import geopandas as gpd

def load_data(data_transformed):
    """Load the transformed data into a SQLite database."""
    engine = create_engine('sqlite:///./data/processed/database.db', echo=False)
    
    for key, value in data_transformed.items():
        # Check if 'geometry' column exists and convert it to WKT string
        if 'geometry' in value.columns:

            # Save GeoDataFrame to a file
            value['points_geometry'] = value['points_geometry'].apply(lambda geom: geom.wkt if geom else None)
            value = gpd.GeoDataFrame(value, geometry='geometry')
            value.to_file(f'./data/processed/{key}.gpkg', driver='GPKG', index=False)
        else: 
            value.to_sql(key, con=engine, index=False, if_exists='replace')

    return
