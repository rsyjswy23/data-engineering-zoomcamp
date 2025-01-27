### Running Postgres with Docker

#### Linux and MacOS

```bash
 docker run -it \
  -e POSTGRES_DB=ny_taxi \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --name pgdatabase \
  postgres:17-alpine
```

### CLI for Postgres

Create virtual env

```bash
source myenv/bin/activate
```

Install pgcli and necessary packages

```bash
pip install pgcli
```

Use `pgcli` to connect to Postgres

```bash
pgcli -h localhost -p 5432 -u postgres -d ny_taxi
```

### NY Trips Dataset

Dataset:
* https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
* https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv


### Jupyter Notebook

Install Jupyter and neccessary packages

```bash
pip install jupyter notebook
pip install pandas sqlalchemy psycopg2-binary
```

### pgAdmin

Run pgAdmin in docker

```bash
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="pgadmin@pgadmin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="pgadmin" \
  -p 8080:80 \
  dpage/pgadmin4
```

Running Postgres and pgAdmin together

Since Postgres and pgAdmin are running on different docker containers, we need to create a network for them in order to link them together.

Create a network

```bash
docker network create pg-network
```

Run Postgres (change name to pg_database)

```bash
 docker run -it \
   -e POSTGRES_DB=ny_taxi \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network=pg-network \
  --name pg-database \
  postgres:17-alpine
```

Run pgAdmin

```bash
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="pgadmin@pgadmin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="pgadmin" \
  -p 8080:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4
```
![pgAdmin_Screenshot](screenshots/pgAdmin_Screenshot.jpeg)


### Data ingestion

Putting the ingestion script into Docker

* Converting the Jupyter notebook to a Python script
* Parametrizing the script with argparse
* Dockerizing the ingestion script

```bash
jupyter nbconvert --to=script upload-data.ipynb
```

Use argparse to paratetrizing the script and run

```bash
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz"

python ingest_data.py \
  --user=postgres \
  --password=postgres \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table_name=green_taxi_data \
  --url=${URL}
```

Dockerizing the ingestion script

```bash
    docker build -t taxi_ingest:v001 .
```

After all, run docker image in the pg-network.

```bash
    URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz"
    docker run -it \
        --network=pg-network \
        taxi_ingest:v001 \
            --user=postgres \
            --password=postgres \
            --host=pg-database \
            --port=5432 \
            --db=ny_taxi \
            --table_name=green_taxi_data \
            --url=${URL}
```

Launch HTTP server 

```base
    python -m http.server
```


### Running Postgres and pgAdmin with Docker-Compose

Update Dockerfile with Docker-Compose to avoid running docker command for postgres, pgadmin and creating network seperately.

Update configuration file docker-compose.yml

Make sure to correct volume mount to parent directory that containing data files, but the file itself. 

```bash
    volumes:
      - ./ny_taxi_postgres_data:/var/lib/postgresql/data
```
 ./ny_taxi_postgres_data and vol-pgdata achieve the same goal of mounting data to postgres container, but one uses local folder to store data and the other one uses a "virtual usb". 

 
Stop and remove all containers, and remember to remove pg-network, and then spin up the contain:
```bash
   docker network rm pg-network
   docker-compose up
```
![container](screenshots/container.jpeg)

And reconfigure pgadmin server.

![reconfigure](screenshots/reconfigure.jpeg)

### SQL Refresher

You can run the following code using Jupyter Notebook to ingest the data for Taxi Zones:

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
engine.connect()

!wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv

df_zones = pd.read_csv("taxi_zone_lookup.csv")
df_zones.to_sql(name='zones', con=engine, if_exists='replace')
```

Once done, go to http://localhost:8080/browser/ to access pgAdmin.

Sample Query + Results:

1. Inner join. 
Best practics: create separate alias for the same table zones to extract different columns.

```sql
SELECT
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    total_amount,
    CONCAT(zpu."Borough", ' | ', zpu."Zone") AS "pickup_loc",
    CONCAT(zdo."Borough", ' | ', zdo."Zone") AS "dropff_loc"
FROM 
    yellow_taxi_trips t,
    zones zpu,
    zones zdo
WHERE
    t."PULocationID" = zpu."LocationID"
    AND t."DOLocationID" = zdo."LocationID"
LIMIT 100;
```
![qry1](screenshots/qry1.jpeg)


