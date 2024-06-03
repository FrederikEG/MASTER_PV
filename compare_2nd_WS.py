 # -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 15:51:11 2024

@author: frede
"""

# Compare with the secondary weather station

import pandas as pd 
import numpy as np
from daily_plots import day_plot
import matplotlib.pyplot as plt

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 


GHI_2nd = pd.to_numeric(data[('GHI_2nd station (W.m-2)')])
GHI_2nd = GHI_2nd.dropna()
GHI_2nd = GHI_2nd.asfreq('5T', method='ffill')
GHI_2nd.index = GHI_2nd.index - pd.Timedelta(hours=1) #Shifted one hour

    

GHI = pd.to_numeric(data[('GHI (W.m-2)')])[GHI_2nd.index]
GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')])[GHI_2nd.index]
ref_up = data['Reference Cell Tilted facing up (W.m-2)']

GHI_hour = GHI.resample('H').mean()
GHI_SPN1_hour = GHI_SPN1.resample('H').mean()
ref_up_hour = data['Reference Cell Tilted facing up (W.m-2)'].resample('H').mean()


GHI_5min = GHI_hour.asfreq('5T', method='ffill')
GHI_SPN1_5min = GHI_SPN1_hour.asfreq('5T', method='ffill')
ref_up_5min = ref_up_hour.asfreq('5T', method='ffill')

sun_cloud_days = ['2023-05-12 00:00:00', '2023-05-17 00:00:00']


mag_factor = GHI_2nd/GHI_5min
mag_factor.replace([np.inf, -np.inf, np.nan], 1, inplace=True)

mag_factor_smooth = mag_factor.rolling(window=12, min_periods=1).mean()

GHI_mag = GHI*mag_factor_smooth



#SPN1 
mag_factor_SPN1 = GHI_2nd/GHI_SPN1_5min
mag_factor_SPN1.replace([np.inf, -np.inf, np.nan], 1, inplace=True)

mag_factor_smooth_SPN1 = mag_factor_SPN1.rolling(window=12, min_periods=1).mean()

GHI_mag_SPN1 = GHI_SPN1*mag_factor_smooth_SPN1




day_plot('GHI compare', 
            'Irradiance',
            value1 = GHI_5min,
            value2 = GHI_SPN1_5min,
            value3 = GHI_2nd,
            y_lim= 1000,
            days = sun_cloud_days,
            custom_label=['CMP6 hour mean','SPN1 hour mean','2nd WS','','' ])




day_plot('GHI compare', 
            'Irradiance',
            value1 = GHI_2nd,
            value2 = GHI,
            value3 = GHI_SPN1,
            y_lim= 1200,
            days = sun_cloud_days,
            custom_label=['2nd WS', 'CMP6','SPN1','',''])


day_plot('GHI compare SPN1', 
            'Irradiance',
            value1 = GHI_SPN1_5min,
            value2 = GHI_2nd,
            value3= ref_up_5min,
            days = sun_cloud_days)




day_plot('GHI compare', 
            'Irradiance',
            value1 = GHI_mag,
            value2= ref_up,
            value3=GHI,
            days = sun_cloud_days)




#%%% POA calculations



#Adding all data for the PV panel to one dict
PV_data =   {'celltype' : 'monoSi', 
            'pdc0' : 555,
            'v_mp' : 42.2,
            'i_mp' : 13.16,
            'v_oc' : 50.4,
            'i_sc' : 13.93, 
            'gamma_pdc' : -0.32,
            'cells_in_series' : 144,
            'temp_ref' : 25,
            'bifaciality' : 0.8,
            'module_height' : 2.280,
            'module_width' : 1.134,
            'cell_width' : 0.182, 
            'cell_height' : 0.091}

PV_data['alpha_sc'] = 0.00046 * PV_data['i_sc']
PV_data['beta_voc'] = -0.0026 * PV_data['v_oc']


#Adding all data for the installation to one dict

installation_data =     {'lat' : 56.493786, 
                        'lon' : 9.560852,
                        'altitude' : 47,
                        'orientation' : 180,
                        'tilt' : 30,                #must be confirmed
                        'pitch' : 10,
                        'modules_per_string' : 20,
                        'strings_per_inverter' : 4,
                        'modules_vertical' : 2,
                        'w_vertical_structure' : 0.1,
                        'w_horizontal_structure' : 0.1,
                        'inverter' : 'Huawei_Technologies_Co___Ltd___SUN2000_40KTL_US__480V_'}

#installation_data['height'] = 2* PV_data['module_width'] + PV_data['module_width']
#installation_data['gcr'] = installation_data['height'] /installation_data['pitch']
installation_data['pvrow_width'] = 10*PV_data['module_height']
installation_data['height'] = 2* PV_data['module_width'] + PV_data['module_width']
installation_data['gcr'] = (2* PV_data['module_width']) /installation_data['pitch']

tz='UTC' 


model_to_run = {'GHI_sensor':'GHI',                     # 'GHI', 'GHI_SPN1', 'GHI_2nd' (only hour mean)
                'sky_model_inf':'isotropic',            # 'isotropic', 'haydavies'
                'sky_model_simple' : 'isotropic',           # 'isotropic', 'haydavies', 'perez' ......
                'shadow_interpolate' : 'true',          # 'true', 'false'
                'temp_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station' 
                'spectral_mismatch_model' : 'Sandia',   # 'Sandia', 
                'wind_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station'
                'RH_sensor' : 'default',                # 'default', 'weather_station', '2nd weather_station'  
                'shadow' : 'False',                     # 'True', 'False'
                'inverter_model' : 'Sandia',            # 'Sandia', 
                'model_perez' : 'allsitescomposite1990',
                'mount_type' : 'Tilted',
                'iam_apply' : 'SAPM',                   # 'ashrae', 'SAPM' and False  } 
                'inverter_limit' : True,
                'DNI_model': 'dirindex_turbidity'}                      # 'dirint', 'dirindex', 'dirindex_turbidity'                          

model_explain = False
y_lines = True



import pvlib
import pandas as pd
from collections import OrderedDict
from pvlib import spectrum
from shadow import shadow
import numpy as np

module_width = PV_data['module_width']

#Location of PV installation - AU Foulum
lat = installation_data['lat']
lon = installation_data['lon']
altitude= installation_data['altitude']
pitch = installation_data['pitch']
gcr = installation_data['gcr']
tilt = installation_data['tilt']
orientation = installation_data['orientation']

location = pvlib.location.Location(lat, lon, tz=tz)



#import data
data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 

#import data
data_2nd=pd.read_csv('resources/data_2nd.csv',
                 index_col=0)
data_2nd.index = pd.to_datetime(data.index, utc=True)    

    
    
    
# calculate Sun's coordinates
solar_position = location.get_solarposition(times=data.index) 


GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')])
GHI = pd.to_numeric(data[('GHI (W.m-2)')])
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
Albedometer = pd.to_numeric(data[('Albedometer (W.m-2)')])

GHI = (GHI + GHI_mag)/2

pressure = pvlib.atmosphere.alt2pres(altitude)
dni_dirint = pvlib.irradiance.dirint(ghi=GHI,
                              solar_zenith=solar_position['zenith'],
                              times=data.index,
                              pressure=pressure,
                              use_delta_kt_prime=True,
                              temp_dew=None,
                              min_cos_zenith=0.065,
                              max_zenith=87)
dni = dni_dirint
 
# Extraterrestrial radiation 
dni_extra = pvlib.irradiance.get_extra_radiation(data.index,epoch_year=2023)
   

irrad = pvlib.irradiance.get_total_irradiance(30, 180, 
                                                  solar_position['apparent_zenith'],
                                                  solar_position['azimuth'], 
                                                  dni, 
                                                  GHI, 
                                                  DHI_SPN1,
                                                  model = 'perez',
                                                  dni_extra = dni_extra)




#SPN1
GHI_SPN1 = (GHI_SPN1 + GHI_mag_SPN1)/2
irrad_SPN1 = pvlib.irradiance.get_total_irradiance(30, 180, 
                                                  solar_position['apparent_zenith'],
                                                  solar_position['azimuth'], 
                                                  dni, 
                                                  GHI_SPN1, 
                                                  DHI_SPN1,
                                                  model = 'perez',
                                                  dni_extra = dni_extra)


aoi = pvlib.irradiance.aoi(surface_tilt=30,
                           surface_azimuth=180,                              
                           solar_zenith=solar_position['apparent_zenith'],
                           solar_azimuth=solar_position['azimuth'])


#Calculate the dni from the weather station measurements 
pressure = pvlib.atmosphere.alt2pres(altitude)

#calculate airmass 
airmass = pvlib.atmosphere.get_relative_airmass(solar_position['apparent_zenith'])
pressure = pvlib.atmosphere.alt2pres(altitude)
am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
    
#Spectral loss - the module is only used for spectral losses - just needs to be the same type
sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod') 
module_sandia = sandia_modules['LG_LG290N1C_G3__2013_'] # module LG290N1C - mono crystalline si 
spec_loss_sandia = spectrum.mismatch.spectral_factor_sapm(airmass_absolute=am_abs, module=module_sandia)

iam = pvlib.iam.ashrae(aoi)
iam_diffuse =pvlib.iam.marion_diffuse(model='ashrae', surface_tilt=30)

fuel_in = ((irrad['poa_direct']*iam+irrad['poa_ground_diffuse']*iam_diffuse['ground']+irrad['poa_sky_diffuse']*iam_diffuse['sky']))*spec_loss_sandia

fuel_in_SPN1 = ((irrad_SPN1['poa_direct']*iam+irrad_SPN1['poa_ground_diffuse']*iam_diffuse['ground']+irrad_SPN1['poa_sky_diffuse']*iam_diffuse['sky']))*spec_loss_sandia




sun_cloud_days = ['2023-05-12 00:00:00', '2023-05-17 00:00:00']

day=day_plot('POA front', 
            'Irradiance',
            value1 = irrad['poa_global'],
            value2 = data['Reference Cell Tilted facing up (W.m-2)'],
            value3 = fuel_in,
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain = model_explain,
            solar_position = solar_position['azimuth'],
            y_lines = y_lines,
            #custom_yline= 'value2',
            #custom_yline = pd.DateOffset(hours = 11, minutes = 30)
            )



day=day_plot('POA front - SPN1', 
            'Irradiance',
            value1 = irrad_SPN1['poa_global'],
            value2 = data['Reference Cell Tilted facing up (W.m-2)'],
            value3 = fuel_in_SPN1,
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain = model_explain,
            solar_position = solar_position['azimuth'],
            y_lines = y_lines,
            #custom_yline= 'value2',
            #custom_yline = pd.DateOffset(hours = 11, minutes = 30)
            )


plt.plot(mag_factor_smooth)

day_plot('magfactor', 
         value1=mag_factor_smooth, 
         y_label = 'magfactor', 
         days = sun_cloud_days,
         y_lim = 2)
