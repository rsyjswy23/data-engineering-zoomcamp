import os
import argparse

import pandas as pd
from sqlalchemy import create_engine

from time import time

#pd.__version__
# df = pd.read_csv('green_tripdata_2019-10.csv.gz', nrows=100)

def main(params):
    user = params.user
    password = params.password
    host = params.host 
    port = params.port 
    db = params.db
    table_name = params.table_name
    url = params.url
    
    # the backup files are gzipped, and it's important to keep the correct extension
    # for pandas to be able to open the file
    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'

    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    #dataset_url = 'green_tripdata_2019-10.csv.gz'
    #df = pd.read_csv(csv_name, low_memory=False, encoding='latin1')

    #pd.io.sql.get_schema(df, name='green_taxi_data')
    #print(pd.io.sql.get_schema(df, name='green_taxi_data'))

    #pd.to_datetime(df.lpep_pickup_datetime)
    #df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    #df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    #print(pd.io.sql.get_schema(df, name='green_taxi_data', con=engine))

    # df_iter = pd.read_csv('green_tripdata_2019-10.csv.gz', iterator=True, chunksize=50000)
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=50000, low_memory=False)

    df = next(df_iter)
    #len(df)

    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    df.to_sql(name=table_name, con=engine, if_exists='append')

    while True: 
        try: 
            t_start = time()

            df = next(df_iter)

            df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
            df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
        
            df.to_sql(name=table_name, con=engine, if_exists='append')

            t_end = time()

            print('inserted another chunk, took %.3f second' % (t_end - t_start))

        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    parser.add_argument('--url', required=True, help='url of the csv file')

    args = parser.parse_args()

    main(args)

#get_ipython().system('wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv')
#df_zones = pd.read_csv('taxi_zone_lookup.csv')
#df_zones.head()
#df_zones.to_sql(name='zones', con=engine, if_exists='replace')



