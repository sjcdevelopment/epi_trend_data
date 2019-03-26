# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 15:14:55 2019

@author: sswifter
"""
import epi_trend_data_analysis as data
import upload_epi_trend_data as up
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf

def upload_growth_data_and_generate_report(file):
    
    
    connection, engine = up.define_connection('root','localhost','epi_trend_data')
    
    result = up.parse_growth_data_into_db(file, connection, engine)
    
    up.close_connection(connection, engine)
    if(result):
        print('Data already Uploaded!')
        return True
    connection, engine = up.define_connection('root','localhost','epi_trend_data')
    
    query = "SELECT * FROM growth_data where growth_id in (select max(growth_id) from growth_data)"
    df = pd.read_sql(query,connection)
    growth_id = df['growth_id'][0]
    
    data.plot_in_data(connection,growth_id)
    data.plot_ga_data(connection,growth_id)
    data.plot_si_data(connection,growth_id)
    data.plot_be_data(connection,growth_id)
    data.plot_n_data(connection,growth_id)
    
    query = "SELECT * FROM growth_data WHERE growth_id = " + growth_id
    df = pd.read_sql(query,connection)
    growth_name = df['growth_name'][0]
    
    up.close_connection(connection, engine)
    filename = "C:/Users/sswifter/Desktop/" + growth_name + "_report.pdf"
    pdf = matplotlib.backends.backend_pdf.PdfPages(filename)
    for fig in range(1, plt.gcf().number + 1): 
        
        pdf.savefig( fig )
    pdf.close()
    
file = "C:/Users/sswifter/Desktop/Random Data/TGR-419_amaros_MBEtrend.txt"    
upload_growth_data_and_generate_report(file)