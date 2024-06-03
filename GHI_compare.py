# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 09:27:03 2024

@author: frede
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 
import pvlib
import numpy as np
from scipy.optimize import curve_fit
from POA_function_tilt_and_vertical import POA, POA_simple, shadow_interpolate_function
from DC_output import DC_generation, DC_generation_temp_select
from AC_output import AC_generation
from daily_plots import daily_plots
from daily_plots import day_plot, scatter_plot, solar_pos_scat, bar_plots, day_histo_plot, reg_line
from iam_custom import iam_custom, iam_custom_read, iam_custom_days
from sklearn.metrics import mean_squared_error
import math
from model_to_run_select import model_to_run_select, interval_select


data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 


tz='UTC' 


model_explain = False
model_explain_scatter = False
y_lines = True



# The mount type and model variation doesn't matter - only used to extract installation data
mount_type = 'Tilted'
model_variation = 'sensor'         # 'DNI', 'sensor', 'transposition_simple', 'transposition_inf', 'IAM', 'spectrum'
model_to_run1, model_to_run2, model_to_run3, model_to_run4, PV_data, installation_data = model_to_run_select(model_variation= model_variation, mount_type=mount_type)

#Location of PV installation - AU Foulum
lat = installation_data['lat']
lon = installation_data['lon']
location = pvlib.location.Location(lat, lon, tz=tz)

# calculate Sun's coordinates
solar_position = location.get_solarposition(times=data.index) 


GHI_CMP6 = pd.to_numeric(data[('GHI (W.m-2)')]).copy()
GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')]).copy()
GHI_2nd = pd.to_numeric(data[('GHI_2nd station (W.m-2)')]).copy()
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')]).copy()
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')]).copy()
Albedometer = pd.to_numeric(data[('Albedometer (W.m-2)')]).copy()

ref_up = data['Reference Cell Tilted facing up (W.m-2)'].copy()


#Shift data
GHI_2nd = GHI_2nd.dropna()
GHI_2nd = GHI_2nd.asfreq('5T', method='ffill')
GHI_2nd.index = GHI_2nd.index - pd.Timedelta(hours=1) #Shifted one hour


#Select sesor to compare
sensor1 = GHI_CMP6
sensor2 = GHI_SPN1
resolution = '5T'         #Set the time resolution for the data
shadow_interpolate = True  #Makes interpolation when sensor is in shadow
interval = 'false'    # 'false' excludes no measurements
elevation_min = 0.01        # Excludes measurements with elevation lower than the min. Doesn't work with 0 but with 0.1
#elevation_min = False
#lower_limit = 200            # excludes measurements where GHI is below the limit
period = 'default'


model_explain = False
model_explain_scatter = False
y_lines = True
filter_faulty=True #Filters out timestamps when the irradiance from ref cells or pyranometers are too high and therefore wrong
offset_correct_SPN1 = True #Corrects for the offset from 0 on SPN1 during night
slope_adjust = True
ref_cell_adjust = False

exclude_day = True


time_index_type = 'all_relevant'    # 'all_relevant', 'interval1', 'interval2', 'interval3', 'interval4', 'sunny', 'cloudy'
time_index  = interval_select(time_index_type, data = data, filter_faulty=filter_faulty)


time_index_type1 = 'interval1'    # 'all_relevant', 'interval1', 'interval2', 'interval3', 'interval4', 'sunny', 'cloudy'
time_index1  = interval_select(time_index_type1, data = data, filter_faulty=filter_faulty)

if time_index_type == 'interval4' and exclude_day == True:
    day = ['2024-01-17','2024-01-18', '2024-01-19']
    for i in day:
        time_index_exclude = pd.date_range(start=i, 
                               periods=24*12*1, 
                               freq='5min',
                               tz=tz)
        mask = ~time_index.isin(time_index_exclude)
        time_index= time_index[mask]


