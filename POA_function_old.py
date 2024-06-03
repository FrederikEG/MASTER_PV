# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 15:35:40 2024

@author: frede
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 13:04:39 2024

@author: frede
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 14:02:01 2024

@author: frede
"""

#In this scriped I try to make the calculation of POA into i function that can be called

def POA(PV_data,installation_data):
    
    """Calculates the fuel-in POA for the vertical installation in Foulum
    
    Parameters
    -------
    start_date :  Beginning of the calculation in the form '2023-4-10 00:00:00'   
    
    end_date :  End of the calculation in the form '2023-4-10 00:00:00'   


    Returns
    -------
    POA_fuel_in : DataFrame
        Output is a DataFrame with series of the East and West side in [W/m^2]  
    """

    import pvlib
    import pandas as pd
    from collections import OrderedDict
    from pvlib import spectrum


    module_width = 1.134

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

    
    #import data
    data=pd.read_csv('resources/clean_data.csv',
                     index_col=0)
    
    data.index = pd.to_datetime(data.index, utc=True) 
    
    
    GHI = pd.to_numeric(data[('GHI (W.m-2)')])
    GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')])
    DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
    DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
    Albedometer = pd.to_numeric(data[('Albedometer (W.m-2)')])
   # wind_speed = pd.to_numeric(data[('wind velocity (m.s-1)')])
   # temp_air = pd.to_numeric(data[('Ambient Temperature (Deg C)')])
    
    GHI = (GHI+GHI_SPN1)/2
    
    # calculate Sun's coordinates
    solar_position = location.get_solarposition(times=data.index) 
    
    #Calculate the dni from the weather station measurements 
    pressure = pvlib.atmosphere.alt2pres(altitude)
    
    #calculate airmass 
    airmass = pvlib.atmosphere.get_relative_airmass(solar_position['apparent_zenith'])
    pressure = pvlib.atmosphere.alt2pres(altitude)
    am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
    
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
    
    fuel_in = OrderedDict()
    fuel_in['POA fuel_in West'] = fuel_in_west_infinite_sheds
    fuel_in['POA fuel_in East'] = fuel_in_east_infinite_sheds

    POA_fuel_in = pd.DataFrame(fuel_in)
    
    return POA_fuel_in


