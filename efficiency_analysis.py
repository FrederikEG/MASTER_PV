# -*- coding: utf-8 -*-

"""
Calculate efficiency for both systems

"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 


start_date2 = '2023-06-11 00:00:00' 
start_date3 = '2023-09-12 00:00:00'
end_date = '2023-11-30 23:55:00'

tz = 'CET' 

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) #.tz_convert(tz=tz)

time_index = pd.date_range(start=start_date2, 
                           end=end_date, 
                           freq='5min',
                           tz=tz)

time_index_day = pd.date_range(start=start_date2, 
                           periods=24*1*12, 
                           freq='5min',
                           tz=tz)

time_index_day_winter = pd.date_range(start=start_date3, 
                           periods=24*1*12, 
                           freq='5min',
                           tz=tz)
area = 80*2.280*1.134 #80 PV panels per inverter
bifaciality=0.8
irradiance_tilted = (data['Reference Cell Tilted facing up (W.m-2)'] +
                     bifaciality*data['Reference Cell Tilted facing down (W.m-2)'])

irradiance_vertical = (bifaciality*data['Reference Cell Vertical East (W.m-2)']
                       + data['Reference Cell Vertical West (W.m-2)'])

#irradiance_vertical.index += pd.DateOffset(hours=1)
data['Efficiency INV-1-TBF'] = (1000/area)* data['INV-1-TBF Total input power (kW)'] / irradiance_tilted

data['Efficiency INV-2-VBF'] = (1000/area)* data['INV-2-VBF Total input power (kW)'] / irradiance_vertical

#%%
plt.figure(figsize=(18, 30))
gs1 = gridspec.GridSpec(5, 5)
gs1.update(wspace=0.2, hspace=0.2)
ax0 = plt.subplot(gs1[0,0:3]) 
ax1 = plt.subplot(gs1[1,0:3]) 
ax2 = ax1.twinx()
ax3 = plt.subplot(gs1[2,0:3]) 
ax4 = ax3.twinx()
ax5 = plt.subplot(gs1[3,0:3]) 
ax6 = ax5.twinx()
ax7 = plt.subplot(gs1[4,0:3]) 
ax8 = ax7.twinx()
colors = ['black', 'firebrick']

ax0.plot(data['Efficiency INV-1-TBF'][time_index_day], 
         alpha=0.5,
         color=colors[0],
         marker='o',
         markersize=5,
         linewidth=0,
         label='Efficiency INV-1-TBF')
ax0.plot(data['Efficiency INV-2-VBF'][time_index_day], 
         alpha=0.5,
         color=colors[1],
         marker='o',
         markersize=5,
         linewidth=0,
         label='Efficiency INV-2-VBF')
ax0.set_ylabel('Efficiency')
ax0.grid('--')
ax0.set_ylim([0, 0.25])
ax0.legend()

sources = [ 'INV-1-TBF Total input power (kW)',
          'INV-2-VBF Total input power (kW)']

sources_r = ['Reference Cell Tilted facing up (W.m-2)',
           'Reference Cell Tilted facing down (W.m-2)',
           'GHI (W.m-2)',
           'Reference Cell Vertical East (W.m-2)',
           'Reference Cell Vertical West (W.m-2)']
for i, source in enumerate(sources[0:1]):
    ax1.plot(data[source][time_index_day], 
             alpha=0.5,
             color=colors[i],
             label=source)
    ax1.legend()
    
    ax3.plot(data[source][time_index_day_winter], 
             alpha=0.5,
             color=colors[i],
             label=source)
    ax3.legend()

for i, source in enumerate(sources_r[0:2]):
    ax2.plot(data[source][time_index_day], 
             alpha=0.5,
             label=source)
    ax2.legend() 
    ax4.plot(data[source][time_index_day_winter], 
             alpha=0.5,
             label=source)
    ax4.legend() 

for i, source in enumerate(sources[1:2]):
    ax5.plot(data[source][time_index_day], 
             alpha=0.5,
             color=colors[i],
             label=source)
    ax5.legend()
    
    ax7.plot(data[source][time_index_day_winter], 
             alpha=0.5,
             color=colors[i],
             label=source)
    ax7.legend()

for i, source in enumerate(sources_r[2:5]):
    ax6.plot(data[source][time_index_day], 
             alpha=0.5,
             label=source)
    ax6.legend() 
    ax8.plot(data[source][time_index_day_winter], 
             alpha=0.5,
             label=source)
    ax8.legend()     
    
ax1.set_ylabel('DC Power (kW)')    
ax3.set_ylabel('DC Power (kW)') 
ax2.set_ylabel('POA irradiance (W.m-2)') 
ax4.set_ylabel('POA irradiance (W.m-2)') 
ax5.set_ylabel('DC Power (kW)')    
ax6.set_ylabel('DC Power (kW)') 
ax7.set_ylabel('POA irradiance (W.m-2)') 
ax8.set_ylabel('POA irradiance (W.m-2)')

plt.savefig('Figures/Efficiency_analysis.jpg', dpi=300, bbox_inches='tight')
#%%
plt.figure(figsize=(8, 6))
gs1 = gridspec.GridSpec(1, 1)
ax0 = plt.subplot(gs1[0,0])
start_date4 = '2023-06-11 07:00:00' 
start_date5 = '2023-06-11 14:30:00' 
time_index_halfday = pd.date_range(start=start_date4, 
                           periods=10*1*12, 
                           freq='5min',
                           tz=tz)
time_index_halfday2 = pd.date_range(start=start_date5, 
                           periods=5*1*12, 
                           freq='5min',
                           tz=tz)
ax0.scatter(data['Reference Cell Tilted facing up (W.m-2)'][time_index_halfday],  
            data['Efficiency INV-1-TBF'][time_index_halfday],  
           color='dodgerblue',
           label='Efficiency INV-1-TBF')
ax0.scatter(data['Reference Cell Vertical West (W.m-2)'][time_index_halfday2],  
            data['Efficiency INV-2-VBF'][time_index_halfday2],  
           color='firebrick',
           label='Efficiency INV-2-VBF')

ax0.set_ylabel('Efficiency')
ax0.set_xlabel('Plany of Array (POA) irradiance')
ax0.grid('--')
ax0.set_ylim([0.15, 0.20])
ax0.legend()
plt.savefig('Figures/Efficiency_analysis2.jpg', dpi=300, bbox_inches='tight')