if time_index_type == 'interval3' and exclude_day == True:
    day = ['2023-11-29','2023-12-22']
    for i in day:
        time_index_exclude = pd.date_range(start=i, 
                               periods=24*12*1, 
                               freq='5min',
                               tz=tz)
        mask = ~time_index.isin(time_index_exclude)
        time_index= time_index[mask]

if time_index_type == 'all_relevant' and exclude_day == True:
    day = ['2023-11-29','2023-12-22','2024-01-17','2024-01-18', '2024-01-19']
    for i in day:
        time_index_exclude = pd.date_range(start=i, 
                               periods=24*12*1, 
                               freq='5min',
                               tz=tz)
        mask = ~time_index.isin(time_index_exclude)
        time_index= time_index[mask]



"""
if period == 'default':
    start_date = '2023-04-12 00:00:00'
    end_date='2023-05-13 00:00:00'
elif period == 'sunny':
    start_date = '2023-05-12 00:00:00'
    end_date = '2023-05-12 23:55:00'
elif period == 'cloudy':
    start_date = '2023-05-17 00:00:00'
    end_date = '2023-05-17 23:55:00'
"""    

#Naming for file
if elevation_min == False:
    elev_numb = False
else:
    elev_numb = np.abs((int(elevation_min)))
    
if elevation_min<0:
    elev_name = 'minus'
else:
    elev_name = ''
#%%% Create folder for the data 
from pathlib import Path

# Specify the name or path to the new directory
#folder_name = './results/'+str(sensor1.name)+'_vs_'+str(sensor2.name)+'_'+str(resolution)+'_shadow_inter_'+str(shadow_interpolate)+'_offset_'+str(offset_correct)+'_elevatin_min_'+elev_name+str(elev_numb)


folder_name = './results/'+str(sensor1.name)+'_vs_'+str(sensor2.name)
figure_name = str(resolution)+ '_filter_faulty_'+str(filter_faulty)+'_shadow_inter_'+str(shadow_interpolate)+'_offset_SPN1_'+str(offset_correct_SPN1)+'_elevatin_min_'+elev_name+str(elev_numb)+'_'+time_index_type+'_exclude_day_'+str(exclude_day)

# Create the directory; parents=True allows creating parent directories if needed, exist_ok=True avoids an error if the directory already exists
try:
    Path(folder_name).mkdir(parents=True, exist_ok=True)
    print(f"Directory '{folder_name}' created successfully")
except OSError as error:
    print(f"Creation of the directory '{folder_name}' failed: {error}")


#%%%



#The interpolation function should be included here before anything with resolution 
if shadow_interpolate == True:
    GHI_CMP6 = shadow_interpolate_function(data, 
                                                   GHI_sensor = 'GHI', 
                                                   solar_position = solar_position)
    
    GHI_SPN1 = shadow_interpolate_function(data, 
                                                   GHI_sensor = 'SPN1', 
                                                   solar_position = solar_position)
    

#Offset correction of SPN1
if offset_correct_SPN1 == True:
    GHI_zero_index = GHI_CMP6[GHI_CMP6==0].index
    GHI_SPN1_offset = np.average(GHI_SPN1[GHI_zero_index])
    GHI_SPN1 = GHI_SPN1-GHI_SPN1_offset
    


#Offset correction of the reference cell
if ref_cell_adjust == True:
    GHI_zero_index = GHI_CMP6[time_index][GHI_CMP6==0].index
    ref_up_offset = ref_up[GHI_zero_index].mean()
    ref_up = ref_up - ref_up_offset


#Exclusion of measurements are done in the scatter plot function

    

if resolution =='5T':
    #Checks that only CMP6 and SPN1 are compared at 5min resolution
    if str(sensor1.name) == str(GHI_2nd.name) or str(sensor2.name) == str(GHI_2nd.name) : #or sensor2 == GHI_2nd:
        # Raise an exception with the specified error message
        raise ValueError("GHI_2nd must be compared at one hour resolution")

