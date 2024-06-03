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

start_date = '2023-05-01 00:00:00'
end_date = '2023-11-01 00:00:00'
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
    
    plt.figure(figsize=(18, 18))
    gs1 = gridspec.GridSpec(2, 5)
    gs1.update(wspace=0.2, hspace=0.2)
    ax1 = plt.subplot(gs1[0,0:3]) 
    ax2 = ax1.twinx()

    ax5 = plt.subplot(gs1[1,0:3]) 
    ax6 = ax5.twinx()
    colors = ['black', 'firebrick']


    sources = [ 'INV-1-TBF Total input power (kW)',
              'INV-2-VBF Total input power (kW)']

    sources_r = ['Reference Cell Tilted facing up (W.m-2)',
               'Reference Cell Tilted facing down (W.m-2)',
               'GHI (W.m-2)',
               'Reference Cell Vertical East (W.m-2)',
               'Reference Cell Vertical West (W.m-2)']
    for i, source in enumerate(sources[0:1]):
        ax1.plot(data[source][time_index], 
                 alpha=0.5,
                 color=colors[i],
                 label=source)
        ax1.legend()
        

    for i, source in enumerate(sources_r[0:3]):
        ax2.plot(data[source][time_index], 
                 alpha=0.5,
                 label=source)
        ax2.legend() 


    for i, source in enumerate(sources[1:2]):
        ax5.plot(data[source][time_index], 
                  alpha=0.5,
                  color=colors[i],
                  label=source)
        ax5.legend()
        

    for i, source in enumerate(sources_r[2:5]):
        ax6.plot(data[source][time_index], 
                  alpha=0.5,
                  label=source)
        ax6.legend() 

        
    ax1.set_ylabel('DC Power (kW)')    
    ax2.set_ylabel('POA irradiance (W.m-2)') 
    ax5.set_ylabel('DC Power (kW)')    
    ax6.set_ylabel('POA irradiance (W.m-2)') 
    ax1.set_ylim([0, 40])
    ax2.set_ylim([0, 1100])
    ax5.set_ylim([0, 40])
    ax6.set_ylim([0, 1100])
    
    plt.savefig('Figures/daily_profiles_test/test_{}_{}_{}.jpg'.format(day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                dpi=100, bbox_inches='tight')



   