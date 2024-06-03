# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 09:04:15 2024

@author: frede
"""

import pvlib
import pandas as pd
from collections import OrderedDict
from pvlib import spectrum
import numpy as np
from model_to_run_select import model_to_run_select, interval_select
from POA_function_tilt_and_vertical import shadow_interpolate_function
import matplotlib.pyplot as plt
import pytz

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 


filter_faulty = True



tz = 'UTC'
lat = 56.493786, 
lon = 9.560852,
altitude = 47
location = pvlib.location.Location(lat, lon, tz=tz)

# calculate Sun's coordinates
solar_position = location.get_solarposition(times=data.index) 

GHI_CMP6 = pd.to_numeric(data[('GHI (W.m-2)')]).copy()
GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')]).copy()
GHI_2nd = pd.to_numeric(data[('GHI_2nd station (W.m-2)')]).copy()
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')]).copy()
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')]).copy()
Albedometer = pd.to_numeric(data[('Albedometer (W.m-2)')]).copy()


GHI = shadow_interpolate_function(data, 
                                  GHI_sensor= 'GHI', 
                                  solar_position= solar_position)


#Takes the average of the albedo when the solar elevation is above 10 deg and uses that average for the whole day
albedo = Albedometer/GHI
albedo_fil = albedo[solar_position['elevation']>10]
albedo_daily_mid_day_mean = albedo_fil.resample('D').mean()
albedo_daily = albedo_daily_mid_day_mean.reindex(albedo.index, method='ffill')


#The minimum albedo
albedo_daily_mid_day_min = albedo_fil.resample('D').min()
albedo_daily_min = albedo_daily_mid_day_min.reindex(albedo.index, method='ffill')


# Calculating the time_index here overruels the start and end date
time_index_type = 'all_relevant'
time_index  = interval_select(time_index_type, data = data, filter_faulty=filter_faulty)



time_index_type1 = 'interval1'
time_index1  = interval_select(time_index_type1, data = data, filter_faulty=filter_faulty)

time_index_type2 = 'interval2'
time_index2  = interval_select(time_index_type2, data = data, filter_faulty=filter_faulty)

time_index_type3 = 'interval3'
time_index3  = interval_select(time_index_type3, data = data, filter_faulty=filter_faulty)

time_index_type4 = 'interval4'
time_index4  = interval_select(time_index_type4, data = data, filter_faulty=filter_faulty)



fig1, ax1 = plt.subplots()
fig1.suptitle('Albedo')
ax1.plot(albedo_daily[time_index3],label='Albedo_10°_avg')
ax1.set(xlabel = 'Day in the year')
ax1.set_ylim([0,1])
#ax1.set_xlim([pd.datetime.date(2023, 10,15), pd.datetime.date(2023, 10, 16)])
plt.xticks(rotation=45)
plt.legend()

continuous_time = range(len(time_index))


time_index1_date = time_index1.strftime('%Y-%m-%d')
time_index2_date = time_index2.strftime('%Y-%m-%d')
time_index3_date = time_index3.strftime('%Y-%m-%d')
time_index4_date = time_index4.strftime('%Y-%m-%d')

fig1, ax1 = plt.subplots()
fig1.suptitle('Albedo over time')
ax1.plot(continuous_time,albedo_daily[time_index],label='Albedo_10°_avg')
#ax1.set(xlabel = 'Day in the year')
ax1.set(ylabel = 'Albedo [-]')
ax1.set_ylim([0,1.2])
ax1.axvline(continuous_time[len(time_index1)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(time_index1)+ len(time_index2)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(time_index1)+ len(time_index2) + len(time_index3)], color='black', linestyle = '--')
ax1.set_xticks([])  # This removes x-ticks from the plot
ax1.text(continuous_time[len(time_index1_date)]/2, -0.1, str(time_index1_date[0])+ '\n' + time_index1_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + round((len(time_index2))/2)] , -0.1, str(time_index2_date[0])+ '\n' + time_index2_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(time_index2) + round((len(time_index3))/2)], -0.1, str(time_index3_date[0])+ '\n' + time_index3_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(time_index2) + len(time_index3) + round((len(time_index4))/2)] , -0.1, str(time_index4_date[0])+ '\n' + time_index4_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
plt.legend()


#%%%

#Importing snow data from DMI
snow_november=pd.read_csv('snow_data_dmi/november_viborg.csv',
                 index_col=0)

snow_november = snow_november.rename(columns={'Maks. snedybde': 'Max snow depth [cm]'})
snow_november = snow_november['Max snow depth [cm]']
snow_november = snow_november.dropna()


snow_november.index = pd.to_datetime(snow_november.index, format='%d-%m-%y %H:%M')


snow_november.index = pd.to_datetime(snow_november.index).tz_localize(tz='Europe/Oslo', 
                                                    ambiguous='infer',
                                                    nonexistent='shift_forward')

snow_november.index = snow_november.index.tz_convert('UTC')





snow_december=pd.read_csv('snow_data_dmi/december_viborg.csv',
                 index_col=0)

snow_december = snow_december.rename(columns={'Maks. snedybde': 'Max snow depth [cm]'})
snow_december = snow_december['Max snow depth [cm]']

snow_december.index = pd.to_datetime(snow_december.index, format='%d-%m-%y %H:%M')

snow_december.index = pd.to_datetime(snow_december.index).tz_localize(tz='Europe/Oslo', 
                                                    ambiguous='infer',
                                                    nonexistent='shift_forward')

snow_december.index = snow_december.index.tz_convert('UTC')
snow_december = snow_december.dropna()


snow_januar=pd.read_csv('snow_data_dmi/januar_viborg.csv',
                 index_col=0)

snow_januar = snow_januar.rename(columns={'Maks. snedybde': 'Max snow depth [cm]'})
snow_januar = snow_januar['Max snow depth [cm]']

snow_januar.index = pd.to_datetime(snow_januar.index, format='%d-%m-%y %H:%M')

snow_januar.index = pd.to_datetime(snow_januar.index).tz_localize(tz='Europe/Oslo', 
                                                    ambiguous='infer',
                                                    nonexistent='shift_forward')

snow_januar.index = snow_januar.index.tz_convert('UTC')
snow_januar = snow_januar.dropna()




snow_februar=pd.read_csv('snow_data_dmi/februar_viborg.csv',
                 index_col=0)

snow_februar = snow_februar.rename(columns={'Maks. snedybde': 'Max snow depth [cm]'})
snow_februar = snow_februar['Max snow depth [cm]']

snow_februar.index = pd.to_datetime(snow_februar.index, format='%d-%m-%y %H:%M')

snow_februar.index = pd.to_datetime(snow_februar.index).tz_localize(tz='Europe/Oslo', 
                                                    ambiguous='infer',
                                                    nonexistent='shift_forward')

snow_februar.index = snow_februar.index.tz_convert('UTC')
snow_februar = snow_februar.dropna()

#Combine the snow series to one
combined_series = pd.concat([snow_november,snow_december,snow_januar, snow_februar], ignore_index=False)

combined_series = combined_series.asfreq('5T', method='ffill')





# Define the target DateTimeIndex that the series should match
target_index = time_index

# Function to resample and adjust the Series
def resample_series_to_match_index(series, target_index):
    # Create a new series with the target index, fill with 0
    resampled_series = pd.Series(0, index=target_index)
    
    # Update the new series with the original data within the bounds of the target index
    # This ensures that data outside the target range are dropped and missing data at the start are filled with 0
    overlap_start = max(series.index.min(), target_index.min())
    overlap_end = min(series.index.max(), target_index.max())
    overlap_index = series.index.intersection(target_index)
    
    resampled_series.loc[overlap_index] = series.loc[overlap_index]

    return resampled_series

# Resample the original series to match the target DateTimeIndex
adjusted_series = resample_series_to_match_index(combined_series, target_index)






fig1, ax1 = plt.subplots()
fig1.suptitle('Albedo over time')
ax1.plot(continuous_time,albedo_daily[time_index],label='Albedo_10°_avg')
#ax1.set(xlabel = 'Day in the year')
ax1.set(ylabel = 'Albedo [-]')
ax1.set_ylim([0,1.2])
ax1.axvline(continuous_time[len(time_index1)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(time_index1)+ len(time_index2)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(time_index1)+ len(time_index2) + len(time_index3)], color='black', linestyle = '--')
ax1.set_xticks([])  # This removes x-ticks from the plot
ax1.text(continuous_time[len(time_index1_date)]/2, -0.1, str(time_index1_date[0])+ '\n' + time_index1_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + round((len(time_index2))/2)] , -0.1, str(time_index2_date[0])+ '\n' + time_index2_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(time_index2) + round((len(time_index3))/2)], -0.1, str(time_index3_date[0])+ '\n' + time_index3_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(time_index2) + len(time_index3) + round((len(time_index4))/2)] , -0.1, str(time_index4_date[0])+ '\n' + time_index4_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
plt.legend()
ax2= ax1.twinx()
ax2.set(ylabel = 'Snow depth [cm]')
ax2.plot(continuous_time,adjusted_series, color='red', label='Snow')
plt.legend()


#%%%

#Similar to snow just with rain


#Importing snow data from DMI
rain_may=pd.read_csv('rain_data_dmi/rain_viborg_5.csv',
                 index_col=0)

rain_may = rain_may.rename(columns={'Nedbør': 'Summed Rain [mm]'})
rain_may = rain_may['Summed Rain [mm]']
rain_may = rain_may.dropna()


rain_may.index = pd.to_datetime(rain_may.index, format='%d-%m-%y %H:%M')


rain_may.index = pd.to_datetime(rain_may.index).tz_localize(tz='Europe/Oslo', 
                                                    ambiguous='infer',
                                                    nonexistent='shift_forward')

rain_may.index = rain_may.index.tz_convert('UTC')





rain_october=pd.read_csv('rain_data_dmi/rain_viborg_10.csv',
                 index_col=0)

rain_october = rain_october.rename(columns={'Nedbør': 'Summed Rain [mm]'})
rain_october = rain_october['Summed Rain [mm]']
rain_october = rain_october.dropna()


rain_october.index = pd.to_datetime(rain_october.index, format='%d-%m-%y %H:%M')


rain_october.index = pd.to_datetime(rain_october.index).tz_localize(tz='Europe/Oslo', 
                                                    ambiguous='infer',
                                                    nonexistent='shift_forward')

rain_october.index = rain_october.index.tz_convert('UTC')






rain_november=pd.read_csv('rain_data_dmi/rain_viborg_11.csv',
                 index_col=0)

rain_november = rain_november.rename(columns={'Nedbør': 'Summed Rain [mm]'})
rain_november = rain_november['Summed Rain [mm]']
rain_november = rain_november.dropna()


rain_november.index = pd.to_datetime(rain_november.index, format='%d-%m-%y %H:%M')


rain_november.index = pd.to_datetime(rain_november.index).tz_localize(tz='Europe/Oslo', 
                                                    ambiguous='infer',
                                                    nonexistent='shift_forward')

rain_november.index = rain_november.index.tz_convert('UTC')




rain_december=pd.read_csv('rain_data_dmi/rain_viborg_12.csv',
                 index_col=0)

rain_december = rain_december.rename(columns={'Nedbør': 'Summed Rain [mm]'})
rain_december = rain_december['Summed Rain [mm]']
rain_december = rain_december.dropna()


rain_december.index = pd.to_datetime(rain_december.index, format='%d-%m-%y %H:%M')


rain_december.index = pd.to_datetime(rain_december.index).tz_localize(tz='Europe/Oslo', 
                                                    ambiguous='infer',
                                                    nonexistent='shift_forward')

rain_december.index = rain_december.index.tz_convert('UTC')




rain_january=pd.read_csv('rain_data_dmi/rain_viborg_1.csv',
                 index_col=0)

rain_january = rain_january.rename(columns={'Nedbør': 'Summed Rain [mm]'})
rain_january = rain_january['Summed Rain [mm]']
rain_january = rain_january.dropna()


rain_january.index = pd.to_datetime(rain_january.index, format='%d-%m-%y %H:%M')


rain_january.index = pd.to_datetime(rain_january.index).tz_localize(tz='Europe/Oslo', 
                                                    ambiguous='infer',
                                                    nonexistent='shift_forward')

rain_january.index = rain_january.index.tz_convert('UTC')






rain_february=pd.read_csv('rain_data_dmi/rain_viborg_2.csv',
                 index_col=0)

rain_february = rain_february.rename(columns={'Nedbør': 'Summed Rain [mm]'})
rain_february = rain_february['Summed Rain [mm]']
rain_february = rain_february.dropna()


rain_february.index = pd.to_datetime(rain_february.index, format='%d-%m-%y %H:%M')


rain_february.index = pd.to_datetime(rain_february.index).tz_localize(tz='Europe/Oslo', 
                                                    ambiguous='infer',
                                                    nonexistent='shift_forward')

rain_february.index = rain_february.index.tz_convert('UTC')





#Combine the rain series to one
combined_rain = pd.concat([rain_may, rain_october, rain_november, rain_december, rain_january, rain_february], ignore_index=False)

combined_rain = combined_rain.asfreq('5T', method='ffill')


# Resample the original series to match the target DateTimeIndex
adjusted_rain = resample_series_to_match_index(combined_rain, target_index)


fig1, ax1 = plt.subplots()
fig1.suptitle('Albedo over time')
ax1.plot(continuous_time,albedo_daily[time_index],label='Albedo_10°_avg')
#ax1.set(xlabel = 'Day in the year')
ax1.set(ylabel = 'Albedo [-]')
ax1.set_ylim([0,1.2])
ax1.axvline(continuous_time[len(time_index1)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(time_index1)+ len(time_index2)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(time_index1)+ len(time_index2) + len(time_index3)], color='black', linestyle = '--')
ax1.set_xticks([])  # This removes x-ticks from the plot
ax1.text(continuous_time[len(time_index1_date)]/2, -0.1, str(time_index1_date[0])+ '\n' + time_index1_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + round((len(time_index2))/2)] , -0.1, str(time_index2_date[0])+ '\n' + time_index2_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(time_index2) + round((len(time_index3))/2)], -0.1, str(time_index3_date[0])+ '\n' + time_index3_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(time_index2) + len(time_index3) + round((len(time_index4))/2)] , -0.1, str(time_index4_date[0])+ '\n' + time_index4_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
plt.legend()
ax2= ax1.twinx()
ax2.set(ylabel = 'Daily summed rain [mm]')
ax2.plot(continuous_time,adjusted_rain, color='red', label='Summed rain')
plt.legend()



fig1, ax1 = plt.subplots()
fig1.suptitle('Albedo over time')
ax1.plot(albedo_daily[time_index2],label='Albedo_10°_avg')
#ax1.set(xlabel = 'Day in the year')
ax1.set(ylabel = 'Albedo [-]')
ax1.set_ylim([0,1.2])
plt.legend()
ax2= ax1.twinx()
ax2.set(ylabel = 'Daily summed rain [mm]')
ax2.plot(adjusted_rain[time_index2], color='red', label='Summed rain')
plt.legend()


fig1, ax1 = plt.subplots()
fig1.suptitle('Albedo over time')
ax1.plot(albedo_daily_min[time_index1],label='Albedo_10°_avg')
#ax1.set(xlabel = 'Day in the year')
ax1.set(ylabel = 'Albedo [-]')
ax1.set_ylim([0,1.2])
plt.legend()
ax2= ax1.twinx()
ax2.set(ylabel = 'Daily summed rain [mm]')
ax2.plot(adjusted_rain[time_index1], color='red', label='Summed rain')
plt.legend()







#Takes the average of the albedo when the solar elevation is above 10 deg and uses that average for the whole day
albedo1 = Albedometer/GHI_SPN1
albedo_fil1 = albedo1[solar_position['elevation']>10]
albedo_daily_mid_day_mean1 = albedo_fil1.resample('D').mean()
albedo_daily1 = albedo_daily_mid_day_mean1.reindex(albedo.index, method='ffill')


albedo_in_shadow1 = albedo1[(solar_position['azimuth']<290) & (solar_position['azimuth']>270)]
albedo_shadow_mean = albedo_daily1.reindex(albedo_in_shadow1.index) 

filtered_series = albedo_in_shadow1[albedo_in_shadow1 >= 2 * albedo_shadow_mean]
