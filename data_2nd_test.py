# -*- coding: utf-8 -*-

"""
This script retrieves raw data files from the weather stations and the 
nverters datalogger, creates a data file named 'clean_data.csv' and 
stores it in the folder 'resources'.
"""

import pandas as pd
import numpy as np
import datetime
import seaborn as sns
import matplotlib.pyplot as plt




def retrieve_weather_station6069(fn, clean_dataframe, dic_columns, start_date, end_date, tz):  

    """
    Read data from 2nd weather station 6069 (Jeroen's)
    """
    
    data = pd.read_csv(fn, 
                       sep=',',
                       low_memory=False)

    data['index'] =[datetime.datetime.strptime(x+' '+str(y).zfill(2)+':00:00',"%d/%m/%Y %H:%M:%S") 
                    for x,y in zip(data['date'],data['time'])]
    data.set_index(data['index'], drop=True, inplace=True)


    data.index = pd.to_datetime(data.index).tz_localize(tz=tz, 
                                                        ambiguous='NaT', #'infer',
                                                        nonexistent='shift_forward')
    
    #index to read hourly values from second weather station
    time_index_hour = pd.date_range(start=start_date, 
                                    end=end_date, 
                                    freq='H',  
                                    tz=tz)
    
    for key, value in dic_columns.items():        
        clean_data.loc[time_index_hour,key] = data[value].reindex(time_index_hour) 

    clean_data.to_csv('resources/data_2nd_v2.csv')
    return clean_data


# Create empty dataframe to be populated
tz = 'UTC' 
start_date = '2022-12-01 00:00:00'
#end_date = '2024-03-01 23:55:00'
end_date = '2024-05-01 23:55:00'
time_index = pd.date_range(start=start_date, 
                               end=end_date, 
                               freq='5min',  
                               tz=tz)
clean_data=pd.DataFrame(index=time_index)   

time_index_hour = pd.date_range(start=start_date, 
                                end=end_date, 
                                freq='H',  
                                tz=tz)

#retrieve data from second weather station, dataindex in UTC?
dic_columns = {'GHI_2nd station (W.m-2)':'glorad',
               'Ambient Temperature_2nd station (Deg C)':'metp',
               'wind velocity_2nd station 2m height (m.s-1)': 'wv2', 
               'wind direction_2nd station 2m height (deg)':'wd2',
               'wind velocity_2nd station 10m height (m.s-1)': 'meanwv', 
               'wind direction_2nd station 10m height (deg)':'meanwd',
               'Relative humidity (%)' : 'meanrh'
            
               }

fn = 'data/weather_station_6069/522945015.csv'
clean_data = retrieve_weather_station6069(fn, 
                                          clean_data, 
                                          dic_columns, 
                                          start_date, 
                                          end_date, 
                                          tz='UTC')

