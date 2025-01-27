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
Remember ingestion script locates inside the network and it directly communicates to Postgres DB, not the localhost. So it listens to port 5432 at Postgres DB.

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
![container](/Users/hui/Documents/GitHub/data-engineering-zoomcamp/cohorts/2025/01-docker-terraform/2_docker_sql/screenshots/container.jpg)

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

Sample Query + Results: tutorial video [text](https://www.youtube.com/watch?v=QEcps_iskgg&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=11)

# 1. Inner join (both implicit and explicit)
Best practics: create separate alias for the same table zones to extract different columns.

Joining Taxi table with Zones table (implicit INNER JOIN)
 
```sql
SELECT
    lpep_pickup_datetime,
    lpep_dropoff_datetime,
    total_amount,
    CONCAT(zpu."Borough", ' | ', zpu."Zone") AS "pickup_loc",
    CONCAT(zdo."Borough", ' | ', zdo."Zone") AS "dropff_loc"
FROM 
    green_taxi_data t,
    zones zpu,
    zones zdo
WHERE
    t."PULocationID" = zpu."LocationID"
    AND t."DOLocationID" = zdo."LocationID"
LIMIT 100;
```

Joining Taxi table with Zones table (Explicit INNER JOIN)

```sql
SELECT
    lpep_pickup_datetime,
    lpep_dropoff_datetime,
    total_amount,
    CONCAT(zpu."Borough", ' | ', zpu."Zone") AS "pickup_loc",
    CONCAT(zdo."Borough", ' | ', zdo."Zone") AS "dropff_loc"
FROM 
    green_taxi_data t
JOIN 
-- or INNER JOIN but it's less used, when writing JOIN postgreSQL undranstands implicitly that we want to use an INNER JOIN
    zones zpu ON t."PULocationID" = zpu."LocationID"
JOIN
    zones zdo ON t."DOLocationID" = zdo."LocationID"
LIMIT 100;
```

![qry1](screenshots/qry1.jpeg)


# 2. Check for records with NULL Location IDs in the Taxi table

```sql
SELECT
    lpep_pickup_datetime,
    lpep_dropoff_datetime,
    total_amount,
    "PULocationID",
    "DOLocationID"
FROM 
    green_taxi_data t
WHERE
    "PULocationID" IS NULL
    OR "DOLocationID" IS NULL
LIMIT 100;
```

# 3. Check for Location IDs in the Zones table NOT IN the green Taxi table

```sql
SELECT
    lpep_pickup_datetime,
    lpep_dropoff_datetime,
    total_amount,
    "PULocationID",
    "DOLocationID"
FROM 
    green_taxi_data t
WHERE
    "DOLocationID" NOT IN (SELECT "LocationID" from zones)
    OR "PULocationID" NOT IN (SELECT "LocationID" from zones)
LIMIT 100;
```

# 4. Use LEFT, RIGHT, and OUTER JOINS when some Location IDs are not in either Tables

```sql
DELETE FROM zones WHERE "LocationID" = 142;

SELECT
    lpep_pickup_datetime,
    lpep_dropoff_datetime,
    total_amount,
    CONCAT(zpu."Borough", ' | ', zpu."Zone") AS "pickup_loc",
    CONCAT(zdo."Borough", ' | ', zdo."Zone") AS "dropff_loc"
FROM 
    green_taxi_data t
-- left join: record will show if it exists on left table.
LEFT JOIN 
    zones zpu ON t."PULocationID" = zpu."LocationID"
JOIN
    zones zdo ON t."DOLocationID" = zdo."LocationID"
LIMIT 100;
```

```sql
SELECT
    lpep_pickup_datetime,
    lpep_dropoff_datetime,
    total_amount,
    CONCAT(zpu."Borough", ' | ', zpu."Zone") AS "pickup_loc",
    CONCAT(zdo."Borough", ' | ', zdo."Zone") AS "dropff_loc"
FROM 
    green_taxi_data t
-- right join: record will show if it exists on right table.
RIGHT JOIN 
    zones zpu ON t."PULocationID" = zpu."LocationID"
JOIN
    zones zdo ON t."DOLocationID" = zdo."LocationID"
LIMIT 100;
```

```sql
SELECT
    lpep_pickup_datetime,
    lpep_dropoff_datetime,
    total_amount,
    CONCAT(zpu."Borough", ' | ', zpu."Zone") AS "pickup_loc",
    CONCAT(zdo."Borough", ' | ', zdo."Zone") AS "dropff_loc"
FROM 
    green_taxi_data t
-- outer join: is a combination of left and right join and will show both query results.
OUTER JOIN 
    zones zpu ON t."PULocationID" = zpu."LocationID"
JOIN
    zones zdo ON t."DOLocationID" = zdo."LocationID"
LIMIT 100;
```

# 5. Using GROUP BY to calculate number of trips per day

```sql
SELECT
    CAST(lpep_dropoff_datetime AS DATE) AS "day",
    COUNT(1)
FROM 
    green_taxi_data t
GROUP BY
    CAST(lpep_dropoff_datetime AS DATE)
LIMIT 100;
```

# 6. Using ORDER BY to order the results of your query

```sql
-- Ordering by day
SELECT
    CAST(lpep_dropoff_datetime AS DATE) AS "day",
    COUNT(1)
FROM 
    green_taxi_data t
GROUP BY
    CAST(lpep_dropoff_datetime AS DATE)
ORDER BY
    "day" ASC
LIMIT 100;

-- Ordering by count

SELECT
    CAST(lpep_dropoff_datetime AS DATE) AS "day",
    COUNT(1) AS "count"
FROM 
    green_taxi_data t
GROUP BY
    CAST(lpep_dropoff_datetime AS DATE)
ORDER BY
    "count" DESC
LIMIT 100;
```

# 7. Other kinds of aggregations

```sql
SELECT
    CAST(lpep_dropoff_datetime AS DATE) AS "day",
    COUNT(1) AS "count",
    MAX(total_amount) AS "total_amount",
    MAX(passenger_count) AS "passenger_count"
FROM 
    green_taxi_data t
GROUP BY
    CAST(lpep_dropoff_datetime AS DATE)
ORDER BY
    "count" DESC
LIMIT 100;
```

# 8. Grouping by multiple fields

```sql
SELECT
    CAST(lpep_dropoff_datetime AS DATE) AS "day",
    "DOLocationID",
    COUNT(1) AS "count",
    MAX(total_amount) AS "total_amount",
    MAX(passenger_count) AS "passenger_count"
FROM 
    green_taxi_data t
-- GROUP BY 1, 2 refer to first 2 SELECT. 
GROUP BY
    1, 2
ORDER BY
    "day" ASC, 
    "DOLocationID" ASC
LIMIT 100;
```

### Port Mapping and Networks in Docker
![portmapping](screenshots/portmapping.jpeg)