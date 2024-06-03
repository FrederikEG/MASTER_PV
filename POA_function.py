# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 13:04:39 2024

@author: frede
"""
#In this scriped I try to make the calculation of POA into i function that can be called

def POA(PV_data,installation_data,tz,GHI_sensor, model, DNI_model, mount_type, spectral_mismatch_model,shadow_interpolate='false', temp_sensor = 'default', RH_sensor = 'default', iam_apply = True):
    
    """Calculates the fuel-in POA for the vertical installation in Foulum
    
    Parameters
    -------
    PV_data :  
        dict containing the data about the PV panels   
    
    installation_data :  
        dict containing the data for the installation 
        
    tz :  str.
        The time zone. Should be 'UTC'
        
    GHI_sensor : str.
        CMP6 sensor 'GHI'
        SPN1 sensor 'GHI_SPN1'
        
    model : str.
        Irradiance model - 'isotropic' or 'haydavies'.

    Returns
    -------
    POA_fuel_in : DataFrame
        Output is a DataFrame with series of the East and West side in [W/m^2]  
    """

    import pvlib
    import pandas as pd
    from collections import OrderedDict
    from pvlib import spectrum
    from shadow import shadow
    import numpy as np
    from GHI_2nd_WS_correct import GHI_2nd_WS_correct

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
    else:
    # Raise an error if no condition is met
        raise ValueError("No GHI sensor selected")
        
        

    #Takes the average of the albedo when the solar elevation is above 10 deg and uses that average for the whole day
    albedo = Albedometer/GHI
    albedo_fil = albedo[solar_position['elevation']>10]
    albedo_daily_mid_day_mean = albedo_fil.resample('D').mean()
    albedo_daily = albedo_daily_mid_day_mean.reindex(albedo.index, method='ffill')
    
    GHI = shadow_interpolate_function(shadow_interpolate= shadow_interpolate,
                                      data = data,
                                      GHI_sensor = GHI_sensor, 
                                      solar_position = solar_position)

    """
    #Interpolates GHI when the pyranometers are in the shadow
    if shadow_interpolate == 'true' and GHI_sensor == 'GHI':
        #identify when the pyranometers are bloked by shadow
        #uses direction for approximate interval and cap on albedo for exact location
        albedo_in_shadow = albedo_fil[(solar_position['azimuth']<255) & (solar_position['azimuth']>240)]
        albedo_high = albedo_in_shadow[albedo_in_shadow>0.3].index
        GHI_linear = linear_interpolate_at_drops(GHI, albedo_high)
        #s = GHI
        # Interpolate faulty measurements
        #for idx in albedo_high:
         #       s.loc[idx] = (s.loc[idx - pd.Timedelta(minutes=5)] + s.loc[idx + pd.Timedelta(minutes=5)]) / 2
          #      GHI = s
        GHI = GHI_linear  
        
    elif shadow_interpolate == 'true' and GHI_sensor == 'SPN1':
        #identify when the pyranometers are bloked by shadow
        #uses direction for approximate interval and cap on albedo for exact location
        albedo_in_shadow = albedo_fil[(solar_position['azimuth']<290) & (solar_position['azimuth']>270)]
        albedo_high = albedo_in_shadow[albedo_in_shadow>0.3].index
        start_date = albedo_high[0]-pd.Timedelta(minutes=5)
        end_date = albedo_high[-1]+pd.Timedelta(minutes=5)
        start_diff = GHI[start_date]-GHI_CMP6[start_date]
        GHI[start_date:end_date] = GHI_CMP6[start_date:end_date]
        #GHI_linear = linear_interpolate_at_drops(GHI, albedo_high)
        #s = GHI
        # Interpolate faulty measurements
        #for idx in albedo_high:
         #       s.loc[idx] = (s.loc[idx - pd.Timedelta(minutes=5)] + s.loc[idx + pd.Timedelta(minutes=5)]) / 2
          #      GHI = s
        #GHI = GHI_linear
    
    #elif shadow_interpolate == 'false':
     #   GHI = GHI
   """
   
   
    """
    #Interpolates GHI when the pyranometers are in the shadow
    if shadow_interpolate == 'true' and GHI_sensor == 'GHI':
        #identify when the pyranometers are bloked by shadow
        #uses direction for approximate interval and cap on albedo for exact location
        albedo_in_shadow = albedo_fil[(solar_position['azimuth']<255) & (solar_position['azimuth']>240)]
        albedo_high = albedo_in_shadow[albedo_in_shadow>0.3].index
        GHI_linear = linear_interpolate_at_drops(GHI, albedo_high)
       # s = GHI
        # Interpolate faulty measurements
        #for idx in albedo_high:
         #       s.loc[idx] = (s.loc[idx - pd.Timedelta(minutes=5)] + s.loc[idx + pd.Timedelta(minutes=5)]) / 2
          #      GHI = s
        GHI = GHI_linear
    elif shadow_interpolate == 'true' and GHI_sensor == 'SPN1':
    #identify when the pyranometers are bloked by shadow
        #uses direction for approximate interval and cap on albedo for exact location
        albedo_in_shadow = albedo_fil[(solar_position['azimuth']<290) & (solar_position['azimuth']>270)]
        albedo_high = albedo_in_shadow[albedo_in_shadow>0.3].index
        start_date = albedo_high[0]-pd.Timedelta(minutes=5)
        end_date = albedo_high[-1]+pd.Timedelta(minutes=5)
        inter_range = pd.date_range(start_date, end_date, freq='5T', tz='UTC')
        start_diff = GHI_SPN1[start_date]-GHI_CMP6[start_date]
                
        # Example DateTimeIndex (UTC timezone for consistency with previous steps)
        original_index = albedo_high
        
        # Find unique days in the DateTimeIndex
        unique_days = original_index.normalize().unique()
        
        # Initialize a list to hold all datetime objects, including additional timesteps
        extended_index_list = []
        
        # Time delta of 1 timestep (assuming 1H as a timestep; adjust as needed)
        time_step = pd.Timedelta(minutes=5)
        
        # Iterate through each unique day to find the first timestep and add two before it
        for day in unique_days:
            # Extract the first timestep of the day
            first_time_step_of_day = original_index[original_index.normalize() == day][0]
            
            # Generate two timesteps before the first timestep
            timestep_minus_1 = first_time_step_of_day - time_step
            timestep_minus_2 = first_time_step_of_day - 2 * time_step
            
            # Append the new timesteps to the list
            extended_index_list.extend([timestep_minus_2, timestep_minus_1])
        
        # Combine the original and new timesteps and remove duplicates
        extended_index_list.extend(original_index)
        extended_datetime_index = pd.DatetimeIndex(list(set(extended_index_list)))
        
        # Sort the combined index to maintain chronological order
        extended_datetime_index = extended_datetime_index.sort_values()
        
     
        s=GHI_SPN1
        for idx in extended_datetime_index:
                #s.loc[idx] = (s.loc[idx - pd.Timedelta(minutes=5)] + s.loc[idx + pd.Timedelta(minutes=5)]) / 2
                #s.loc[idx] = s.loc[idx-pd.Timedelta(minutes=5)] + ((s.loc[idx + pd.Timedelta(minutes=15)] - s.loc[idx + pd.Timedelta(minutes=5)]) /4 ) * 1
                s.loc[idx] = GHI_CMP6[idx] + start_diff
                GHI = s
                
        #GHI = GHI_linear
    
    elif shadow_interpolate == 'false':
        GHI = GHI
   """
   
    
    
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
                                                 use_delta_kt_prime=True)
    
        
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
    
    #%%% Using infinite sheds 
    #height_mid = 2*module_width #height of center point
    
    if mount_type == 'Vertical':
        height_mid = 3*module_width/2 #height of center point
        height_top = installation_data['height']
    elif mount_type == 'Tilted':
        tilt_rad = np.deg2rad(tilt)
        height_mid = ((module_height/2)*np.sin(tilt_rad))+module_width  #height of center point
        height_top = installation_data['height'] # needs update
        
    #elevation_min = np.arctan(height_mid/installation_data['pitch'])
    elevation_min = np.arctan(height_top/installation_data['pitch'])
    
    elevation_min = np.rad2deg(elevation_min)
    
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
                                                 model = model,
                                                 dni_extra= dni_extra,
                                                 iam_front=1.0,
                                                 iam_back=1.0,
                                                 bifaciality=1,
                                                 shade_factor= 0,
                                                 transmission_factor=0,
                                                 npoints=100)
    
    
    #This sums the different contributions since the summed results from
    #infinite sheds sometimes leaves the diffuse contribution out 
    poa_front = poa_infinite_sheds['poa_front_direct'] + poa_infinite_sheds['poa_front_diffuse'] + poa_infinite_sheds['poa_front_ground_diffuse'] + poa_infinite_sheds['poa_front_sky_diffuse']
    poa_back = poa_infinite_sheds['poa_back_direct'] + poa_infinite_sheds['poa_back_diffuse'] + poa_infinite_sheds['poa_back_ground_diffuse'] + poa_infinite_sheds['poa_back_sky_diffuse']  
    poa_global = poa_front + poa_back
    
    """
    # calculate irradiante at the plane of the array (poa)
    poa_front = pvlib.irradiance.get_total_irradiance(surface_tilt=tilt,
                                                           surface_azimuth=orientation,
                                                           dni= dni,
                                                           ghi=GHI,
                                                           dhi=DHI_SPN1,
                                                           solar_zenith=solar_position['apparent_zenith'],
                                                           solar_azimuth=solar_position['azimuth'],
                                                           albedo=albedo_daily)
    """
    #Correct for nan in direct measurements - this should be 0 for the function to work
    #poa_infinite_sheds['poa_front_direct'] = poa_infinite_sheds['poa_front_direct'].fillna(0)
    
    #poa_front['poa_direct'] = poa_front['poa_direct'].fillna(0)
    
    
    
    
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
    
    #Spectral loss - the module is only used for spectral losses - just needs to be the same type
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod') 
    module_sandia = sandia_modules['LG_LG290N1C_G3__2013_'] # module LG290N1C - mono crystalline si 
    spec_loss_sandia = spectrum.mismatch.spectral_factor_sapm(airmass_absolute=am_abs, module=module_sandia)
    
    
    # The incidence angle modifiers 
    if iam_apply == 'ashrae':
        iam_east = pvlib.iam.ashrae(aoi_east)
        iam_west = pvlib.iam.ashrae(aoi_west)
        iam_diffuse_front =pvlib.iam.marion_diffuse(model='ashrae', surface_tilt=tilt)
        iam_diffuse_back =pvlib.iam.marion_diffuse(model='ashrae', surface_tilt=180-tilt)
    elif iam_apply == 'SAPM':
        iam_east = pvlib.iam.sapm(aoi_east, module = module_sandia)
        iam_west = pvlib.iam.sapm(aoi_west, module = module_sandia)
        iam_diffuse_front =pvlib.iam.marion_diffuse(model='sapm', module = module_sandia, surface_tilt=tilt)
        iam_diffuse_back =pvlib.iam.marion_diffuse(model='sapm', module = module_sandia, surface_tilt=180-tilt)
    elif iam_apply == False:
        iam_east = 1
        iam_west = 1
        iam_diffuse_front = {'sky':1,'ground':1, 'horizon':1}
        iam_diffuse_back = {'sky':1,'ground':1, 'horizon':1}
    

  
#%%%    Apply different spectral loss model


     #Transforming the hourly measurements from 2nd weather station to 5 min interval
    temp_2nd = data['Ambient Temperature_2nd station (Deg C)']
    temp_2nd = temp_2nd.loc['2023-01-01 00:00:00+00:00' : '2023-12-31 23:55:00+00:00']
    temp_2nd = temp_2nd.dropna()
    temp_2nd = temp_2nd.asfreq('5T', method='ffill')
    
    
    # Selcting the sensor that's available
    temp_WS = data['Ambient Temperature (Deg C)']
    temp_2nd_WS = temp_2nd.reindex(temp_WS.index, fill_value = 'nan')
    selected_values = np.where(pd.notna(temp_WS), temp_WS, temp_2nd_WS)
    

    # Create a new Series from the selected values
    temp_sensor_select = pd.Series(selected_values, index=temp_WS.index, dtype=float)
    
    #Selecting the temperature sensor
    if temp_sensor == 'default':
        temp_air = temp_sensor_select
    elif temp_sensor == 'weather_station':
        temp_air = data['Ambient Temperature (Deg C)']
    elif temp_sensor == '2nd weather_station'    :
        temp_air = temp_2nd
    
    
    

    
     #Transforming the hourly measurements from 2nd weather station to 5 min interval
    RH_2nd = data_2nd['Relative humidity (%)']
    RH_2nd = RH_2nd.loc['2023-01-01 00:00:00+00:00' : '2023-12-31 23:55:00+00:00']
    RH_2nd = RH_2nd.dropna()
    RH_2nd = RH_2nd.asfreq('5T', method='ffill')
    
    
    # Selcting the sensor that's available
    RH_WS = data['Relative Humidity (%)']
    RH_2nd_WS = RH_2nd.reindex(RH_WS.index, fill_value = 'nan')
    selected_values = np.where(pd.notna(RH_WS), RH_WS, RH_2nd_WS)
    

    # Create a new Series from the selected values
    RH_sensor_select = pd.Series(selected_values, index=RH_WS.index, dtype=float)
    
    #Selecting the humidity sensor
    if RH_sensor == 'default':
        relative_humidity = RH_sensor_select
    elif RH_sensor == 'weather_station':
        relative_humidity = data['Relative Humidity (%)']
    elif RH_sensor == '2nd weather_station'    :
        relative_humidity = RH_2nd
        
    #Overruling the selection of sensor - why?
    #rel_humididy_WS = pd.to_numeric(data['Relative Humidity (%)']) 
    #relative_humidity = rel_humididy_WS 
    
    
    precipitable_water = pvlib.atmosphere.gueymard94_pw(temp_air, relative_humidity)
    spec_loss_Gueymard = spectrum.mismatch.spectral_factor_firstsolar(precipitable_water, 
                                                                      airmass_absolute = am_abs,
                                                                      module_type= PV_data['celltype'])

    if spectral_mismatch_model == 'Sandia':
        spec_loss = spec_loss_sandia
    elif spectral_mismatch_model == 'Gueymard':
        spec_loss = spec_loss_Gueymard
    elif spectral_mismatch_model == None:
        spec_loss = pd.Series(1, index=data.index)
    
  

#%%%
    #Fuel in - bifaciality not included - this can be compared with the ref cells
    fuel_in_east_infinite_sheds = ((poa_infinite_sheds['poa_front_direct']*iam_east+poa_infinite_sheds['poa_front_ground_diffuse']*iam_diffuse_front['ground']+poa_infinite_sheds['poa_front_sky_diffuse']*iam_diffuse_front['sky']))*spec_loss
    fuel_in_west_infinite_sheds = ((poa_infinite_sheds['poa_back_direct']*iam_west+poa_infinite_sheds['poa_back_ground_diffuse']*iam_diffuse_back['ground']+poa_infinite_sheds['poa_back_sky_diffuse']*iam_diffuse_back['sky']))*spec_loss
    
    
    #Shadow and bifaciality adjusted 
    #eta_shadow,L_horizontal, L_vertical = shadow(PV_data, installation_data, tz, data)
    shadow_dict = shadow(PV_data, installation_data, tz, data)
    eta_shadow = shadow_dict['eta_shadow']
    fuel_in_east_shadow = (((poa_infinite_sheds['poa_front_direct']*eta_shadow*iam_east+poa_infinite_sheds['poa_front_ground_diffuse']*iam_diffuse_front['ground']+poa_infinite_sheds['poa_front_sky_diffuse']*iam_diffuse_front['sky']))*spec_loss)
    fuel_in_west_shadow = ((poa_infinite_sheds['poa_back_direct']*iam_west+poa_infinite_sheds['poa_back_ground_diffuse']*iam_diffuse_back['ground']+poa_infinite_sheds['poa_back_sky_diffuse']*iam_diffuse_back['sky']))*spec_loss
    poa_front_shadow = poa_infinite_sheds['poa_front_direct']*eta_shadow + poa_infinite_sheds['poa_front_diffuse'] + poa_infinite_sheds['poa_front_ground_diffuse'] + poa_infinite_sheds['poa_front_sky_diffuse']
    poa_back_shadow = poa_infinite_sheds['poa_back_direct'] + poa_infinite_sheds['poa_back_diffuse'] + poa_infinite_sheds['poa_back_ground_diffuse'] + poa_infinite_sheds['poa_back_sky_diffuse']  
    poa_global_shadow = poa_front_shadow + poa_back_shadow
    
    
    
    POA_dict = OrderedDict()
    POA_dict['POA fuel_in West'] = fuel_in_west_infinite_sheds
    POA_dict['POA fuel_in East'] = fuel_in_east_infinite_sheds
    POA_dict['POA front'] = poa_front
    POA_dict['POA back'] = poa_back
    POA_dict['POA Global'] = poa_global
    POA_dict['POA front_shadow'] = poa_front_shadow
    POA_dict['POA back_shadow'] = poa_back_shadow
    POA_dict['POA Global_shadow'] = poa_global_shadow
    POA_dict['POA fuel_in shadow East'] = fuel_in_east_shadow
    POA_dict['POA fuel_in shadow West'] = fuel_in_west_shadow

    POA = pd.DataFrame(POA_dict)
    
    
    return POA, solar_position, albedo, GHI, aoi_west, aoi_east, spec_loss, poa_infinite_sheds, albedo_daily, dni, elevation_min














##########################################################

# Here the POA is calculated in the simple way where shadows are ignored

def POA_simple(PV_data,installation_data,tz,GHI_sensor, model, mount_type, spectral_mismatch_model, DNI_model,shadow_interpolate='false', temp_sensor = 'default', RH_sensor = 'default', model_perez = 'allsitescomposite1990', iam_apply = True):
    
    """Calculates the fuel-in POA for the vertical installation in Foulum. 
    shadows from the neigboring rows are neglected. 
    
    Parameters
    -------
    PV_data :  
        dict containing the data about the PV panels   
    
    installation_data :  
        dict containing the data for the installation 
        
    tz :  str.
        The time zone. Should be 'UTC'
        
    GHI_sensor : str.
        CMP6 sensor 'GHI'
        SPN1 sensor 'GHI_SPN1'
        
    model : str.
        Irradiance model - 'isotropic' or 'haydavies'.

    Returns
    -------
    POA_fuel_in : DataFrame
        Output is a DataFrame with series of the East and West side in [W/m^2]  
    """

    import pvlib
    import pandas as pd
    from collections import OrderedDict
    from pvlib import spectrum
    from shadow import shadow
    import numpy as np
    from GHI_2nd_WS_correct import GHI_2nd_WS_correct

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
    
    GHI = shadow_interpolate_function(shadow_interpolate= shadow_interpolate,data = data ,GHI_sensor = GHI_sensor , solar_position = solar_position)

    """
    #Interpolates GHI when the pyranometers are in the shadow
    if shadow_interpolate == 'true' and GHI_sensor == 'GHI':
        #identify when the pyranometers are bloked by shadow
        #uses direction for approximate interval and cap on albedo for exact location
        albedo_in_shadow = albedo_fil[(solar_position['azimuth']<255) & (solar_position['azimuth']>240)]
        albedo_high = albedo_in_shadow[albedo_in_shadow>0.3].index
        GHI_linear = linear_interpolate_at_drops(GHI, albedo_high)
       # s = GHI
        # Interpolate faulty measurements
        #for idx in albedo_high:
         #       s.loc[idx] = (s.loc[idx - pd.Timedelta(minutes=5)] + s.loc[idx + pd.Timedelta(minutes=5)]) / 2
          #      GHI = s
        GHI = GHI_linear
    elif shadow_interpolate == 'true' and GHI_sensor == 'SPN1':
    #identify when the pyranometers are bloked by shadow
        #uses direction for approximate interval and cap on albedo for exact location
        albedo_in_shadow = albedo_fil[(solar_position['azimuth']<290) & (solar_position['azimuth']>270)]
        albedo_high = albedo_in_shadow[albedo_in_shadow>0.3].index
        start_date = albedo_high[0]-pd.Timedelta(minutes=5)
        end_date = albedo_high[-1]+pd.Timedelta(minutes=5)
        inter_range = pd.date_range(start_date, end_date, freq='5T', tz='UTC')
        start_diff = GHI_SPN1[start_date]-GHI_CMP6[start_date]
                
        # Example DateTimeIndex (UTC timezone for consistency with previous steps)
        original_index = albedo_high
        
        # Find unique days in the DateTimeIndex
        unique_days = original_index.normalize().unique()
        
        # Initialize a list to hold all datetime objects, including additional timesteps
        extended_index_list = []
        
        # Time delta of 1 timestep (assuming 1H as a timestep; adjust as needed)
        time_step = pd.Timedelta(minutes=5)
        
        # Iterate through each unique day to find the first timestep and add two before it
        for day in unique_days:
            # Extract the first timestep of the day
            first_time_step_of_day = original_index[original_index.normalize() == day][0]
            
            # Generate two timesteps before the first timestep
            timestep_minus_1 = first_time_step_of_day - time_step
            timestep_minus_2 = first_time_step_of_day - 2 * time_step
            
            # Append the new timesteps to the list
            extended_index_list.extend([timestep_minus_2, timestep_minus_1])
        
        # Combine the original and new timesteps and remove duplicates
        extended_index_list.extend(original_index)
        extended_datetime_index = pd.DatetimeIndex(list(set(extended_index_list)))
        
        # Sort the combined index to maintain chronological order
        extended_datetime_index = extended_datetime_index.sort_values()
        
     
        s=GHI_SPN1
        for idx in extended_datetime_index:
                #s.loc[idx] = (s.loc[idx - pd.Timedelta(minutes=5)] + s.loc[idx + pd.Timedelta(minutes=5)]) / 2
                #s.loc[idx] = s.loc[idx-pd.Timedelta(minutes=5)] + ((s.loc[idx + pd.Timedelta(minutes=15)] - s.loc[idx + pd.Timedelta(minutes=5)]) /4 ) * 1
                s.loc[idx] = GHI_CMP6[idx] + start_diff
                GHI = s
        #GHI = GHI_linear
    
    elif shadow_interpolate == 'false':
        GHI = GHI
   
   """


#%%%  DNI calculations
   
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
    

#%%%    

    if mount_type == 'Vertical':
        height_mid = 3*module_width/2 #height of center point
        height_top = installation_data['height']
    elif mount_type == 'Tilted':
        tilt_rad = np.deg2rad(tilt)
        height_mid = ((module_height/2)*np.sin(tilt_rad))+module_width  #height of center point
        height_top = installation_data['height'] # needs update
        
    #elevation_min = np.arctan(height_mid/installation_data['pitch'])
    elevation_min = np.arctan(height_top/installation_data['pitch'])
    
    elevation_min = np.rad2deg(elevation_min)







    poa_no_shadow_east = pvlib.irradiance.get_total_irradiance(surface_tilt = tilt, 
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
    
    poa_no_shadow_west = pvlib.irradiance.get_total_irradiance(surface_tilt = 180 - tilt, 
                                                          surface_azimuth = orientation + 180, 
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
    
    
    poa_no_shadow_east_copy = poa_no_shadow_east.copy()
    poa_no_shadow_west_copy = poa_no_shadow_west.copy()
    poa_no_shadow_east_copy.columns = ['east_' + col for col in poa_no_shadow_east_copy.columns]
    poa_no_shadow_west_copy.columns = ['west_' + col for col in poa_no_shadow_west_copy.columns]
    poa_no_shadow_both = pd.concat([poa_no_shadow_east_copy, poa_no_shadow_west_copy], axis=1)
    
    #This sums the different contributions since the summed results from
    #infinite sheds sometimes leaves the diffuse contribution out 
    poa_east = poa_no_shadow_east['poa_direct'] + poa_no_shadow_east['poa_diffuse'] + poa_no_shadow_east['poa_sky_diffuse'] + poa_no_shadow_east['poa_ground_diffuse']
    poa_west = poa_no_shadow_west['poa_direct'] + poa_no_shadow_west['poa_diffuse'] + poa_no_shadow_west['poa_sky_diffuse'] + poa_no_shadow_west['poa_ground_diffuse']
    poa_global = poa_east + poa_west
    #Correct for nan in direct measurements - this should be 0 for the function to work
    #poa_infinite_sheds['poa_front_direct'] = poa_infinite_sheds['poa_front_direct'].fillna(0)
    
    #poa_front['poa_direct'] = poa_front['poa_direct'].fillna(0)
    
    
    
    
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
    
    #Spectral loss - the module is only used for spectral losses - just needs to be the same type
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod') 
    module_sandia = sandia_modules['LG_LG290N1C_G3__2013_'] # module LG290N1C - mono crystalline si 
    spec_loss_sandia = spectrum.mismatch.spectral_factor_sapm(airmass_absolute=am_abs, module=module_sandia)
    
    
    # Select the IAM 
    if iam_apply == 'ashrae':
        iam_east = pvlib.iam.ashrae(aoi_east)
        iam_west = pvlib.iam.ashrae(aoi_west)
        iam_diffuse_front =pvlib.iam.marion_diffuse(model='ashrae', surface_tilt=tilt)
        iam_diffuse_back =pvlib.iam.marion_diffuse(model='ashrae', surface_tilt=180-tilt)
    elif iam_apply == 'SAPM':
        iam_east = pvlib.iam.sapm(aoi_east, module = module_sandia)
        iam_west = pvlib.iam.sapm(aoi_west, module = module_sandia)
        iam_diffuse_front =pvlib.iam.marion_diffuse(model='sapm', module = module_sandia, surface_tilt=tilt)
        iam_diffuse_back =pvlib.iam.marion_diffuse(model='sapm', module = module_sandia, surface_tilt=180-tilt)  
    elif iam_apply == False:
        iam_east = 1
        iam_west = 1
        iam_diffuse_front = {'sky':1,'ground':1, 'horizon':1}
        iam_diffuse_back = {'sky':1,'ground':1, 'horizon':1}

    

  
#%%%    Apply different spectral loss model


     #Transforming the hourly measurements from 2nd weather station to 5 min interval
    temp_2nd = data['Ambient Temperature_2nd station (Deg C)']
    temp_2nd = temp_2nd.loc['2023-01-01 00:00:00+00:00' : '2023-12-31 23:55:00+00:00']
    temp_2nd = temp_2nd.dropna()
    temp_2nd = temp_2nd.asfreq('5T', method='ffill')
    
    
    # Selcting the sensor that's available
    temp_WS = data['Ambient Temperature (Deg C)']
    temp_2nd_WS = temp_2nd.reindex(temp_WS.index, fill_value = 'nan')
    selected_values = np.where(pd.notna(temp_WS), temp_WS, temp_2nd_WS)
    

    # Create a new Series from the selected values
    temp_sensor_select = pd.Series(selected_values, index=temp_WS.index, dtype=float)
    
    #Selecting the temperature sensor
    if temp_sensor == 'default':
        temp_air = temp_sensor_select
    elif temp_sensor == 'weather_station':
        temp_air = data['Ambient Temperature (Deg C)']
    elif temp_sensor == '2nd weather_station'    :
        temp_air = temp_2nd
    
    
     #Transforming the hourly measurements from 2nd weather station to 5 min interval
    RH_2nd = data_2nd['Relative humidity (%)']
    RH_2nd = RH_2nd.loc['2023-01-01 00:00:00+00:00' : '2023-12-31 23:55:00+00:00']
    RH_2nd = RH_2nd.dropna()
    RH_2nd = RH_2nd.asfreq('5T', method='ffill')
    
    
    # Selcting the sensor that's available
    RH_WS = data['Relative Humidity (%)']
    RH_2nd_WS = RH_2nd.reindex(RH_WS.index, fill_value = 'nan')
    selected_values = np.where(pd.notna(RH_WS), RH_WS, RH_2nd_WS)
    

    # Create a new Series from the selected values
    RH_sensor_select = pd.Series(selected_values, index=RH_WS.index, dtype=float)
    
    #Selecting the humidity sensor
    if RH_sensor == 'default':
        relative_humidity = RH_sensor_select
    elif RH_sensor == 'weather_station':
        relative_humidity = data['Relative Humidity (%)']
    elif RH_sensor == '2nd weather_station'    :
        relative_humidity = RH_2nd
        
    #overruling the selection of humidity sensor - why?
    #rel_humididy_WS = pd.to_numeric(data['Relative Humidity (%)']) 
    #relative_humidity = rel_humididy_WS 
    
    
    precipitable_water = pvlib.atmosphere.gueymard94_pw(temp_air, relative_humidity)
    spec_loss_Gueymard = spectrum.mismatch.spectral_factor_firstsolar(precipitable_water, 
                                                                      airmass_absolute = am_abs,
                                                                      module_type= PV_data['celltype'])

    if spectral_mismatch_model == 'Sandia':
        spec_loss = spec_loss_sandia
    elif spectral_mismatch_model == 'Gueymard':
        spec_loss = spec_loss_Gueymard
    elif spectral_mismatch_model == None:
        spec_loss = pd.Series(1, index=data.index)
    
  

#%%%
    
    #Fuel in - bifaciality not included - this can be compared with the ref cells
    fuel_in_east_no_shadow = ((poa_no_shadow_east['poa_direct']*iam_east+poa_no_shadow_east['poa_ground_diffuse']*iam_diffuse_front['ground']+poa_no_shadow_east['poa_sky_diffuse']*iam_diffuse_front['sky']))*spec_loss
    fuel_in_west_no_shadow = ((poa_no_shadow_west['poa_direct']*iam_west+poa_no_shadow_west['poa_ground_diffuse']*iam_diffuse_back['ground']+poa_no_shadow_west['poa_sky_diffuse']*iam_diffuse_back['sky']))*spec_loss
    
    
    #Shadow and bifaciality adjusted 
    #eta_shadow,L_horizontal, L_vertical = shadow(PV_data, installation_data, tz, data)
    shadow_dict = shadow(PV_data, installation_data, tz, data)
    eta_shadow = shadow_dict['eta_shadow']
    fuel_in_east_shadow = (((poa_no_shadow_east['poa_direct']*eta_shadow*iam_east+poa_no_shadow_east['poa_ground_diffuse']*iam_diffuse_front['ground']+poa_no_shadow_east['poa_sky_diffuse']*iam_diffuse_front['sky']))*spec_loss)
    fuel_in_west_shadow = ((poa_no_shadow_west['poa_direct']*iam_west+poa_no_shadow_west['poa_ground_diffuse']*iam_diffuse_back['ground']+poa_no_shadow_west['poa_sky_diffuse']*iam_diffuse_back['sky']))*spec_loss
    poa_front_shadow = poa_no_shadow_east['poa_direct']*eta_shadow + poa_no_shadow_east['poa_diffuse'] + poa_no_shadow_east['poa_ground_diffuse'] + poa_no_shadow_east['poa_sky_diffuse']
    poa_back_shadow = poa_no_shadow_west['poa_direct'] + poa_no_shadow_west['poa_diffuse'] + poa_no_shadow_west['poa_ground_diffuse'] + poa_no_shadow_west['poa_sky_diffuse']  
    poa_global_shadow = poa_front_shadow + poa_back_shadow
    
    
    
    POA_simple_dict = OrderedDict()
    POA_simple_dict['POA fuel_in West'] = fuel_in_west_no_shadow
    POA_simple_dict['POA fuel_in East'] = fuel_in_east_no_shadow
    POA_simple_dict['POA front'] = poa_east
    POA_simple_dict['POA back'] = poa_west
    POA_simple_dict['POA Global'] = poa_global
    POA_simple_dict['POA front_shadow'] = poa_front_shadow
    POA_simple_dict['POA back_shadow'] = poa_back_shadow
    POA_simple_dict['POA Global_shadow'] = poa_global_shadow
    POA_simple_dict['POA fuel_in shadow East'] = fuel_in_east_shadow
    POA_simple_dict['POA fuel_in shadow West'] = fuel_in_west_shadow

    POA_simple = pd.DataFrame(POA_simple_dict)
    
    
    
    
    return POA_simple, poa_no_shadow_east, poa_no_shadow_west, poa_no_shadow_both, GHI, dni, solar_position, elevation_min


#%%% Defining the interpolation function that is used to correct the GHI 
# measurements for the sudden drops due to shadow from the lightning rod

def shadow_interpolate_function(shadow_interpolate, data, GHI_sensor, solar_position):
    import pandas as pd
    GHI_CMP6 = pd.to_numeric(data[('GHI (W.m-2)')])
    GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')])
    GHI_2nd = pd.to_numeric(data[('GHI_2nd station (W.m-2)')])
    DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
    DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
    Albedometer = pd.to_numeric(data[('Albedometer (W.m-2)')])
    
    #Selects the sensor to use for GHI
    if GHI_sensor == 'GHI':
        GHI = GHI_CMP6
    elif GHI_sensor == 'SPN1':
        GHI = GHI_SPN1

    
    albedo = Albedometer/GHI
    #Interpolates GHI when the pyranometers are in the shadow
    if shadow_interpolate == 'true' and GHI_sensor == 'GHI':
        #identify when the pyranometers are bloked by shadow
        #uses direction for approximate interval and cap on albedo for exact location
        albedo_in_shadow = albedo[(solar_position['azimuth']<255) & (solar_position['azimuth']>240)]
        albedo_high = albedo_in_shadow[albedo_in_shadow>0.3].index
        GHI_linear = linear_interpolate_at_drops(GHI, albedo_high)
       # s = GHI
        # Interpolate faulty measurements
        #for idx in albedo_high:
         #       s.loc[idx] = (s.loc[idx - pd.Timedelta(minutes=5)] + s.loc[idx + pd.Timedelta(minutes=5)]) / 2
          #      GHI = s
        GHI = GHI_linear
    elif shadow_interpolate == 'true' and GHI_sensor == 'SPN1':
    #identify when the pyranometers are bloked by shadow
        #uses direction for approximate interval and cap on albedo for exact location
        albedo_in_shadow = albedo[(solar_position['azimuth']<290) & (solar_position['azimuth']>270)]
        albedo_high = albedo_in_shadow[albedo_in_shadow>0.3].index
        start_date = albedo_high[0]-pd.Timedelta(minutes=5)
        end_date = albedo_high[-1]+pd.Timedelta(minutes=5)
        inter_range = pd.date_range(start_date, end_date, freq='5T', tz='UTC')
        start_diff = GHI_SPN1[start_date]-GHI_CMP6[start_date]
                
        # Example DateTimeIndex (UTC timezone for consistency with previous steps)
        original_index = albedo_high
        
        # Find unique days in the DateTimeIndex
        unique_days = original_index.normalize().unique()
        
        # Initialize a list to hold all datetime objects, including additional timesteps
        extended_index_list = []
        
        # Time delta of 1 timestep (assuming 1H as a timestep; adjust as needed)
        time_step = pd.Timedelta(minutes=5)
        
        # Iterate through each unique day to find the first timestep and add two before it
        for day in unique_days:
            # Extract the first timestep of the day
            first_time_step_of_day = original_index[original_index.normalize() == day][0]
            
            # Generate two timesteps before the first timestep
            timestep_minus_1 = first_time_step_of_day - time_step
            timestep_minus_2 = first_time_step_of_day - 2 * time_step
            
            # Append the new timesteps to the list
            extended_index_list.extend([timestep_minus_2, timestep_minus_1])
        
        # Combine the original and new timesteps and remove duplicates
        extended_index_list.extend(original_index)
        extended_datetime_index = pd.DatetimeIndex(list(set(extended_index_list)))
        
        # Sort the combined index to maintain chronological order
        extended_datetime_index = extended_datetime_index.sort_values()
        
     
        s=GHI_SPN1
        for idx in extended_datetime_index:
                #s.loc[idx] = (s.loc[idx - pd.Timedelta(minutes=5)] + s.loc[idx + pd.Timedelta(minutes=5)]) / 2
                #s.loc[idx] = s.loc[idx-pd.Timedelta(minutes=5)] + ((s.loc[idx + pd.Timedelta(minutes=15)] - s.loc[idx + pd.Timedelta(minutes=5)]) /4 ) * 1
                s.loc[idx] = GHI_CMP6[idx] + start_diff
                GHI = s
        #GHI = GHI_linear
    
    elif shadow_interpolate == 'false':
        GHI = GHI

    return GHI










#%%%  Need to check - just chatGPT

# Example setup (make sure your df is similar)
# df = pd.DataFrame({
#     'value': [1, 2, 3, 4, None, None, None, 8, 9, 10]
# }, index=pd.date_range(start='2024-01-01', periods=10, freq='D'))

# albedo_high = pd.date_range(start='2024-01-05', periods=3, freq='D')


def linear_interpolate_at_drops(series, albedo_high):
    # Iterate through each drop date
    for drop_date in albedo_high:
        if drop_date in series.index:
            # Get the position of the drop date in the series
            idx_pos = series.index.get_loc(drop_date)
            
            # Find the indices just before and after the drop
            before_drop_idx = idx_pos - 1 if idx_pos > 0 else None
            after_drop_idx = idx_pos + 1
            
            # Find the index after the drop, considering consecutive drop dates
            while after_drop_idx < len(series) and series.index[after_drop_idx] in albedo_high:
                after_drop_idx += 1
            
            # Skip if we're at the bounds or if the next valid point is out of the series range
            if before_drop_idx is None or after_drop_idx >= len(series):
                continue
            
            # Extract the timestamps (as numerical values) and the corresponding values for interpolation
            x0 = series.index[before_drop_idx].value
            x1 = series.index[after_drop_idx].value
            y0 = series.iloc[before_drop_idx]
            y1 = series.iloc[after_drop_idx]
            
            # Calculate the interpolation for missing values
            for i in range(before_drop_idx + 1, after_drop_idx):
                xi = series.index[i].value
                yi = y0 + (xi - x0) * (y1 - y0) / (x1 - x0)
                series.iloc[i] = yi
                
    return series

# Note: Make sure your 'df' and 'albedo_high' variables are correctly set before running this.
# df_interpolated = linear_interpolate_at_drops(df, albedo_high)







    



