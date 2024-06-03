# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 14:02:01 2024

@author: frede
"""

import pvlib
import pandas as pd
import matplotlib.pyplot as plt
import pytz
import numpy as np
import datetime
import matplotlib.gridspec as gridspec      
from pvlib.bifacial.pvfactors import pvfactors_timeseries
from pvlib import spectrum, solarposition, irradiance, atmosphere
from pvlib.pvsystem import PVSystem
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 

#PV module
celltype = 'monoSi' 
pdc0 = 555
v_mp = 42.2
i_mp = 13.16
v_oc = 50.4
i_sc = 13.93
alpha_sc = 0.00046 *i_sc
beta_voc = -0.0026 *v_oc     
gamma_pdc = -0.32
cells_in_series = 144
temp_ref = 25
bifaciality = 0.8
module_height = 2.280
module_width = 1.134
cell_width = 0.182 
cell_height = 0.091
cell_area = cell_width*cell_height

#Location of PV installation - AU Foulum
lat = 56.48985507481198 
lon = 9.583764312381613
altitude= 63

tz='UTC' 


location = pvlib.location.Location(lat, lon, tz=tz)
orientation = 90 # pvlib sets orientation origin at North -> South=180
tilt = 90    #Degrees from horizontal


pitch = 10 #Distance betweeen rows
height = 2*module_width+module_width
gcr = height/pitch
pvrow_width = 10*module_height






#import data
data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 


GHI = pd.to_numeric(data[('GHI (W.m-2)')])
GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')])
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
Albedometer = pd.to_numeric(data[('Albedometer (W.m-2)')])
wind_speed = pd.to_numeric(data[('wind velocity (m.s-1)')])
temp_air = pd.to_numeric(data[('Ambient Temperature (Deg C)')])

GHI = (GHI+GHI_SPN1)/2

# calculate Sun's coordinates
solar_position = location.get_solarposition(times=data.index) 

#Calculate the dni from the weather station measurements 
pressure = pvlib.atmosphere.alt2pres(altitude)

#calculate airmass 
airmass = pvlib.atmosphere.get_relative_airmass(solar_position['apparent_zenith'])
pressure = pvlib.atmosphere.alt2pres(altitude)
am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)

#%%% Wind speed equation from www.wind-data.ch

#Estimation of the wind speed in 10 meter from the measurement in 2 meter 

h_2 = 10 #height where the wind speed is needed for temperature calculations with sandia
h_1 = 2 #height of the anemomenter at the weather station 
z_0 = 0.03 #roughness height
wind_10 = wind_speed*(np.log(h_2/z_0)/np.log(h_1/z_0))
wind_speed = wind_10
#%%%

# Extraterrestrial radiation 
dni_extra = pvlib.irradiance.get_extra_radiation(data.index,epoch_year=2023)

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

dni_dirindex_turbidity = pvlib.irradiance.dirindex(ghi=GHI,
                                         ghi_clearsky=clearsky_ineichen['ghi'],
                                         dni_clearsky=clearsky_ineichen['dni'],
                                         zenith=solar_position['zenith'],
                                         times=data.index,
                                         pressure=pressure)

dni = dni_dirindex_turbidity

#Takes the average of the albedo when the solar elevation is above 10 deg and uses that average for the whole day
albedo = Albedometer/GHI
albedo_fil = albedo[solar_position['elevation']>10]
albedo_daily_mid_day_mean = albedo_fil.resample('D').mean()
albedo_daily = albedo_daily_mid_day_mean.reindex(albedo.index, method='ffill')

#%%% Using infinite sheds 


pitch = 10 #Distance betweeen rows
height_mid = 2*module_width #height of center point
gcr = height/pitch
pvrow_width = 10*module_height


poa_infinite_sheds = pvlib.bifacial.infinite_sheds.get_irradiance(surface_tilt=tilt,
                                             surface_azimuth=orientation,
                                             solar_zenith=solar_position['apparent_zenith'],
                                             solar_azimuth=solar_position['azimuth'],
                                             gcr=gcr,
                                             height=height_mid,
                                             pitch=pitch,
                                             ghi=GHI,
                                             dhi=DHI_SPN1,
                                             dni=dni,
                                             albedo=albedo_daily,
                                             iam_front=1.0,
                                             iam_back=1.0,
                                             bifaciality=1,
                                             shade_factor= 0,
                                             transmission_factor=0,
                                             npoints=100)

#calculate the angle of incidence (aoi) - should be checked that aoi is working correct when we've a front and a back side
aoi_east = pvlib.irradiance.aoi(surface_tilt=tilt,
                           surface_azimuth=orientation,                              
                           solar_zenith=solar_position['apparent_zenith'],
                           solar_azimuth=solar_position['azimuth'])

#calculate the angle of incidence (aoi)
aoi_west = pvlib.irradiance.aoi(surface_tilt=180-tilt,
                           surface_azimuth=orientation+180,                              
                           solar_zenith=solar_position['apparent_zenith'],
                           solar_azimuth=solar_position['azimuth'])


iam_east = pvlib.iam.ashrae(aoi_east)
iam_west = pvlib.iam.ashrae(aoi_west)
iam_diffuse =pvlib.iam.marion_diffuse(model='ashrae', surface_tilt=tilt)


#Spectral loss - the module is only used for spectral losses - just needs to be the same type
sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod') 
module_sandia = sandia_modules['LG_LG290N1C_G3__2013_'] # module LG290N1C - mono crystalline si 
spec_loss_sandia=spectrum.mismatch.spectral_factor_sapm(airmass_absolute=am_abs, module=module_sandia)





#Fuel in - bifaciality not included - this can be compared with the ref cells
fuel_in_east_infinite_sheds = ((poa_infinite_sheds['poa_front_direct']*iam_east+poa_infinite_sheds['poa_front_ground_diffuse']*iam_diffuse['ground']+poa_infinite_sheds['poa_front_sky_diffuse']*iam_diffuse['sky']))*spec_loss_sandia
fuel_in_west_infinite_sheds = ((poa_infinite_sheds['poa_back_direct']*iam_west+poa_infinite_sheds['poa_back_ground_diffuse']*iam_diffuse['ground']+poa_infinite_sheds['poa_back_sky_diffuse']*iam_diffuse['sky']))*spec_loss_sandia



#%%% Plots

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 

start_date = '2023-06-10 00:00:00'
end_date = '2023-06-30 00:00:00'
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

    #FG changes - plot of ref cells
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    ax0.plot(fuel_in_east_infinite_sheds[time_index], 
              color='dodgerblue',
              label='Fuel_in east (W.m-2)')
    ax0.plot(data['Reference Cell Vertical East (W.m-2)'][time_index], 
              color='red',
              label='Reference Cell Vertical East (W.m-2)')
    ax0.plot(fuel_in_west_infinite_sheds[time_index], 
              color='orange',
              label='Fuel_in west (W.m-2)')
    ax0.plot(data['Reference Cell Vertical West (W.m-2)'][time_index], 
              color='green',
              label='Reference Cell Vertical West (W.m-2)')
    ax0.set_ylim([0,1000])
    ax0.set_ylabel('Irradiance (W.m-2)')
    plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
    ax0.grid('--')
    ax0.legend()
    plt.savefig('Figures/daily_profiles/modelled_ref_cells_{}_{}_{}.jpg'.format(day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                dpi=100, bbox_inches='tight')    
    
    

   



