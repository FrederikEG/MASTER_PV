# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:20:04 2024

@author: frede
"""

#Comparison between the individual rows



import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 
import matplotlib.dates as mdates
import pvlib

#import data
data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 


day='2023-05-12 00:00:00+00:00'
tz = 'UTC'

time_index = pd.date_range(start=day, 
                           periods=24*12*1, 
                           freq='5min',
                           tz=tz)

gs1 = gridspec.GridSpec(2, 2)


ax3 = plt.subplot(gs1[1,1])
#power generation per string 
colors=['firebrick', 'green', 'orange', 'gold']
for i in ['1', '2', '3', '4']:
    ax3.plot(0.001*data['VBF PV{} input voltage (V)'.format(i)][time_index]*data['VBF PV{} input current (A)'.format(i)][time_index], 
             color=colors[int(i)-1],
             alpha=0.8,
             label='vertical row {}'.format(i))
 
ax3.set_ylim([0,10])
ax3.set_xlim(time_index[0], time_index[-1])
ax3.set_ylabel('DC Power (kW)')
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%m'))
ax3.set_xlim([time_index[24], time_index[264]])
plt.setp(ax3.get_xticklabels(), ha="right", rotation=45)
ax3.grid('--')
ax3.legend(bbox_to_anchor=(1.01, 0.3))

 
ax3.text(0.05, 0.95, 'd)', 
         fontsize=20,
         horizontalalignment='center',
         verticalalignment='center', 
         transform=ax3.transAxes)

plt.savefig('Figures/figure_paper.jpg', 
                dpi=100, bbox_inches='tight')






#%%%
installation_type ='VBF' # 'VBF' or 'TBF'

from model_to_run_select import model_to_run_select, interval_select
from daily_plots import day_plot, scatter_plot, solar_pos_scat, bar_plots, day_histo_plot, reg_line


#%%% Create folder for the data 
from pathlib import Path

# Specify the name or path to the new directory
folder_name = './results/string_compare_'+str(installation_type)


# Create the directory; parents=True allows creating parent directories if needed, exist_ok=True avoids an error if the directory already exists
try:
    Path(folder_name).mkdir(parents=True, exist_ok=True)
    print(f"Directory '{folder_name}' created successfully")
except OSError as error:
    print(f"Creation of the directory '{folder_name}' failed: {error}")


model_explain = False
model_explain_scatter = False
y_lines = True
filter_faulty=True #Filters out timestamps when the irradiance from ref cells or pyranometers are too high and therefore wrong
offset_correct = False #Corrects for the offset from 0 on SPN1 during night
slope_adjust = False
ref_cell_adjust = False

interval = 'false'    # 'false' excludes no measurements

elevation_min = 0.01 



# The mount type and model variation doesn't matter - only used to extract installation data
trans_side = 'both_sides'
mount_type = 'Tilted'
model_variation = 'sensor'         # 'DNI', 'sensor', 'transposition_simple', 'transposition_inf', 'IAM', 'spectrum'
model_to_run1, model_to_run2, model_to_run3, model_to_run4, PV_data, installation_data = model_to_run_select(model_variation= model_variation, mount_type=mount_type, trans_side=trans_side)

#Location of PV installation - AU Foulum
lat = installation_data['lat']
lon = installation_data['lon']
location = pvlib.location.Location(lat, lon, tz=tz)

# calculate Sun's coordinates
solar_position = location.get_solarposition(times=data.index) 


# The vertical installation
VBF_V={'1':data['VBF PV1 input voltage (V)'].copy(),
       '2': data['VBF PV2 input voltage (V)'].copy(),
       '3': data['VBF PV3 input voltage (V)'].copy(),
       '4': data['VBF PV4 input voltage (V)'].copy()}


VBF_A={'1':data['VBF PV1 input current (A)'].copy(),
       '2': data['VBF PV2 input current (A)'].copy(),
       '3': data['VBF PV3 input current (A)'].copy(),
       '4': data['VBF PV4 input current (A)'].copy()}

VBF_P = {}
       

# The tilted installation
TBF_V={'1':data['TBF PV1 input voltage (V)'].copy(),
       '2': data['TBF PV2 input voltage (V)'].copy(),
       '3': data['TBF PV3 input voltage (V)'].copy(),
       '4': data['TBF PV4 input voltage (V)'].copy()}


TBF_A={'1':data['TBF PV1 input current (A)'].copy(),
       '2': data['TBF PV2 input current (A)'].copy(),
       '3': data['TBF PV3 input current (A)'].copy(),
       '4': data['TBF PV4 input current (A)'].copy()}

TBF_P = {}

for i in ['1','2','3','4']:
    VBF_P[i] = VBF_V[i] * VBF_A[i]
    TBF_P[i] = TBF_V[i] * TBF_A[i]




# Calculating the time_index here overruels the start and end date
time_index_type = 'interval4'    # 'all_relevant'
time_index  = interval_select(time_index_type, data = data, filter_faulty=filter_faulty)


if installation_type == 'VBF':
    power = VBF_P
    title = 'VBF string compare'
    x_power = '1'
elif installation_type == 'TBF':
    power = TBF_P
    title = 'TBF string compare'
    x_power = '4'

for i in ['1','2','3','4']:
    figure_name = str(installation_type) +'_String_'+str(i) + '_' + str(interval) 
    
    scat_index, fit_dict1 = scatter_plot(title, 
                     y_label = str(installation_type) +' String'+str(i) + ' (kW)',
                     x_label = str(installation_type) +' String'+str(x_power) + ' (kW)',
                     modelled_value = 0.001*power[x_power], 
                     measured_value = 0.001*power[i], 
                 #start_date = start_date, 
                 #end_date=end_date,
                 time_index= time_index,
                 #color_value= 'blue',
                 color_value = solar_position['azimuth'],
                 y_lim = 'default',
                 model_explain= model_explain_scatter,
                 interval= interval,
                 solar_position = solar_position,
                 elevation_min= elevation_min)  # False to have no lower bound on elevation
    plt.savefig(str(folder_name)+'/'+figure_name, dpi=300)
    


if slope_adjust == True:
    for i in ['1','2','3','4']:
        modelled_slope_adjust1 = power['1']*fit_dict1['slope']+fit_dict1['offset']
        scat_index, fit_dict1_ad = scatter_plot(title + ' slope adjusted', 
                         y_label = str(installation_type) +' String'+str(i) + ' (kW)',
                         x_label = str(installation_type) +' String 1 (kW)'+ ' slope adjusted',
                     modelled_value = 0.001 * modelled_slope_adjust1, 
                     measured_value = 0.001*power[i], 
                     #start_date = '2023-04-12 00:00:00', 
                     #end_date=end_date,
                     time_index= time_index,   
                     color_value= 'blue',
                     y_lim = 'default',
                     model_explain= model_explain_scatter,
                     interval= interval,
                     solar_position = solar_position,
                     elevation_min= elevation_min)  # False to have no lower bound on elevation
        #plt.savefig(str(folder_name)+'/'+figure_name+'_slope_adjust', dpi=300)



"""
if slope_adjust == True:
    POA_slope_adjust4 = POA4['POA fuel_in '+ str(side_of_panel)]*fit_dict4['slope'] + fit_dict4['offset']
    scat_index, fit_dict4_ad = scatter_plot('Ref '+ str(back_name)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[3])+' slope adjusted', 
                 y_label = 'Measured',
                 x_label = 'Modelled',
                 modelled_value = POA_slope_adjust4, 
                 measured_value = ref_cell, 
                 #start_date = start_date, 
                 #end_date=end_date,
                 time_index= time_index,
                 #start_date = start_date, 
                 #end_date=end_date,
                 solar_position= solar_position1,
                 interval=plot_interval_back,
                 color_value= solar_position1['azimuth'],
                 y_lim = y_lim[str(side_of_panel)],
                 model_to_run = model_to_run1,
                 model_explain= model_explain_scatter,
                 elevation_min= elevation_min1)  # False to have no lower bound on elevation
    #plt.savefig(str(folder_name)+'/'+'Ref_'+ str(back_name)+'_compare_' + str(model_variation)+ '_' +str(custom_label[3])+'_slope_adjusted', dpi=300)

"""



