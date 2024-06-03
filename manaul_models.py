# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 09:57:41 2024

@author: frede
"""


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 
import pvlib
import numpy as np
from scipy.optimize import curve_fit
from POA_function import POA, POA_simple
from DC_output import DC_generation, DC_generation_temp_select
from AC_output import AC_generation
from daily_plots import daily_plots
from daily_plots import day_plot, scatter_plot, solar_pos_scat, bar_plots, day_histo_plot, reg_line
from iam_custom import iam_custom, iam_custom_read, iam_custom_days
from sklearn.metrics import mean_squared_error
import math


data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 

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
                        'orientation' : 97,
                        'tilt' : 90,
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


model_to_run = {'GHI_sensor':'GHI',                     # 'GHI', 'SPN1', 'GHI_2nd' (only hour mean)
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
                'mount_type' : 'Vertical',
                'iam_apply' : 'SAPM',
                'inverter_limit' : True,
                'DNI_model': 'dirint'}                 # 'ashrae', 'SAPM' and False       

model_explain = True
y_lines = True

#%%%


#Location of PV installation - AU Foulum
lat = installation_data['lat']
lon = installation_data['lon']
altitude= installation_data['altitude']
pitch = installation_data['pitch']
gcr = installation_data['gcr']
tilt = installation_data['tilt']
orientation = installation_data['orientation']

location = pvlib.location.Location(lat, lon, tz=tz)

solar_position = location.get_solarposition(times=data.index)
 
aoi_front = pvlib.irradiance.aoi(surface_tilt=tilt,
                           surface_azimuth=installation_data['orientation'],                              
                           solar_zenith=solar_position['apparent_zenith'],
                           solar_azimuth=solar_position['azimuth'])


aoi_back = pvlib.irradiance.aoi(surface_tilt=180-tilt,
                           surface_azimuth=installation_data['orientation']+180,                              
                           solar_zenith=solar_position['apparent_zenith'],
                           solar_azimuth=solar_position['azimuth'])

aoi_front_rad = np.deg2rad(aoi_front)
aoi_back_rad = np.deg2rad(aoi_back)



GHI_CMP6 = pd.to_numeric(data[('GHI (W.m-2)')])
GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')])
GHI_2nd = pd.to_numeric(data[('GHI_2nd station (W.m-2)')])
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
Albedometer = pd.to_numeric(data[('Albedometer (W.m-2)')])

GHI = GHI_SPN1



#Calculate the dni from the weather station measurements 
pressure = pvlib.atmosphere.alt2pres(altitude)

#calculate airmass 
airmass = pvlib.atmosphere.get_relative_airmass(solar_position['apparent_zenith'])
pressure = pvlib.atmosphere.alt2pres(altitude)
am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)

# Extraterrestrial radiation 
dni_extra = pvlib.irradiance.get_extra_radiation(data.index,epoch_year=2023)

dni_dirint = pvlib.irradiance.dirint(ghi=GHI,
                              solar_zenith=solar_position['zenith'],
                              times=data.index,
                              pressure=pressure,
                              use_delta_kt_prime=True,
                              temp_dew=None,
                              min_cos_zenith=0.065,
                              max_zenith=87)

#dni = dni_dirint

clearsky = location.get_clearsky(times=data.index,
                                 solar_position=solar_position)
   
# Semi complex model for DNI 
dni_dirindex = pvlib.irradiance.dirindex(ghi=GHI,
                                         ghi_clearsky=clearsky['ghi'],
                                         dni_clearsky=clearsky['dni'],
                                         zenith=solar_position['zenith'],
                                         times=data.index,
                                         pressure=pressure)
#dni = dni_dirindex



# Optical thickness of atmosphere due to water vapor and aerosols
turbidity = pvlib.clearsky.lookup_linke_turbidity(time=data.index,
                                                  latitude=lat,
                                                  longitude=lon,
                                                  filepath='LinkeTurbidities.h5')

clearsky_ineichen = pvlib.clearsky.ineichen(apparent_zenith=solar_position['apparent_zenith'],
                                            airmass_absolute=am_abs,
                                            linke_turbidity = turbidity,
                                            altitude=altitude,
                                            dni_extra=dni_extra,
                                            perez_enhancement=True)
   
# Complex model for DNI
dni_dirindex_turbidity = pvlib.irradiance.dirindex(ghi=GHI,
                                         ghi_clearsky=clearsky_ineichen['ghi'],
                                         dni_clearsky=clearsky_ineichen['dni'],
                                         zenith=solar_position['zenith'],
                                         times=data.index,
                                         pressure=pressure,
                                         use_delta_kt_prime=True)


#dni = dni_dirindex_turbidity       

dni_simple = pvlib.irradiance.dni(GHI,
                                  DHI_SPN1,
                                  zenith = solar_position['apparent_zenith'])


dni = dni_simple


def steven1_degrees(solar_position, aoi, tilt):
    # Convert angles from degrees to radians for trigonometric calculations
    theta_rad = np.deg2rad(aoi)
    Z_rad = np.deg2rad(solar_position['apparent_zenith'])
    s_rad = np.deg2rad(tilt)
    
    # Calculate rb as per the formula, ensuring non-negative values with np.maximum
    rb = np.maximum(0, np.cos(theta_rad) / np.cos(Z_rad))
    
    # Perform the Steven and Unsworth calculation with radian conversions for trig functions
    steven = np.sin(s_rad) - s_rad * np.cos(s_rad) - np.pi * (np.sin(s_rad / 2)) ** 2
    Rd = 0.51 * rb + (1 - 0.51) * ((np.cos(s_rad / 2)) ** 2 - 0.4395708 * steven)
    
    

    return Rd






def Liu(tilt):
    # Convert degrees to radians
    s = math.radians(tilt)
    # Calculate Rd
    Rd = (1 + math.cos(tilt)) / 2
    return Rd



Rd_steven1 = steven1_degrees(solar_position = solar_position, 
                                aoi = aoi_front, 
                                tilt = tilt)

Rd_Liu=Liu(tilt)

s_rad = np.deg2rad(tilt)
Rr = (1-np.cos(s_rad))/2

albedo = 0.2


D_steven1 = DHI_SPN1 * Rd_steven1
D_Liu = DHI_SPN1 * Rd_Liu

I_direct_front = dni * np.cos(aoi_front_rad)
I_direct_front = I_direct_front.apply(lambda x: max(0, x))


I_direct_back = dni * np.cos(aoi_back_rad)
I_direct_back = I_direct_back.apply(lambda x: max(0, x))

D_g = albedo*GHI*Rr




Irrad_front_steven1 = D_steven1 + I_direct_front + D_g

Irrad_front_Liu = D_Liu + I_direct_front + D_g

Irrad_back_Liu = D_Liu + I_direct_back + D_g




time_index = pd.date_range(start='2023-05-12', 
                       periods=24*12*1, 
                       freq='5min',
                       tz=tz)

plt.plot(Irrad_front_Liu[time_index])

plt.plot(Irrad_back_Liu[time_index])

plt.plot(dni[time_index])
plt.plot(GHI[time_index])