elif resolution == 'H':
    #Resamples the data to one hour mean
    GHI_CMP6_hour = GHI_CMP6.resample('H').mean()
    GHI_SPN1_hour = GHI_SPN1.resample('H').mean()
    ref_up_hour = data['Reference Cell Tilted facing up (W.m-2)'].resample('H').mean()

    #The index is still 5min index so here the one hour mean values are filled
    #to fit with the 5min index
    GHI_CMP6 = GHI_CMP6_hour.asfreq('5T', method='ffill')
    GHI_SPN1 = GHI_SPN1_hour.asfreq('5T', method='ffill')
    ref_up = ref_up_hour.asfreq('5T', method='ffill')
    GHI_2nd = GHI_2nd.asfreq('5T', method='ffill')
    


#Reassigning values to the sensors after conversions
if sensor1.name == 'GHI (W.m-2)':
    sensor1 = GHI_CMP6
elif sensor1.name == 'GHI_SPN1 (W.m-2)':
    sensor1 = GHI_SPN1
elif sensor1.name == 'GHI_2nd station (W.m-2)':
    sensor1 = GHI_2nd
    
if sensor2.name == 'GHI (W.m-2)':
    sensor2 = GHI_CMP6
elif sensor2.name == 'GHI_SPN1 (W.m-2)':
    sensor2 = GHI_SPN1
elif sensor2.name == 'GHI_2nd station (W.m-2)':
    sensor2 = GHI_2nd



# Input for the title of the scatter plot based on the comparison made

if resolution =='5T':
    title = 'GHI compare '+ str(sensor1.name)+' vs ' + str(sensor2.name)+ '\n at 5 minute time steps'
elif resolution == 'H':
    title = 'GHI compare '+ str(sensor1.name)+' vs ' + str(sensor2.name)+ '\n at hourly mean'
else:
    raise ValueError("Time resolution not correctly specified")

scat_index, fit_dict1 = scatter_plot(title, 
             y_label = str(sensor2.name),
             x_label = str(sensor1.name),
             modelled_value = sensor1, 
             measured_value = sensor2, 
             #start_date = start_date, 
             #end_date=end_date,
             time_index= time_index,
             color_value= 'blue',
             y_lim = 'default',
             model_explain= model_explain_scatter,
             interval= interval,
             solar_position = solar_position,
             elevation_min= elevation_min)  # False to have no lower bound on elevation
plt.savefig(str(folder_name)+'/'+figure_name, dpi=300)





if slope_adjust == True:
    modelled_slope_adjust1 = sensor1*fit_dict1['slope']+fit_dict1['offset']
    scat_index, fit_dict1_ad = scatter_plot(title + ' slope adjusted', 
                 y_label = str(sensor2.name),
                 x_label = str(sensor1.name) + 'slope adjusted',
                 modelled_value = modelled_slope_adjust1, 
                 measured_value = sensor2, 
                 #start_date = '2023-04-12 00:00:00', 
                 #end_date=end_date,
                 time_index= time_index,   
                 color_value= 'blue',
                 y_lim = 'default',
                 model_explain= model_explain_scatter,
                 interval= interval,
                 solar_position = solar_position,
                 elevation_min= elevation_min)  # False to have no lower bound on elevation
    plt.savefig(str(folder_name)+'/'+figure_name+'_slope_adjust', dpi=300)


sun_cloud_days = ['2023-05-12 00:00:00', '2023-05-17 00:00:00']

day_plot('GHI', 
            'Irradiance',
            value1 = data[('GHI (W.m-2)')],
            value2= data[('GHI_SPN1 (W.m-2)')],
            value3 = GHI_CMP6,
            value4 = GHI_SPN1,
            days = sun_cloud_days,
            model_explain= model_explain,
            solar_position = solar_position['azimuth'],
            y_lines = y_lines,
            y_lim = 1000,
            save_plots = False,
            custom_label= ['CMP6', 'SPN1', 'CMP6_interpolated','SPN1_interpolated',''])
