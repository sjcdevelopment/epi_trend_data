# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 07:51:53 2019

@author: sswifter
"""
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from IPython.display import display
import os
import time
import matplotlib.pyplot as plt
from upload_epi_trend_data import define_connection, close_connection
import matplotlib
import matplotlib.transforms as mtransforms
import matplotlib.collections as collections
import matplotlib.backends.backend_pdf


def plot_data_vs_time(connection,variables,growth_id):
    i=1
    query = "SELECT * FROM growth_data WHERE growth_id = " + str(growth_id)
    df = pd.read_sql(query,connection)
    if len(variables)%3==1:
        num_rows = int(len(variables)/3)+1
    else:
        num_rows = int(len(variables)/3)
    fig = plt.figure(1,figsize=(19.2,10.8), dpi=100)
    plt.subplots_adjust(wspace = .2, hspace=.6)
    plt.suptitle(df['growth_name'][0])
    font = {'family' : 'DejaVu Sans',
        'weight' : 'normal',
        'size'   : 12}

    matplotlib.rc('font', **font)
    for variable in variables:
        try:
            
            x = df['time_seconds']
            y1= df[variable+'_measured']
            try:    
                y2 = df[variable+'_setpoint']
            except:
                y2 = df[variable+'_workingsetpoint']
            ax1 = plt.subplot(num_rows,3,i)
            ax1.plot(x,y1, label= 'measured')
            ax1.plot(x,y2, label= 'setpoint')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel(variable)
            ax1.set_title(variable + ( ' vs. time'))
            ax1.legend()
            box = ax1.get_position()
            ax1.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            i = i+1
        except:
            print('error with plotting ' + variable)
    plt.show()
    
def plot_ga_data(connection,growth_id):
    query = "SELECT * FROM growth_data WHERE growth_id = " + str(growth_id)
    df = pd.read_sql(query,connection)
    growth_name = df['growth_name'][0]
    variables = []
    for col in df.columns:
        if 'ga1' in col or 'ga2' in col or 'ga3' in col:
            variables.append(col)
    variables.append('time_seconds')
    variables_df = df[variables]
    set_meas = []
    for variable in variables:
        if 'measured' in variable:
            set_meas.append(variable.split('_measured')[0])
    for variable in set_meas:
        new_col_name = variable+'_diff_percent'
        variables_df.loc[:,new_col_name] = 0.0
        for i , row in variables_df.iterrows():
                variables_df.at[i,new_col_name] = (1-variables_df[variable+'_measured'][i]/variables_df[variable+'_setpoint'][i])*100
    
    #plot tip
    fig1, ax1 = plt.subplots()
    ax1.plot(variables_df['time_seconds'],variables_df['s_ga1_tip_diff_percent'],color='blue',label='s_ga1')
    ax1.plot(variables_df['time_seconds'],variables_df['s_ga2_tip_diff_percent'],color='red',label='s_ga2')
    ax1.plot(variables_df['time_seconds'],variables_df['s_ga3_tip_diff_percent'],color='yellow',label='s_ga3')


    #trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    t = np.linspace(0,len(variables_df['time_seconds']),len(variables_df['time_seconds'])+1)
    collection1 = collections.BrokenBarHCollection.span_where(t, ymin=2.4, ymax=2.6, where=variables_df['s_ga1_tip_shutterstatus']==0, facecolor='blue', alpha=0.5)
    ax1.add_collection(collection1)
    collection2 = collections.BrokenBarHCollection.span_where(t, ymin=2.6, ymax=2.8, where=variables_df['s_ga2_tip_shutterstatus']==0, facecolor='red', alpha=0.5)
    ax1.add_collection(collection2)
    collection3 = collections.BrokenBarHCollection.span_where(t, ymin=2.8, ymax=3, where=variables_df['s_ga3_tip_shutterstatus']==0, facecolor='yellow', alpha=0.5)
    ax1.add_collection(collection3)
    collection4 = collections.BrokenBarHCollection.span_where(t, ymin=-.5, ymax=.5,where=variables_df['s_ga3_tip_shutterstatus']<2, facecolor='green', alpha=0.3)
    ax1.add_collection(collection4)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Percent Difference Setpoint/Measured')
    ax1.set_title(growth_name+ ' Ga Tip')
    plt.xlim((0,max(t)))
    plt.ylim((-3,3))
    plt.legend()
    
    #plot base
    fig2, ax2 = plt.subplots()
    ax2.plot(variables_df['time_seconds'],variables_df['s_ga1_base_diff_percent'],color='blue',label='s_ga1')
    ax2.plot(variables_df['time_seconds'],variables_df['s_ga2_base_diff_percent'],color='red',label='s_ga2')
    ax2.plot(variables_df['time_seconds'],variables_df['s_ga3_base_diff_percent'],color='yellow',label='s_ga3')


    #trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    t = np.linspace(0,len(variables_df['time_seconds']),len(variables_df['time_seconds'])+1)
    collection1 = collections.BrokenBarHCollection.span_where(t, ymin=2.4, ymax=2.6, where=variables_df['s_ga1_tip_shutterstatus']==0, facecolor='blue', alpha=0.5)
    ax2.add_collection(collection1)
    collection2 = collections.BrokenBarHCollection.span_where(t, ymin=2.6, ymax=2.8, where=variables_df['s_ga2_tip_shutterstatus']==0, facecolor='red', alpha=0.5)
    ax2.add_collection(collection2)
    collection3 = collections.BrokenBarHCollection.span_where(t, ymin=2.8, ymax=3, where=variables_df['s_ga3_tip_shutterstatus']==0, facecolor='yellow', alpha=0.5)
    ax2.add_collection(collection3)
    collection4 = collections.BrokenBarHCollection.span_where(t, ymin=-.5, ymax=.5,where=variables_df['s_ga3_tip_shutterstatus']<2, facecolor='green', alpha=0.3)
    ax2.add_collection(collection4)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Percent Difference Setpoint/Measured')
    ax2.set_title(growth_name + ' Ga Base')
    plt.ylim((-3,3))
    plt.legend()

def plot_in_data(connection,growth_id):
    query = "SELECT * FROM growth_data WHERE growth_id = " + str(growth_id)
    df = pd.read_sql(query,connection)
    growth_name = df['growth_name'][0]
    variables = []
    for col in df.columns:
        if 'in1' in col or 'in2' in col:
            variables.append(col)
    variables.append('time_seconds')
    variables_df = df[variables]
    set_meas = []
    for variable in variables:
        if 'measured' in variable:
            set_meas.append(variable.split('_measured')[0])
    for variable in set_meas:
        new_col_name = variable+'_diff_percent'
        variables_df.loc[:,new_col_name] = 0.0
        for i , row in variables_df.iterrows():
                variables_df.at[i,new_col_name] = (1-variables_df[variable+'_measured'][i]/variables_df[variable+'_setpoint'][i])*100


    #plot tip
    fig3, ax3 = plt.subplots()
    ax3.plot(variables_df['time_seconds'],variables_df['s_in1_tip_diff_percent'],color='blue',label='s_in1')
    ax3.plot(variables_df['time_seconds'],variables_df['s_in2_tip_diff_percent'],color='red',label='s_in2')


    #trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    t = np.linspace(0,len(variables_df['time_seconds']),len(variables_df['time_seconds'])+1)
    collection1 = collections.BrokenBarHCollection.span_where(t, ymin=2.4, ymax=2.6, where=variables_df['s_in1_tip_shutterstatus']==0, facecolor='blue', alpha=0.5)
    ax3.add_collection(collection1)
    collection2 = collections.BrokenBarHCollection.span_where(t, ymin=2.6, ymax=2.8, where=variables_df['s_in2_tip_shutterstatus']==0, facecolor='red', alpha=0.5)
    ax3.add_collection(collection2)
    collection4 = collections.BrokenBarHCollection.span_where(t, ymin=-.5, ymax=.5,where=variables_df['s_in1_tip_shutterstatus']<2, facecolor='green', alpha=0.3)
    ax3.add_collection(collection4)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Percent Difference Setpoint/Measured')
    ax3.set_title(growth_name+ ' In Tip')
    plt.xlim((0,max(t)))
    plt.ylim((-3,3))
    plt.legend()
    
    #plot base
    fig4, ax4 = plt.subplots()
    ax4.plot(variables_df['time_seconds'],variables_df['s_in1_base_diff_percent'],color='blue',label='s_in1')
    ax4.plot(variables_df['time_seconds'],variables_df['s_in2_base_diff_percent'],color='red',label='s_in2')


    #trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    t = np.linspace(0,len(variables_df['time_seconds']),len(variables_df['time_seconds'])+1)
    collection1 = collections.BrokenBarHCollection.span_where(t, ymin=2.4, ymax=2.6, where=variables_df['s_in1_tip_shutterstatus']==0, facecolor='blue', alpha=0.5)
    ax4.add_collection(collection1)
    collection2 = collections.BrokenBarHCollection.span_where(t, ymin=2.6, ymax=2.8, where=variables_df['s_in2_tip_shutterstatus']==0, facecolor='red', alpha=0.5)
    ax4.add_collection(collection2)
    collection4 = collections.BrokenBarHCollection.span_where(t, ymin=-.5, ymax=.5,where=variables_df['s_in1_tip_shutterstatus']<2, facecolor='green', alpha=0.3)
    ax4.add_collection(collection4)
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Percent Difference Setpoint/Measured')
    ax4.set_title(growth_name + ' In Base')
    plt.ylim((-3,3))
    plt.legend()    


def plot_si_data(connection,growth_id):
    query = "SELECT * FROM growth_data WHERE growth_id = " + str(growth_id)
    df = pd.read_sql(query,connection)
    growth_name = df['growth_name'][0]
    variables = []
    for col in df.columns:
        if 'si1' in col:
            variables.append(col)
    variables.append('time_seconds')
    variables_df = df[variables]
    set_meas = []
    for variable in variables:
        if 'measured' in variable:
            set_meas.append(variable.split('_measured')[0])
    for variable in set_meas:
        new_col_name = variable+'_diff_percent'
        variables_df.loc[:,new_col_name] = 0.0
        for i , row in variables_df.iterrows():
                variables_df.at[i,new_col_name] = (1-variables_df[variable+'_measured'][i]/variables_df[variable+'_setpoint'][i])*100
    #plot base
    fig5, ax5 = plt.subplots()
    ax5.plot(variables_df['time_seconds'],variables_df['s_si1_base_diff_percent'],color='blue',label='s_si1')

    #trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    t = np.linspace(0,len(variables_df['time_seconds']),len(variables_df['time_seconds'])+1)
    collection1 = collections.BrokenBarHCollection.span_where(t, ymin=2.4, ymax=2.6, where=variables_df['s_si1_base_shutterstatus']==0, facecolor='blue', alpha=0.5)
    ax5.add_collection(collection1)
    collection4 = collections.BrokenBarHCollection.span_where(t, ymin=-.5, ymax=.5,where=variables_df['s_si1_base_shutterstatus']<2, facecolor='green', alpha=0.3)
    ax5.add_collection(collection4)
    ax5.set_xlabel('Time (s)')
    ax5.set_ylabel('Percent Difference Setpoint/Measured')
    ax5.set_title(growth_name + ' Si Base')
    plt.ylim((-3,3))
    plt.legend() 

def plot_be_data(connection,growth_id):
    query = "SELECT * FROM growth_data WHERE growth_id = " + str(growth_id)
    df = pd.read_sql(query,connection)
    growth_name = df['growth_name'][0]
    variables = []
    for col in df.columns:
        if 'be1' in col:
            variables.append(col)
    variables.append('time_seconds')
    variables_df = df[variables]
    set_meas = []
    print(variables)
    for variable in variables:
        if 'measured' in variable:
            set_meas.append(variable.split('_measured')[0])
    for variable in set_meas:
        try:
            new_col_name = variable+'_diff_percent'
            variables_df.loc[:,new_col_name] = 0.0
            for i , row in variables_df.iterrows():
                    variables_df.at[i,new_col_name] = (1-variables_df[variable+'_measured'][i]/variables_df[variable+'_setpoint'][i])*100
        except:
            print('cant parse' + variable)
    #plot base
    fig5, ax5 = plt.subplots()
    ax5.plot(variables_df['time_seconds'],variables_df['s_be1_be_diff_percent'],color='blue',label='s_be1')

    #trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    t = np.linspace(0,len(variables_df['time_seconds']),len(variables_df['time_seconds'])+1)
    collection1 = collections.BrokenBarHCollection.span_where(t, ymin=2.4, ymax=2.6, where=variables_df['s_be1_state_shutterstatus']==0, facecolor='blue', alpha=0.5)
    ax5.add_collection(collection1)
    collection4 = collections.BrokenBarHCollection.span_where(t, ymin=-.5, ymax=.5,where=variables_df['s_be1_state_shutterstatus']<2, facecolor='green', alpha=0.3)
    ax5.add_collection(collection4)
    ax5.set_xlabel('Time (s)')
    ax5.set_ylabel('Percent Difference Setpoint/Measured')
    ax5.set_title(growth_name + ' Be')
    plt.ylim((-3,3))
    plt.legend()
    
    
    fig9, ax9 = plt.subplots(3,1)
    ax9[0].plot(variables_df['time_seconds'],variables_df['s_be1_pressure_measured'],color='blue',label='meas')
    ax9[0].set_ylabel('be1 Pressure')
    fig9.legend()
    
    ax9[1].plot(variables_df['time_seconds'],variables_df['s_be1_state_measured'],color='blue',label='meas')
    ax9[1].set_ylabel('be1 State')
    
    ax9[2].plot(variables_df['time_seconds'],variables_df['s_be1_state_shutterstatus'],color='blue',label='meas')
    ax9[2].set_ylabel('Be Shutter')
    fig9.suptitle(growth_name + ' Be pressure and State')

def plot_n_data(connection,growth_id):
    query = "SELECT * FROM growth_data WHERE growth_id = " + str(growth_id)
    df = pd.read_sql(query,connection)
    growth_name = df['growth_name'][0]
    variables = []
    for col in df.columns:
        if '_n1' in col or '_n2' in col:
            variables.append(col)
    variables.append('time_seconds')
    variables_df = df[variables]
    
    fig7, ax7 = plt.subplots(5,2,figsize=(19.2,10.8), dpi=100)
    plt.subplots_adjust(wspace = .2, hspace=.4)

    ax7[0,0].plot(variables_df['time_seconds'],variables_df['s_n1_rf_tuningcap_measured'],color='blue',label='meas')
    ax7[0,0].plot(variables_df['time_seconds'],variables_df['s_n1_rf_tuningcap_setpoint'],color='red',label='set')
    ax7[0,0].set_ylabel('n1 Tuning Cap')
    fig7.legend()
    
    ax7[0,1].plot(variables_df['time_seconds'],variables_df['s_n2_rf_tuningcap_measured'],color='blue',label='meas')
    ax7[0,1].plot(variables_df['time_seconds'],variables_df['s_n2_rf_tuningcap_setpoint'],color='red',label='set')
    ax7[0,1].set_ylabel('n2 Tuning Cap')
    
    ax7[1,0].plot(variables_df['time_seconds'],variables_df['s_n1_rf_loadcap_measured'],color='blue',label='meas')
    ax7[1,0].plot(variables_df['time_seconds'],variables_df['s_n1_rf_loadcap_setpoint'],color='red',label='set')
    ax7[1,0].set_ylabel('n1 Load Cap')
    
    ax7[1,1].plot(variables_df['time_seconds'],variables_df['s_n2_rf_loadcap_measured'],color='blue',label='meas')
    ax7[1,1].plot(variables_df['time_seconds'],variables_df['s_n2_rf_loadcap_setpoint'],color='red',label='set')
    ax7[1,1].set_ylabel('n2 Load Cap')
    
    ax7[2,0].plot(variables_df['time_seconds'],variables_df['s_n1_mfc_run_measured'],color='blue',label='meas')
    ax7[2,0].plot(variables_df['time_seconds'],variables_df['s_n1_mfc_run_setpoint'],color='red',label='set')
    ax7[2,0].set_ylabel('n1 MFC run')
    
    ax7[2,1].plot(variables_df['time_seconds'],variables_df['s_n2_mfc_run_measured'],color='blue',label='meas')
    ax7[2,1].plot(variables_df['time_seconds'],variables_df['s_n2_mfc_run_setpoint'],color='red',label='set')
    ax7[2,1].set_ylabel('n2 MFC run')

    ax7[3,0].plot(variables_df['time_seconds'],variables_df['s_n1_rf_forward_measured'],color='blue',label='meas')
    ax7[3,0].plot(variables_df['time_seconds'],variables_df['s_n1_rf_forward_setpoint'],color='red',label='set')
    ax7[3,0].set_ylabel('n1 Forward')
    
    ax7[3,1].plot(variables_df['time_seconds'],variables_df['s_n2_rf_forward_measured'],color='blue',label='meas')
    ax7[3,1].plot(variables_df['time_seconds'],variables_df['s_n2_rf_forward_setpoint'],color='red',label='set')
    ax7[3,1].set_ylabel('n2 Forward')
    
    ax7[4,0].plot(variables_df['time_seconds'],variables_df['s_n1_mfc_run_shutterstatus'],color='blue',label='meas')
    ax7[4,0].set_ylabel('Shutter')
    ax7[4,0].set_xlabel('Time (s)')
    
    ax7[4,1].plot(variables_df['time_seconds'],variables_df['s_n1_mfc_run_shutterstatus'],color='blue',label='meas')
    ax7[4,1].set_ylabel('Shutter')
    ax7[4,1].set_xlabel('Time (s)')
    
    fig7.suptitle(growth_name + ' N data')
    
    
def plot_as_data(connection,growth_id):
    query = "SELECT * FROM growth_data WHERE growth_id = " + str(growth_id)
    df = pd.read_sql(query,connection)
    growth_name = df['growth_name'][0]
    variables = []
    for col in df.columns:
        if 'as1' in col or 'as2' in col or 'as3' in col:
            variables.append(col)
    variables.append('time_seconds')
    variables_df = df[variables]
    set_meas = []
    for variable in variables:
        if 'measured' in variable:
            set_meas.append(variable.split('_measured')[0])
    for variable in set_meas:
        new_col_name = variable+'_diff_percent'
        variables_df.loc[:,new_col_name] = 0.0
        for i , row in variables_df.iterrows():
                variables_df.at[i,new_col_name] = (1-variables_df[variable+'_measured'][i]/variables_df[variable+'_setpoint'][i])*100
    #plot base
    fig1, ax1 = plt.subplots()
    ax1.plot(variables_df['time_seconds'],variables_df['s_as1_bulk_diff_percent'],color='green',label='s_as1')
    ax1.plot(variables_df['time_seconds'],variables_df['s_as2_bulk_diff_percent'],color='blue',label='s_as2')

    #trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    t = np.linspace(0,len(variables_df['time_seconds']),len(variables_df['time_seconds'])+1)
    collection1 = collections.BrokenBarHCollection.span_where(t, ymin=1, ymax=2, where=variables_df['s_as1_valve_shutterstatus']==0, facecolor='green', alpha=0.5)
    ax1.add_collection(collection1)
    collection2 = collections.BrokenBarHCollection.span_where(t, ymin=2, ymax=3, where=variables_df['s_as2_valve_shutterstatus']==0, facecolor='blue', alpha=0.5)
    ax1.add_collection(collection2)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Percent Difference Setpoint/Measured')
    ax1.set_title(growth_name+ ' As Bulk')
    plt.ylim((-7,7))
    plt.legend()
    
    #plot crack
    fig1, ax1 = plt.subplots()
    ax1.plot(variables_df['time_seconds'],variables_df['s_as1_crack_diff_percent'],color='green',label='s_as1')
    ax1.plot(variables_df['time_seconds'],variables_df['s_as2_crack_diff_percent'],color='blue',label='s_as2')

    #trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    t = np.linspace(0,len(variables_df['time_seconds']),len(variables_df['time_seconds'])+1)
    collection1 = collections.BrokenBarHCollection.span_where(t, ymin=1, ymax=2, where=variables_df['s_as1_valve_shutterstatus']==0, facecolor='green', alpha=0.5)
    ax1.add_collection(collection1)
    collection2 = collections.BrokenBarHCollection.span_where(t, ymin=2, ymax=3, where=variables_df['s_as2_valve_shutterstatus']==0, facecolor='blue', alpha=0.5)
    ax1.add_collection(collection2)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Percent Difference Setpoint/Measured')
    ax1.set_title(growth_name+ ' As Crack')
    plt.ylim((-7,7))
    plt.legend()
    
    #plot valve
    fig1, ax1 = plt.subplots()
    ax1.plot(variables_df['time_seconds'],variables_df['s_as1_valve_diff_percent'],color='green',label='s_as1')
    ax1.plot(variables_df['time_seconds'],variables_df['s_as2_valve_diff_percent'],color='blue',label='s_as2')

    #trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    t = np.linspace(0,len(variables_df['time_seconds']),len(variables_df['time_seconds'])+1)
    collection1 = collections.BrokenBarHCollection.span_where(t, ymin=1, ymax=2, where=variables_df['s_as1_valve_shutterstatus']==0, facecolor='green', alpha=0.5)
    ax1.add_collection(collection1)
    collection2 = collections.BrokenBarHCollection.span_where(t, ymin=2, ymax=3, where=variables_df['s_as2_valve_shutterstatus']==0, facecolor='blue', alpha=0.5)
    ax1.add_collection(collection2)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Percent Difference Setpoint/Measured')
    ax1.set_title(growth_name+ ' As Valve')
    plt.ylim((-7,7))
    plt.legend()
    
def check_measured_vs_setpoint(connection, growth_id):
    query = "SELECT * FROM growth_data WHERE growth_id = " + str(growth_id)
    df = pd.read_sql(query,connection)
    cols = df.columns
    set_meas = []
    for var in cols:
        if 'setpoint' in var and 'workingsetpoint' not in var:
            var_name = var.split('_setpoint')[0]
            set_meas.append(var_name)
        if 'workingsetpoint' in var:
            var_name = var.split('_workingsetpoint')[0]
            set_meas.append(var_name)
    cols_to_plot = []
    for variable in set_meas:
        try:    
            try:
                setpoint_data = df[variable + '_setpoint']
            except:
                setpoint_data = df[variable + '_workingsetpoint']
            meas_data = df[variable + '_measured']
            percent_diff_array = []
            try:
                for i in range(len(meas_data)):
                    if setpoint_data[i] != 0:
                        percent_diff_array.append(np.abs((1-meas_data[i]/setpoint_data[i])*100))
            except:
                pass
            avg_percent_diff = np.average(percent_diff_array)
            if avg_percent_diff>=5:
                cols_to_plot.append(variable)
        except:
            print('error with ' + variable)
    return cols_to_plot


if __name__ == "__main__":
   
    connection, engine = define_connection('root','localhost','epi_trend_data')

    plot_in_data(connection,2)
    plot_ga_data(connection,2)
    plot_si_data(connection,2)
    plot_be_data(connection,2)
    plot_n_data(connection,2)
    
    query = "SELECT * FROM growth_data WHERE growth_id = " + str(2)
    df = pd.read_sql(query,connection)
    growth_name = df['growth_name'][0]
    
    close_connection(connection, engine)
    filename = "C:/Users/sswifter/Desktop/" + growth_name + "_report.pdf"
    pdf = matplotlib.backends.backend_pdf.PdfPages(filename)
    for fig in range(1, plt.gcf().number + 1): 
        
        pdf.savefig( fig )
    pdf.close()