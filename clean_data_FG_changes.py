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

def retrieve_inverter(data_path, clean_dataframe, start_date, end_date, tz): 

    """
    Retrieve inverters data (collected trough solar fussion)
    """

    #index to read the datafiles, one datafile per month, 
    time_index_month = pd.date_range(start=start_date, 
                                     end=end_date, 
                                     freq='M',  
                                     tz=tz)
    
    for m in time_index_month:
    
        fn='Inverter_{}_{}.xlsx'.format(m.year, str(m.month).zfill(2))
        print('retrieving ' + fn)
        input_data = pd.read_excel((data_path + fn),
                                   sheet_name="5 minutes", 
                                   index_col=3, 
                                   header=0, 
                                   skiprows=3,
                                   engine='openpyxl').squeeze("columns")
    
        input_data.index = pd.to_datetime(input_data.index).tz_localize(tz=tz)

        #identify data for inverter 1 (tilted bifacial) and 2 (vertical bifacial)
        inv1=input_data[input_data['ManageObject']=='Logger-1/INV-1-TBF']
        inv2=input_data[input_data['ManageObject']=='Logger-1/INV-2-VBF']

        clean_data.loc[inv1.index,['INV-1-TBF Total input power (kW)']] = inv1['Total input power(kW)']
        clean_data.loc[inv2.index,['INV-2-VBF Total input power (kW)']] = inv2['Total input power(kW)']
        clean_data.loc[inv1.index,['INV-1-TBF Active power (kW)']] = inv1['Active power(kW)']
        clean_data.loc[inv2.index,['INV-2-VBF Active power (kW)']] = inv2['Active power(kW)']
        clean_data.loc[inv2.index,['INV-2-VBF Inverter status']] = inv2['Inverter status'] #Add FG
        clean_data.loc[inv1.index,['INV-1-TBF Inverter status']] = inv1['Inverter status'] #Add FG


        clean_data.loc[inv1.index,['TBF PV1 input current (A)']] = inv1['PV1 input current(A)']
        clean_data.loc[inv1.index,['TBF PV2 input current (A)']] = inv1['PV2 input current(A)']
        clean_data.loc[inv1.index,['TBF PV3 input current (A)']] = inv1['PV3 input current(A)']
        clean_data.loc[inv1.index,['TBF PV4 input current (A)']] = inv1['PV4 input current(A)']
        clean_data.loc[inv2.index,['VBF PV1 input current (A)']] = inv2['PV1 input current(A)']
        clean_data.loc[inv2.index,['VBF PV2 input current (A)']] = inv2['PV2 input current(A)']
        clean_data.loc[inv2.index,['VBF PV3 input current (A)']] = inv2['PV3 input current(A)']
        clean_data.loc[inv2.index,['VBF PV4 input current (A)']] = inv2['PV4 input current(A)']    
        clean_data.loc[inv1.index,['TBF PV1 input voltage (V)']] = inv1['PV1 input voltage(V)']
        clean_data.loc[inv1.index,['TBF PV2 input voltage (V)']] = inv1['PV2 input voltage(V)']
        clean_data.loc[inv1.index,['TBF PV3 input voltage (V)']] = inv1['PV3 input voltage(V)']
        clean_data.loc[inv1.index,['TBF PV4 input voltage (V)']] = inv1['PV4 input voltage(V)']    
        clean_data.loc[inv2.index,['VBF PV1 input voltage (V)']] = inv2['PV1 input voltage(V)']
        clean_data.loc[inv2.index,['VBF PV2 input voltage (V)']] = inv2['PV2 input voltage(V)']
        clean_data.loc[inv2.index,['VBF PV3 input voltage (V)']] = inv2['PV3 input voltage(V)']
        clean_data.loc[inv2.index,['VBF PV4 input voltage (V)']] = inv2['PV4 input voltage(V)']
    
    clean_data.to_csv('resources/clean_data.csv')
    return clean_data
    