#plt.savefig(str(folder_name)+'/'+'GHI'+ str(model_variation), dpi=300)


if resolution == 'H':
        
    day_plot('GHI hourly mean', 
                'Irradiance [W.m-2]',
                value1 = GHI_CMP6,
                value2= GHI_SPN1,
                value3 = GHI_2nd,
                value4 = ref_up,
                days = sun_cloud_days,
                model_explain= model_explain,
                solar_position = solar_position['azimuth'],
                y_lines = y_lines,
                y_lim = 1000,
                save_plots = False,
                custom_label= ['CMP6', 'SPN1', '2nd','ref_up',''])
    #plt.savefig(str(folder_name)+'/'+'GHI'+ str(model_variation), dpi=300)

    
    scat_index, fit_dict_2nd = scatter_plot('GHI 2nd vs GHI', 
                 y_label = 'GHI 2nd (W.m-2)',
                 x_label = str(sensor1.name),
                 modelled_value = sensor1, 
                 measured_value = GHI_2nd, 
                 #start_date = start_date, 
                 #end_date=end_date,
                 time_index= time_index1,
                 color_value= 'blue',
                 y_lim = 'default',
                 model_explain= model_explain_scatter,
                 interval= interval,
                 solar_position = solar_position,
                 elevation_min= elevation_min)
    
    
    scat_index, fit_dict_2nd = scatter_plot('GHI 2nd vs SPN1', 
                 y_label = 'GHI 2nd (W.m-2)',
                 x_label = str(sensor2.name),
                 modelled_value = sensor2, 
                 measured_value = GHI_2nd, 
                 #start_date = start_date, 
                 #end_date=end_date,
                 time_index= time_index1,
                 color_value= 'blue',
                 y_lim = 'default',
                 model_explain= model_explain_scatter,
                 interval= interval,
                 solar_position = solar_position,
                 elevation_min= elevation_min)
    
    scat_index, fit_dict_2nd = scatter_plot('Ref up vs ' + str(sensor2.name) , 
                 y_label = 'Ref up (W.m-2)',
                 x_label = str(sensor2.name),
                 modelled_value = sensor2, 
                 measured_value = ref_up, 
                 #start_date = start_date, 
                 #end_date=end_date,
                 time_index= time_index1,
                 color_value= 'blue',
                 y_lim = 'default',
                 model_explain= model_explain_scatter,
                 interval= interval,
                 solar_position = solar_position,
                 elevation_min= elevation_min)
    
    scat_index, fit_dict_2nd = scatter_plot('Ref up vs ' + str(sensor1.name) , 
                 y_label = 'Ref up (W.m-2)',
                 x_label = str(sensor1.name),
                 modelled_value = sensor1, 
                 measured_value = ref_up, 
                 #start_date = start_date, 
                 #end_date=end_date,
                 time_index= time_index1,
                 color_value= 'blue',
                 y_lim = 'default',
                 model_explain= model_explain_scatter,
                 interval= interval,
                 solar_position = solar_position,
                 elevation_min= elevation_min)


#csv_file_path_with_header = str(folder_name)+'/fit_data.csv'


GHI_winter = GHI_CMP6[time_index]


#%%%

import plotly.express as px
import pandas as pd
import plotly.io as pio

# Set default renderer to browser
pio.renderers.default = "browser"

# Sample DataFrame
data = {
    'sensor1': sensor1[time_index],
    'sensor2': sensor2[time_index]}

df = pd.DataFrame(data)

# Creating the scatter plot
fig = px.scatter(df, x='sensor1', y='sensor2',
                 hover_data=[df.index],  # Data to show on hover
                 title='Sensor Data Comparison',
                 labels={'sensor1': 'Sensor 1 Values', 'sensor2': 'Sensor 2 Values'})

# Displaying the plot
fig.show()
