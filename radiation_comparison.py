# -*- coding: utf-8 -*-

"""
Compare Global Horizontal Irradiance (GHI) from the three available sources
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 
import numpy as np  
import math

start_date = '2022-12-01 00:00:00'
start_date2 = '2023-06-01 00:00:00' 
start_date3 = '2023-09-01 00:00:00' 
end_date = '2023-11-30 23:55:00'

tz = 'UTC' 

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 

time_index = pd.date_range(start=start_date, 
                           end=end_date, 
                           freq='5min',
                           tz=tz)
time_index_hour = pd.date_range(start=start_date, 
                           end=end_date, 
                           freq='H',
                           tz=tz)
time_index_day = pd.date_range(start=start_date2, 
                           periods=24*1*12, 
                           freq='5min',
                           tz=tz)
time_index_day_hour = pd.date_range(start=start_date2, 
                           periods=24*1, 
                           freq='H',
                           tz=tz)
time_index_day_winter = pd.date_range(start=start_date3, 
                           periods=24*1*12, 
                           freq='5min',
                           tz=tz)
time_index_day_hour_winter = pd.date_range(start=start_date3, 
                           periods=24*1, 
                           freq='H',
                           tz=tz)
#%%
plt.figure(figsize=(18, 18))
gs1 = gridspec.GridSpec(3, 3)
gs1.update(wspace=0.2, hspace=0.2)
ax2 = plt.subplot(gs1[1,0:3]) 
ax3 = plt.subplot(gs1[2,0:3])

pairs=[['GHI (W.m-2)','GHI_SPN1 (W.m-2)'],
       ['GHI (W.m-2)' , 'GHI_2nd station (W.m-2)'],
       ['GHI_SPN1 (W.m-2)','GHI_2nd station (W.m-2)']]

sources = ['GHI (W.m-2)', 
           'GHI_SPN1 (W.m-2)', 
           'GHI_2nd station (W.m-2)'] 

for i, pair in enumerate(pairs):
    ax1 = plt.subplot(gs1[0,i])
    ax1.plot([0,1000],[0, 1000], linewidth=1, color='black')
    time = time_index if i==0 else time_index_hour
    if i==0:     
        series_a = data[pair[0]][time]       
    else:
        series_a = data[pair[0]].resample('H').mean()[time]
    
    series_b = data[pair[1]][time] 
    
    ax1.scatter(series_a, 
                series_b,
                facecolors='None', 
                edgecolors='orange',
                s=4, 
                alpha=0.5)
    
    RMSE = math.sqrt(np.square(np.subtract(series_a,series_b)).mean())
    nRMSE = RMSE/series_a.mean()

    ax1.text(0.05, 0.95, 'nRMSE = ' + str(round(nRMSE*100,1))+'%', 
             transform=ax1.transAxes)
    
    ax1.set_xlim([0,1000])
    ax1.set_ylim([0,1000])
    ax1.set_xlabel(pair[0])
    ax1.set_ylabel(pair[1])    

for i,source in enumerate(sources):    
    time = time_index_day_hour if i==2 else time_index_day  
    time_winter = time_index_day_hour_winter if i==2 else time_index_day_winter 
    ax2.plot(data[source][time], 
             marker='o',
             markerfacecolor='None',
             markersize=4,
             alpha=0.5,
             label=source)
    ax3.plot(data[source][time_winter], 
             marker='o',
             markerfacecolor='None',
             markersize=4,
             alpha=0.5,
             label=source)
    ax2.legend()
    ax3.legend()
    ax2.set_ylabel('W.m-2')
    ax3.set_ylabel('W.m-2')
    ax2.grid('--')
    ax3.grid('--')
plt.savefig('Figures/GHI_analysis.jpg', dpi=300, bbox_inches='tight')