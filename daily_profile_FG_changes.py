# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 14:49:09 2024

@author: marta.victoria.perez
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 

start_date = '2023-10-10 00:00:00'
end_date = '2023-10-30 00:00:00'
tz='UTC' 
time_index_day = pd.date_range(start=start_date, 
                                 end=end_date, 
                                 freq='D',  
                                 tz=tz)

for day in time_index_day:
    time_index = pd.date_range(start=day, 
                           periods=24*12*1, 
                           freq='5min',
                           tz=tz)
    """
    #power generation inverter
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    ax0.plot(data['INV-1-TBF Total input power (kW)'][time_index], 
              color='dodgerblue',
              label='INV-1-TBF Total input power (kW)')
    ax0.plot(data['INV-2-VBF Total input power (kW)'][time_index], 
              color='firebrick',
              label='INV-2-VBF Total input power (kW)')
    ax0.set_ylim([0,40])
    ax0.set_ylabel('DC Power (kW)')
    plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
    ax0.grid('--')
    ax0.legend()
    plt.savefig('Figures/daily_profiles/power_generation_{}_{}_{}.jpg'.format(day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                dpi=100, bbox_inches='tight')
    """
    #FG changes - plot of ref cells
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    ax0.plot(data['Reference Cell Tilted facing up (W.m-2)'][time_index], 
              color='dodgerblue',
              label='Reference Cell Tilted facing up (W.m-2)')
    ax0.plot(data['Reference Cell Tilted facing down (W.m-2)'][time_index], 
              color='firebrick',
              label='Reference Cell Tilted facing down (W.m-2)')
    ax0.plot(data['Reference Cell Vertical West (W.m-2)'][time_index], 
              color='blue',
              label='Reference Cell Vertical West (W.m-2)')  
    ax0.plot(data['Reference Cell Vertical East (W.m-2)'][time_index], 
              color='red',
              label='Reference Cell Vertical East (W.m-2)')
    ax0.set_ylim([0,1200])
    ax0.set_ylabel('Irradiance (W.m-2)')
    plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
    ax0.grid('--')
    ax0.legend()
    plt.savefig('Figures/daily_profiles/ref_cells_{}_{}_{}.jpg'.format(day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                dpi=100, bbox_inches='tight')    
    
    
    
    """
    #power generation per string
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    for i in ['1', '2', '3', '4']:
        ax0.plot(0.001*data['VBF PV{} input voltage (V)'.format(i)][time_index]*data['VBF PV{} input current (A)'.format(i)][time_index], 
             label='VBF PV{} power (kW)'.format(i))
    
    ax0.set_ylim([0,10])
    ax0.set_xlim(time_index[0], time_index[-1])
    ax0.set_ylabel('DC Power (kW)')
    plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
    ax0.grid('--')
    ax0.legend()
    plt.savefig('Figures/daily_profiles/strings_vertical_{}_{}_{}.jpg'.format(day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                dpi=100, bbox_inches='tight')

"""

   