def retrieve_weather_station(fn, clean_dataframe, dic_columns, start_date, end_date, tz):  

    """
    Retrieve weather station data
    """  
    time_index = pd.date_range(start=start_date, 
                               end=end_date, 
                               freq='5min',  
                               tz=tz)
    data = pd.read_csv(fn, 
                   skiprows=1,
                   header=[0,1,2],
                   sep=',',
                   index_col=0, 
                   low_memory=False) 

    data.index = pd.to_datetime(data.index).tz_localize(tz=tz, 
                                                    ambiguous='NaT', #'infer',
                                                    nonexistent='shift_forward')

    # merge indices into a single index and convert values to float
    data.columns = data.columns.to_flat_index()
    data=data.astype(float)

    # remove duplicated value due to Daylight Saving Time to enable reindex
    data = data[~data.index.duplicated()]
    
    for key, value in dic_columns.items():
        clean_data.loc[time_index,key] = data[value].reindex(time_index, fill_value=np.nan) 
        
    clean_data.to_csv('resources/clean_data.csv')
    return clean_data






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

    #remove duplicated value due to Daylight Saving Time (DST)
    data = data[~data.index.duplicated()]
    
    #index to read hourly values from second weather station
    time_index_hour = pd.date_range(start=start_date, 
                                    end=end_date, 
                                    freq='H',  
                                    tz=tz)
    
    for key, value in dic_columns.items():        
        clean_data.loc[time_index_hour,key] = data[value].reindex(time_index_hour) 

    clean_data.to_csv('resources/clean_data.csv')
    return clean_data




#%%
# Create empty dataframe to be populated
tz = 'UTC' 
start_date = '2022-12-01 00:00:00'
end_date = '2023-12-31 23:55:00'
time_index = pd.date_range(start=start_date, 
                               end=end_date, 
                               freq='5min',  
                               tz=tz)
clean_data=pd.DataFrame(index=time_index)   

time_index_hour = pd.date_range(start=start_date, 
                                end=end_date, 
                                freq='H',  
                                tz=tz)
#retrieve data from inverters, dateindex in CET/CEST (indicated by DST)
data_path='data/inverter_monthly_datafiles/'
clean_data = retrieve_inverter(data_path, 
                               clean_data, 
                               start_date = '2023-04-01 00:00:00', 
                               end_date = end_date, 
                               tz='CET')

#retrieve data from weather station, dataindex in UTC
fn = 'data/weather_station_data/CR1000XSeries_2_Table2.dat'
dic_columns = {'GHI_SPN1 (W.m-2)':('Global_Avg', 'W.m-2', 'Avg'),
               'DHI_SPN1 (W.m-2)':('Diffuse_Avg', 'W.m-2', 'Avg'),
               'GHI (W.m-2)':('Solar_Wm2_2_Avg', 'W/m²', 'Avg'),
               'Albedometer (W.m-2)':('Solar_Wm2_1_Avg', 'W/m²', 'Avg'),
               'PAR (umol.s-1.m-2)':('PAR_Den_Avg', 'umol/s/m^2', 'Avg'),
               'Ambient Temperature (Deg C)':('AirTC_Avg', 'Deg C', 'Avg'),
               'Relative Humidity (%)':('RH', '%', 'Smp'),
               'Reference Cell Tilted facing up (W.m-2)':('CS325DM_Analog1_1_Avg', 'W/m²', 'Avg'),
               'Reference Cell Tilted facing down (W.m-2)':('CS325DM_Analog1_2_Avg', 'W/m²', 'Avg'),
               'Reference Cell Vertical East (W.m-2)':('CS325DM_Analog1_3_Avg', 'W/m²', 'Avg'),
               'Reference Cell Vertical West (W.m-2)':('CS325DM_Analog1_4_Avg', 'W/m²', 'Avg')} 
clean_data = retrieve_weather_station(fn, 
                                      clean_data, 
                                      dic_columns, 
                                      start_date, 
                                      end_date, 
                                      tz='UTC') 

#Data from weather station from 2023/04/18 to 2023/08/25 
fn = 'data/weather_station_data/CR1000XSeries_Table2_old.dat'
clean_data = retrieve_weather_station(fn, 
                                      clean_data, 
                                      dic_columns, 
                                      start_date = '2023-04-18 00:00:00', 
                                      end_date = '2023-08-25 23:55:00', 
                                      tz = 'UTC') 

# reference cell facing up were not properly working (broken wires)
# from 18/05/2023 to 06/09/2023 (Kamran says 26/01/2023)
time_index_tbc = pd.date_range(start='2023-05-18 00:00:00', 
                                end='2023-09-06 00:00:00', 
                                freq='5min',  
                                tz=tz)
clean_data['Reference Cell Tilted facing up (W.m-2)'][time_index_tbc]=np.nan


# reference cell in vertical setup were not properly working (broken wire)
# from 14/08/2023 to 06/09/2023
time_index_tbc = pd.date_range(start='2023-08-14 00:00:00', 
                                end='2023-09-06 00:00:00', 
                                freq='5min',  
                                tz=tz)
clean_data['Reference Cell Vertical East (W.m-2)'][time_index_tbc]=np.nan
clean_data['Reference Cell Vertical West (W.m-2)'][time_index_tbc]=np.nan

