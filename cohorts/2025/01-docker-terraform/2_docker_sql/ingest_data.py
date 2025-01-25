import pandas as pd
from sqlalchemy import create_engine
from time import time

#pd.__version__
# df = pd.read_csv('green_tripdata_2019-10.csv.gz', nrows=100)
engine = create_engine('postgresql://postgres:postgres@localhost:5432/ny_taxi')
engine.connect()

dataset_url = 'green_tripdata_2019-10.csv.gz'
df = pd.read_csv(dataset_url, low_memory=False, encoding='latin1')

pd.io.sql.get_schema(df, name='green_taxi_data')
#print(pd.io.sql.get_schema(df, name='green_taxi_data'))

#pd.to_datetime(df.lpep_pickup_datetime)
#df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
#df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

#print(pd.io.sql.get_schema(df, name='green_taxi_data', con=engine))

# df_iter = pd.read_csv('green_tripdata_2019-10.csv.gz', iterator=True, chunksize=50000)
df_iter = pd.read_csv(dataset_url, iterator=True, chunksize=100000, low_memory=False)

df = next(df_iter)
#len(df)

df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

df.head(n=0).to_sql(name='green_taxi_data', con=engine, if_exists='replace')

while True: 
    t_start = time()

    df = next(df_iter)

    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
    
    df.to_sql(name='green_taxi_data', con=engine, if_exists='append')

    t_end = time()

    print('inserted another chunk, took %.3f second' % (t_end - t_start))


#get_ipython().system('wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv')


#df_zones = pd.read_csv('taxi_zone_lookup.csv')
#df_zones.head()
#df_zones.to_sql(name='zones', con=engine, if_exists='replace')



