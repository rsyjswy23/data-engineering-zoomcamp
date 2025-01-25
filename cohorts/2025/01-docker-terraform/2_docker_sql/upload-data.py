#!/usr/bin/env python
# coding: utf-8

# In[23]:


import pandas as pd


# In[24]:


pd.__version__


# In[25]:


# df = pd.read_csv('green_tripdata_2019-10.csv.gz', nrows=100)


# In[26]:


dataset_url = 'green_tripdata_2019-10.csv.gz'
df = pd.read_csv(dataset_url, low_memory=False, encoding='latin1')


# In[27]:


df


# In[28]:


pd.io.sql.get_schema(df, name='green_taxi_data')


# In[29]:


print(pd.io.sql.get_schema(df, name='green_taxi_data'))


# In[30]:


pd.to_datetime(df.lpep_pickup_datetime)


# In[31]:


df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)


# In[32]:


from sqlalchemy import create_engine


# In[33]:


engine = create_engine('postgresql://postgres:postgres@localhost:5432/ny_taxi')


# In[34]:


engine.connect()


# In[35]:


print(pd.io.sql.get_schema(df, name='green_taxi_data', con=engine))


# In[36]:


# df_iter = pd.read_csv('green_tripdata_2019-10.csv.gz', iterator=True, chunksize=50000)
df_iter = pd.read_csv(dataset_url, iterator=True, chunksize=100000, low_memory=False)


# In[37]:


df = next(df_iter)


# In[38]:


len(df)


# In[39]:


df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)


# In[40]:


df


# In[41]:


df.head(n=0).to_sql(name='green_taxi_data', con=engine, if_exists='replace')


# In[42]:


get_ipython().run_line_magic('time', "df.to_sql(name='green_taxi_data', con=engine, if_exists='append')")


# In[43]:


from time import time


# In[ ]:


while True: 
    t_start = time()

    df = next(df_iter)

    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
    
    df.to_sql(name='green_taxi_data', con=engine, if_exists='append')

    t_end = time()

    print('inserted another chunk, took %.3f second' % (t_end - t_start))


# In[ ]:


get_ipython().system('wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv')


# In[ ]:


df_zones = pd.read_csv('taxi_zone_lookup.csv')


# In[ ]:


df_zones.head()


# In[ ]:


df_zones.to_sql(name='zones', con=engine, if_exists='replace')


# In[ ]:




