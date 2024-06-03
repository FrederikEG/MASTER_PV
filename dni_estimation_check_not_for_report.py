# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 11:54:02 2024

@author: frede
"""



import pvlib
import pandas as pd
from collections import OrderedDict
from pvlib import spectrum
from shadow import shadow
import numpy as np
from GHI_2nd_WS_correct import GHI_2nd_WS_correct

GHI_sensor = 'GHI'
DNI_model = 'dirindex'
model = 'isotropic'
model_perez = 'allsitescomposite1990'

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

module_width = PV_data['module_width']
module_height = PV_data['module_height']

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

GHI_CMP6 = pd.to_numeric(data[('GHI (W.m-2)')])
GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')])
GHI_2nd = pd.to_numeric(data[('GHI_2nd station (W.m-2)')])
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
Albedometer = pd.to_numeric(data[('Albedometer (W.m-2)')])

# wind_speed = pd.to_numeric(data[('wind velocity (m.s-1)')])
# temp_air = pd.to_numeric(data[('Ambient Temperature (Deg C)')])


#Selects the sensor to use for GHI
if GHI_sensor == 'GHI':
    GHI = GHI_CMP6
elif GHI_sensor == 'SPN1':
    GHI = GHI_SPN1
elif GHI_sensor == 'GHI_2nd':
    GHI = GHI_2nd
elif GHI_sensor == 'GHI_2nd_ws_correct':
    mag_factor = GHI_2nd_WS_correct(data)
    mag_factor.reindex(data.index)
    mag_factor.fillna(1)
    GHI_mag = GHI*mag_factor
    GHI = (GHI_CMP6 + GHI_mag)/2



#Takes the average of the albedo when the solar elevation is above 10 deg and uses that average for the whole day
albedo = Albedometer/GHI
albedo_fil = albedo[solar_position['elevation']>10]
albedo_daily_mid_day_mean = albedo_fil.resample('D').mean()
albedo_daily = albedo_daily_mid_day_mean.reindex(albedo.index, method='ffill')





#Calculate the dni from the weather station measurements 
pressure = pvlib.atmosphere.alt2pres(altitude)

#calculate airmass 
airmass = pvlib.atmosphere.get_relative_airmass(solar_position['apparent_zenith'])
pressure = pvlib.atmosphere.alt2pres(altitude)
am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)

# Extraterrestrial radiation 
dni_extra = pvlib.irradiance.get_extra_radiation(data.index,epoch_year=2023)
   

if DNI_model == 'dirint':
    # Simple model for DNI 
    dni_dirint = pvlib.irradiance.dirint(ghi=GHI,
                                  solar_zenith=solar_position['zenith'],
                                  times=data.index,
                                  pressure=pressure,
                                  use_delta_kt_prime=True,
                                  temp_dew=None,
                                  min_cos_zenith=0.065,
                                  max_zenith=87)
    dni = dni_dirint
    
elif DNI_model == 'dirindex':
        clearsky = location.get_clearsky(times=data.index,
                                         solar_position=solar_position)
       
        # Semi complex model for DNI 
        dni_dirindex = pvlib.irradiance.dirindex(ghi=GHI,
                                                 ghi_clearsky=clearsky['ghi'],
                                                 dni_clearsky=clearsky['dni'],
                                                 zenith=solar_position['zenith'],
                                                 times=data.index,
                                                 pressure=pressure)
        dni = dni_dirindex
        
elif DNI_model == 'dirindex_turbidity':
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
                                             use_delta_kt_prime = True)

    
    dni = dni_dirindex_turbidity       
        
elif DNI_model == 'simple':
    dni_simple = pvlib.irradiance.dni(GHI,
                                      DHI_SPN1,
                                      zenith = solar_position['apparent_zenith'])
    
    
    dni = dni_simple
    


   
albedo = Albedometer/GHI
albedo_fil = albedo[solar_position['elevation']>10]
albedo_daily_mid_day_mean = albedo_fil.resample('D').mean()
albedo_daily = albedo_daily_mid_day_mean.reindex(albedo.index, method='ffill')






poa_no_shadow_front = pvlib.irradiance.get_total_irradiance(surface_tilt = tilt, 
                                                  surface_azimuth = orientation, 
                                                  solar_zenith = solar_position['apparent_zenith'], 
                                                  solar_azimuth = solar_position['azimuth'], 
                                                  dni = dni,
                                                  dni_extra=dni_extra,
                                                  ghi = GHI, 
                                                  dhi = DHI_SPN1,
                                                  airmass = airmass,
                                                  albedo = albedo_daily,
                                                  model = model,
                                                  model_perez = model_perez)