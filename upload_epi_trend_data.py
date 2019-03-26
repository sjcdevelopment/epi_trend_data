# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from IPython.display import display
import os
import time
import matplotlib.pyplot as plt

def get_new_growth_id(connection):
    query = f"SELECT max(growth_id) FROM growth_data"
    
    sql_object = connection.execute(query)
    
    for row in sql_object:
        growth_id = row[0]
    
    if growth_id == None:
        growth_id = 1
    return growth_id

def check_if_uploaded(connection, file):
    query = f"SELECT * FROM uploaded_filenames WHERE filename = '" + os.path.basename(file) + "'"

    sql_object = connection.execute(query)
    file_id = None
    for row in sql_object:
        file_id = row[0]
        
        
    if file_id == None:
        return False
    else:
        return True

def parse_growth_data_into_db(file, connection, engine):
    start_time = time.time()
    print("Checking if previously Uploaded...")
    if(check_if_uploaded(connection,file)):
        print("Previously Uploaded.")
        return True
    print("Not previously uploaded. Parsing data from " + os.path.basename(file))
    dataframe = pd.read_csv(file,delimiter='\t')
    x = list(dataframe.columns.values)
    
    for i in range(0,len(x)):
        x[i] = x[i].replace(".","_")
        x[i] = x[i].replace("(","_")
        x[i] = x[i].replace(")","")
        x[i] = x[i].lower()
        x[i] = x[i].replace("instance","")
    
    dataframe.columns = x    
    dataframe.insert(loc=0,column='datapoint_id', value='NULL')
    dataframe.insert(loc=1,column='growth_id', value=get_new_growth_id(connection)+1)
    dataframe.insert(loc=2,column='growth_name', value=os.path.basename(file).replace('.txt',''))
    print("Uploading to Database...")
    #print(dataframe.shape)
    close_connection(connection, engine)
    
    datapoints = len(dataframe.index)
    breaks = []
    counter = 0
    while(counter<len(dataframe.index)):
        breaks.append(counter)
        counter = counter+450
    array = dataframe.as_matrix()
    print('Estimated Time Remaining: ' + str((len(breaks))/10) + " minutes")

    for i in range(len(breaks)):
        query = 'INSERT INTO growth_data VALUES '
        if breaks[i]==max(breaks):
            chunk = array[breaks[i]:,:]
        else:
            chunk = array[breaks[i]:breaks[i+1],:]
        for j in range(np.shape(chunk)[0]):
            query = query + "("
            for k in range(np.shape(chunk)[1]):
                query = query + "'" + str(chunk[j][k]) + "' ,"
        
            query = query.rstrip(',')
            query = query + "),"
        query = query.rstrip(',')
        connection2, engine = define_connection('root','localhost','epi_trend_data')
        sql_object = connection2.execute(query)
        close_connection(connection2, engine)

    end_time = time.time()
    elapsed = end_time-start_time
    
    query = 'INSERT INTO uploaded_filenames VALUE (NULL,"'+ os.path.basename(file)+ ' ")'
    connection2, engine = define_connection('root','localhost','epi_trend_data')
    sql_object = connection2.execute(query)
    close_connection(connection2, engine)
    
    print("Upload Successful! Time elapsed: " + str(elapsed/60)[0:2] + " minutes. Total data points: " + str(datapoints))

    
    
    

    


def upload_df(connection,table,df):
    df.to_sql(name=table,con=connection,if_exists = 'append', schema="epi_trend_data",chunksize = 500, index = False)
      
    
def define_connection(user, server, schema,password=None):
    if password != None:    
        engine = sqlalchemy.create_engine('mysql+mysqlconnector://' + user + ':'+ password + '@' + server + '/' + schema, echo = False)
    else:
        engine = sqlalchemy.create_engine('mysql+mysqlconnector://' + user  + '@' + server + '/' + schema, echo = False)
    connection = engine.connect()
    session = sessionmaker(bind=engine)
    return connection, engine

    
def close_connection(connection, engine):
    connection.close()
    engine.dispose()

if __name__ == "__main__":
    
    file = "C:/Users/sswifter/Desktop/Random Data/TGR-318_amaros_MBEtrend.txt"
    connection, engine = define_connection('root','localhost','epi_trend_data')
    
    #parse_growth_data_into_db(file, connection, engine)
    
    #plot_data(connection,2)
    close_connection(connection, engine)