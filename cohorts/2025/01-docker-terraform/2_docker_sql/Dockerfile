FROM python:3.12

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2 psycopg2-binary

WORKDIR /app
COPY ingest_data.py ingest_data.py 

ENTRYPOINT ["python", "/app/ingest_data.py"]
# ENTRYPOINT [ "python", "ingest_data.py" ]