#%%
#when vertical reference cells were connected on 2023/10/09 the input where
#swapt between vertical and tilted
time_index_tbc = pd.date_range(start='2023-10-09 00:00:00', 
                                end=end_date, 
                                freq='5min',  
                                tz=tz)
save_a = clean_data['Reference Cell Tilted facing up (W.m-2)'][time_index_tbc].copy()
save_b = clean_data['Reference Cell Tilted facing down (W.m-2)'][time_index_tbc].copy()
clean_data['Reference Cell Tilted facing up (W.m-2)'][time_index_tbc] = clean_data['Reference Cell Vertical East (W.m-2)'][time_index_tbc]
clean_data['Reference Cell Tilted facing down (W.m-2)'][time_index_tbc] = clean_data['Reference Cell Vertical West (W.m-2)'][time_index_tbc]

clean_data['Reference Cell Vertical East (W.m-2)'][time_index_tbc] = save_a[time_index_tbc]
clean_data['Reference Cell Vertical West (W.m-2)'][time_index_tbc] = save_b[time_index_tbc]

#correct measuring errors in temperature sensor and relative humidity sensor
clean_data['Ambient Temperature (Deg C)'][clean_data['Ambient Temperature (Deg C)']<-80.0]=None
clean_data['Relative Humidity (%)'][clean_data['Relative Humidity (%)']==-100.0]=None


#FG changes
#Remove measurements where ref irrad is negative or too high
clean_data['Reference Cell Tilted facing up (W.m-2)'][clean_data['Reference Cell Tilted facing up (W.m-2)']<0]=None
clean_data['Reference Cell Tilted facing down (W.m-2)'][clean_data['Reference Cell Tilted facing down (W.m-2)']<0]=None

clean_data['Reference Cell Tilted facing up (W.m-2)'][clean_data['Reference Cell Tilted facing up (W.m-2)']>1361]=None
clean_data['Reference Cell Tilted facing down (W.m-2)'][clean_data['Reference Cell Tilted facing down (W.m-2)']>1361]=None

clean_data['Reference Cell Vertical West (W.m-2)'][clean_data['Reference Cell Vertical West (W.m-2)']<0]=None
clean_data['Reference Cell Vertical East (W.m-2)'][clean_data['Reference Cell Vertical East (W.m-2)']<0]=None

clean_data['Reference Cell Vertical West (W.m-2)'][clean_data['Reference Cell Vertical West (W.m-2)']>1361]=None
clean_data['Reference Cell Vertical East (W.m-2)'][clean_data['Reference Cell Vertical East (W.m-2)']>1361]=None






#Retrieve weather station data - wind sensor
fn = 'data/weather_station_data/CR1000XSeries_2_Table1.dat'
dic_columns = {'wind velocity (m.s-1)':('WS_ms_S_WVT', 'meters/second', 'WVc'),
               'wind direction (deg)':('WindDir_D1_WVT', 'Deg', 'WVc')}

clean_data = retrieve_weather_station(fn, 
                                      clean_data, 
                                      dic_columns, 
                                      start_date, 
                                      end_date, 
                                      tz='UTC')  

#Retrieve weather station data - wind sensor from 2023/04/18 to 2023/08/25 
fn = 'data/weather_station_data/CR1000XSeries_Table1_old.dat'
clean_data = retrieve_weather_station(fn, 
                                      clean_data, 
                                      dic_columns, 
                                      start_date = '2023-04-18 00:00:00', 
                                      end_date = '2023-08-25 23:55:00', 
                                      tz = 'UTC') 

#retrieve data from second weather station, dataindex in UTC?
dic_columns = {'GHI_2nd station (W.m-2)':'glorad',
               'Ambient Temperature_2nd station (Deg C)':'metp'}
fn = 'data/weather_station_6069/522945015.csv'
clean_data = retrieve_weather_station6069(fn, 
                                          clean_data, 
                                          dic_columns, 
                                          start_date, 
                                          end_date, 
                                          tz='UTC')

# Plot summary of available clean data
clean_data=clean_data.astype(float)
plt.subplots(figsize=(20,15))
ax = sns.heatmap(clean_data.loc[time_index_hour].abs()/clean_data.loc[time_index_hour].abs().max(), 
                 cmap="plasma", mask=clean_data.loc[time_index_hour].isnull())
ticklabels = [time_index_hour[int(tick)].strftime('%Y-%m-%d') for tick in ax.get_yticks()]
ax.set_yticklabels(ticklabels);
plt.savefig('Figures/summary_clean_data.jpg', dpi=300, bbox_inches='tight')

