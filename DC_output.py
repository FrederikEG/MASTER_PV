# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 11:50:54 2024

@author: frede
"""

def DC_generation(POA,PV_data, installation_data, temp_sensor,shadow):
    
    """Calculates the generated DC from POA irradiance
    
    Parameters
    -------
    POA : 
        DataFrame with the "fuel-in POA" for East and West side, East side is assumed to be the back side of the panel.
            
    
    PV_data :  
        dict containing the data about the PV panels   

    
    Installation_data :  
        dict containing the data for the installation  

    Returns
    -------
    DC_output : 
        Output is a series with the generated DC  
    """
    
    import pvlib
    import pandas as pd
    import numpy as np
    from pvlib.pvsystem import PVSystem
    from collections import OrderedDict
    
    #import data
    data=pd.read_csv('resources/clean_data.csv',
                     index_col=0)
    
    data.index = pd.to_datetime(data.index, utc=True) 
    
    
    #Include shadow from structure or not
    if shadow =='False':
        eff_irrad_West = POA['POA fuel_in West']
        eff_irrad_East = POA['POA fuel_in East']*PV_data['bifaciality']
        eff_irrad_total = eff_irrad_West + eff_irrad_East
        POA_global = POA['POA Global']
    elif shadow =='True':
        eff_irrad_West = POA['POA fuel_in shadow West']
        eff_irrad_East = POA['POA fuel_in shadow East']*PV_data['bifaciality']
        eff_irrad_total = eff_irrad_West + eff_irrad_East
        POA_global = POA['POA Global_shadow']
        
    
    
    # Wind speed from sensor
    wind_speed = data['wind velocity (m.s-1)']
    
    #Wind speed equation from www.wind-data.ch
    #Estimation of the wind speed in 10 meter from the measurement in 2 meter 

    h_2 = 10 #height where the wind speed is needed for temperature calculations with sandia
    h_1 = 2 #height of the anemomenter at the weather station 
    z_0 = 0.03 #roughness height
    wind_10 = wind_speed*(np.log(h_2/z_0)/np.log(h_1/z_0))
    wind_speed = wind_10
    
    
    
    
    alpha_sc = PV_data['alpha_sc']
    
    
    #Transforming the hourly measurements from 2nd weather station to 5 min interval
    temp_2nd = data['Ambient Temperature_2nd station (Deg C)']
    temp_2nd = temp_2nd.loc['2023-01-01 00:00:00+00:00' : '2023-12-31 23:55:00+00:00']
    temp_2nd = temp_2nd.dropna()
    temp_2nd = temp_2nd.asfreq('5T', method='ffill') 
    
    
    #Selecting the temperature sensor
    if temp_sensor == 'weather_station':
        temp_air = data['Ambient Temperature (Deg C)']
    elif temp_sensor == '2nd weather_station'    :
        temp_air = temp_2nd
    
    
        
    #Temperature model
    temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    temp_cell = pvlib.temperature.sapm_cell(POA_global,
                                                   temp_air,
                                                   wind_speed,
                                                   temperature_model_parameters["a"],
                                                   temperature_model_parameters["b"],
                                                   temperature_model_parameters["deltaT"]) #wind speed should be at a height of 10 m
    
    
    #Apply the single diode model
    I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, Adjust =pvlib.ivtools.sdm.fit_cec_sam(PV_data['celltype'], 
                                  v_mp = PV_data['v_mp'], 
                                  i_mp = PV_data['i_mp'],
                                  v_oc = PV_data['v_oc'],
                                  i_sc = PV_data['i_sc'],
                                  alpha_sc = PV_data['alpha_sc'],
                                  beta_voc = PV_data['beta_voc'],
                                  gamma_pmp = PV_data['gamma_pdc'],
                                  cells_in_series= PV_data['cells_in_series'],
                                  temp_ref=PV_data['temp_ref'])
    
    #Calculate the CEC parameters at the effective irradiance
    cec_param = pvlib.pvsystem.calcparams_cec(eff_irrad_total,
                                  temp_cell,
                                  alpha_sc,
                                  a_ref,
                                  I_L_ref,
                                  I_o_ref,
                                  R_sh_ref,
                                  R_s,
                                  Adjust)
    
    #max power for single module 
    mpp = pvlib.pvsystem.max_power_point(*cec_param,method='newton')

    
    #Defining the total system of multiple modules
    system = PVSystem(modules_per_string=installation_data['modules_per_string'], strings_per_inverter=installation_data['strings_per_inverter'])
    #DC from the whole PV system without losses
    dc_scaled_no_loss = system.scale_voltage_current_power(mpp)
    
    mid_rows = PVSystem(modules_per_string=installation_data['modules_per_string'], strings_per_inverter=2)
    dc_mid_rows_no_loss = mid_rows.scale_voltage_current_power(mpp)
    
    
    #Losses for the modules
    losses = (pvlib.pvsystem.pvwatts_losses(soiling=2, shading=0, snow=0, mismatch=2, wiring=2, connections=0.5, lid=0, nameplate_rating=1, age=0, availability=0))/100
    dc_scaled = dc_scaled_no_loss*(1-losses)
    
    dc_mid_rows = dc_mid_rows_no_loss * (1-losses)
    
    
    return dc_scaled,dc_mid_rows, eff_irrad_total, temp_cell, temp_air
    
        
        
        
   ##### New version



def DC_generation_temp_select(POA,PV_data, installation_data, temp_sensor, wind_sensor,shadow, mount_type, pyranometer=True, inverter_limit = True):
    
    """Calculates the generated DC from POA irradiance
    
    Parameters
    -------
    POA : 
        DataFrame with the "fuel-in POA" for East and West side, East side is assumed to be the back side of the panel.
            
    
    PV_data :  
        dict containing the data about the PV panels   

    
    Installation_data :  
        dict containing the data for the installation
        
    temp_sensor :
        

    Returns
    -------
    DC_output : 
        Output is a series with the generated DC  
    """
    
    import pvlib
    import pandas as pd
    import numpy as np
    from pvlib.pvsystem import PVSystem
    from collections import OrderedDict
    
    #import data
    data=pd.read_csv('resources/clean_data.csv',
                     index_col=0)
    
    data.index = pd.to_datetime(data.index, utc=True)
    
    # Selection of the right data based on the mounting type
    if mount_type == 'Vertical':
        if pyranometer == True:
            #Include shadow from structure or not
            if shadow =='False':
                eff_irrad_West = POA['POA fuel_in West']
                eff_irrad_East = POA['POA fuel_in East']*PV_data['bifaciality']
                eff_irrad_total = eff_irrad_West + eff_irrad_East
                POA_global = POA['POA Global']
            #elif shadow =='True':
              #  eff_irrad_West = POA['POA effective West']
              #  eff_irrad_East = POA['POA effective East']*PV_data['bifaciality']
              #  eff_irrad_total = eff_irrad_West + eff_irrad_East
              #  POA_global = POA['POA Global_shadow']
        if pyranometer == False:
            eff_irrad_East = data['Reference Cell Vertical East (W.m-2)']*PV_data['bifaciality']
            eff_irrad_West = data['Reference Cell Vertical West (W.m-2)']
            eff_irrad_total = eff_irrad_West + eff_irrad_East
            POA_global = data['Reference Cell Vertical East (W.m-2)'] + data['Reference Cell Vertical West (W.m-2)']
        
        
    if mount_type == 'Tilted':
        if pyranometer == True:
            #Include shadow from structure or not
            if shadow =='False':
                eff_irrad_down = POA['POA fuel_in West']*PV_data['bifaciality']
                eff_irrad_up = POA['POA fuel_in East']
                eff_irrad_total = eff_irrad_down + eff_irrad_up
                POA_global = POA['POA Global']
            #elif shadow =='True':
                #eff_irrad_West = POA['POA effective West']
                #eff_irrad_East = POA['POA effective East']
                #eff_irrad_total = eff_irrad_West + eff_irrad_East
                #POA_global = POA['POA Global_shadow']
        if pyranometer == False:
            eff_irrad_up = data['Reference Cell Tilted facing up (W.m-2)']
            eff_irrad_down = data['Reference Cell Tilted facing down (W.m-2)']*PV_data['bifaciality']
            eff_irrad_total = eff_irrad_up + eff_irrad_down
            POA_global = data['Reference Cell Tilted facing up (W.m-2)'] + data['Reference Cell Tilted facing down (W.m-2)'] 
            
        
            
        
    
    
    # Wind speed at sensor
    wind_speed = data['wind velocity (m.s-1)']
    
    #Wind speed equation from www.wind-data.ch
    #Estimation of the wind speed in 10 meter from the measurement in 2 meter 

    h_2 = 10 #height where the wind speed is needed for temperature calculations with sandia
    h_1 = 2 #height of the anemomenter at the weather station 
    z_0 = 0.03 #roughness height
    wind_10 = wind_speed*(np.log(h_2/z_0)/np.log(h_1/z_0))
    
    
    
    alpha_sc = PV_data['alpha_sc']
    
    
    
    #Transforming the hourly measurements from 2nd weather station to 5 min interval
    wind_speed_2nd_10m = data['wind velocity_2nd station 10m height (m.s-1)']
    wind_speed_2nd_10m = wind_speed_2nd_10m.loc['2023-01-01 00:00:00+00:00' : '2023-12-31 23:55:00+00:00']
    wind_speed_2nd_10m = wind_speed_2nd_10m.dropna()
    wind_speed_2nd_10m = wind_speed_2nd_10m.asfreq('5T', method='ffill')
    # Transforming back to the index of data. 
    wind_speed_2nd_10m = wind_speed_2nd_10m.reindex(data.index, fill_value = 'nan')
    #Selects the available sensor
    selected_wind_10m = np.where(pd.notna(wind_10), wind_10, wind_speed_2nd_10m)
    
    # Create a new Series from the selected values
    wind_sensor_select_10m = pd.Series(selected_wind_10m, index=data.index, dtype=float)
    
    #Selecting the wind_sensor sensor
    if wind_sensor == 'default':
        wind_speed = wind_sensor_select_10m
    elif wind_sensor == 'weather_station':
        wind_speed = wind_10
    elif wind_sensor == '2nd weather_station'    :
        wind_speed = wind_speed_2nd_10m
    
    
    
    
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
    
    """
    # Combine into a DataFrame
    temp_df = pd.DataFrame({'temp_2nd': temp_2nd, 'temp_WS': temp_WS})
    
    # Create a new Series based on the conditions
    def select_series(row):
        if pd.notna(row['temp_WS']):
            return 'temp_WS'
        elif pd.notna(row['temp_2nd']):
            return 'temp_2nd'
        return 'temp_WS'  # Default to temp_WS in case both are NaN or both not NaN
    
    temp_sensor_select = temp_df.apply(select_series, axis=1)
    """
    
    
    #Selecting the temperature sensor
    if temp_sensor == 'default':
        temp_air = temp_sensor_select
    elif temp_sensor == 'weather_station':
        temp_air = data['Ambient Temperature (Deg C)']
    elif temp_sensor == '2nd weather_station'    :
        temp_air = temp_2nd
    
    
        
    #Temperature model
    temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    temp_cell = pvlib.temperature.sapm_cell(POA_global,
                                                   temp_air,
                                                   wind_speed,
                                                   temperature_model_parameters["a"],
                                                   temperature_model_parameters["b"],
                                                   temperature_model_parameters["deltaT"]) #wind speed should be at a height of 10 m
    
    
    #Apply the single diode model
    I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, Adjust =pvlib.ivtools.sdm.fit_cec_sam(PV_data['celltype'], 
                                  v_mp = PV_data['v_mp'], 
                                  i_mp = PV_data['i_mp'],
                                  v_oc = PV_data['v_oc'],
                                  i_sc = PV_data['i_sc'],
                                  alpha_sc = PV_data['alpha_sc'],
                                  beta_voc = PV_data['beta_voc'],
                                  gamma_pmp = PV_data['gamma_pdc'],
                                  cells_in_series= PV_data['cells_in_series'],
                                  temp_ref=PV_data['temp_ref'])
    
    #Calculate the CEC parameters at the effective irradiance
    cec_param = pvlib.pvsystem.calcparams_cec(eff_irrad_total,
                                  temp_cell,
                                  alpha_sc,
                                  a_ref,
                                  I_L_ref,
                                  I_o_ref,
                                  R_sh_ref,
                                  R_s,
                                  Adjust)
    
    #max power for single module 
    mpp = pvlib.pvsystem.max_power_point(*cec_param,method='newton')

    
    #Defining the total system of multiple modules
    system = PVSystem(modules_per_string=installation_data['modules_per_string'], strings_per_inverter=installation_data['strings_per_inverter'])
    #DC from the whole PV system without losses
    dc_scaled_no_loss = system.scale_voltage_current_power(mpp)
    
    mid_rows = PVSystem(modules_per_string=installation_data['modules_per_string'], strings_per_inverter=2)
    dc_mid_rows_no_loss = mid_rows.scale_voltage_current_power(mpp)
    
    
    #Losses for the modules
    losses = (pvlib.pvsystem.pvwatts_losses(soiling=2, shading=0, snow=0, mismatch=2, wiring=2, connections=0.5, lid=0, nameplate_rating=1, age=0, availability=0))/100
    dc_scaled = dc_scaled_no_loss*(1-losses)
    
    dc_mid_rows = dc_mid_rows_no_loss * (1-losses)
    
    #Limits the DC output. This should first be limited be the inverter 
    # but this limit can be observed on the DC input reading to the inverter
    if inverter_limit == True:
        dc_scaled = dc_scaled.clip(upper=36600)
        
    

    return dc_scaled,dc_mid_rows, eff_irrad_total, temp_cell, temp_air
    
     
    
    

    
def DC_generation_simple(POA_Global, eff_total ,PV_data, installation_data, temp_sensor, wind_sensor , inverter_limit, temperature_model):
    
    """Calculates the generated DC from POA irradiance
    
    Parameters
    -------
    POA : 
        DataFrame with the "fuel-in POA" for East and West side, East side is assumed to be the back side of the panel.
            
    
    PV_data :  
        dict containing the data about the PV panels   

    
    Installation_data :  
        dict containing the data for the installation  

    Returns
    -------
    DC_output : 
        Output is a series with the generated DC  
    """
    
    import pvlib
    import pandas as pd
    import numpy as np
    from pvlib.pvsystem import PVSystem
    from collections import OrderedDict
    
    #import data
    data=pd.read_csv('resources/clean_data.csv',
                     index_col=0)
    
    data.index = pd.to_datetime(data.index, utc=True) 
    

    
    # Wind speed from sensor
    wind_speed = data['wind velocity (m.s-1)']
    
    #Wind speed equation from www.wind-data.ch
    #Estimation of the wind speed in 10 meter from the measurement in 2 meter 

    h_2 = 10 #height where the wind speed is needed for temperature calculations with sandia
    h_1 = 3 #height of the anemomenter at the weather station 
    z_0 = 0.03 #roughness height
    wind_10 = wind_speed*(np.log(h_2/z_0)/np.log(h_1/z_0))
    wind_speed = wind_10
    
    
    alpha_sc = PV_data['alpha_sc']
    
    #Transforming the hourly measurements from 2nd weather station to 5 min interval
    wind_speed_2nd_10m = data['wind velocity_2nd station 10m height (m.s-1)']
    wind_speed_2nd_10m = wind_speed_2nd_10m.loc['2023-01-01 00:00:00+00:00' : '2023-12-31 23:55:00+00:00']
    wind_speed_2nd_10m = wind_speed_2nd_10m.dropna()
    wind_speed_2nd_10m = wind_speed_2nd_10m.asfreq('5T', method='ffill')
    # Transforming back to the index of data. 
    wind_speed_2nd_10m = wind_speed_2nd_10m.reindex(data.index, fill_value = 'nan')
    #Selects the available sensor
    selected_wind_10m = np.where(pd.notna(wind_10), wind_10, wind_speed_2nd_10m)
    
    # Create a new Series from the selected values
    wind_sensor_select_10m = pd.Series(selected_wind_10m, index=data.index, dtype=float)
    
    #Selecting the wind_sensor sensor
    if wind_sensor == 'default':
        wind_speed = wind_sensor_select_10m
    elif wind_sensor == 'weather_station':
        wind_speed = wind_10
    elif wind_sensor == '2nd weather_station'    :
        wind_speed = wind_speed_2nd_10m
    
    
    """
    #Transforming the hourly measurements from 2nd weather station to 5 min interval
    temp_2nd = data['Ambient Temperature_2nd station (Deg C)']
    temp_2nd = temp_2nd.loc['2023-01-01 00:00:00+00:00' : '2023-12-31 23:55:00+00:00']
    temp_2nd = temp_2nd.dropna()
    temp_2nd = temp_2nd.asfreq('5T', method='ffill') 
    
    
    #Selecting the temperature sensor
    if temp_sensor == 'weather_station':
        temp_air = data['Ambient Temperature (Deg C)']
    elif temp_sensor == '2nd weather_station'    :
        temp_air = temp_2nd
    
    """
      
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
    
    
    if temperature_model == 'sapm':
        #Temperature model
        temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
        temp_cell = pvlib.temperature.sapm_cell(POA_Global,
                                                       temp_air,
                                                       wind_speed,
                                                       temperature_model_parameters["a"],
                                                       temperature_model_parameters["b"],
                                                       temperature_model_parameters["deltaT"]) #wind speed should be at a height of 10 m
    elif temperature_model == 'PVsyst29':    
      #calculating the cell temperature after the model from PVsyst

      alpha = 0.9
      effic = 0.2166
      U =29
      #temp_cell = temp_air+ 1/U*(alpha*POA['POA Global']*1-effic)
      
      temp_cell = temp_air + POA_Global* alpha* (1-effic)/(U*wind_speed)
      
      temp_cell = pvlib.temperature.pvsyst_cell(poa_global = POA_Global,
                                                temp_air = temp_air,
                                                wind_speed= wind_speed,
                                                u_c = 29,
                                                u_v = 0,
                                                module_efficiency = effic,
                                                alpha_absorption = 0.9)



    elif temperature_model == 'PVsyst56':    
      #calculating the cell temperature after the model from PVsyst

      alpha = 0.9
      effic = 0.2166
      U_bi = 56
      #temp_cell = temp_air+ 1/U_bi*(alpha*POA['POA Global']*1-effic)
      
      #temp_cell = temp_air + POA['POA Global']* alpha* (1-effic)/(U_bi*wind_speed)

      temp_cell = pvlib.temperature.pvsyst_cell(poa_global = POA_Global,
                                              temp_air = temp_air,
                                              wind_speed= wind_speed,
                                              u_c = 56,
                                              u_v = 0,
                                              module_efficiency = effic,
                                              alpha_absorption = 0.9)
        
      # https://pvpmc.sandia.gov/modeling-guide/2-dc-module-iv/cell-temperature/pvsyst-cell-temperature-model/
    
    #Apply the single diode model
    I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, Adjust =pvlib.ivtools.sdm.fit_cec_sam(PV_data['celltype'], 
                                  v_mp = PV_data['v_mp'], 
                                  i_mp = PV_data['i_mp'],
                                  v_oc = PV_data['v_oc'],
                                  i_sc = PV_data['i_sc'],
                                  alpha_sc = PV_data['alpha_sc'],
                                  beta_voc = PV_data['beta_voc'],
                                  gamma_pmp = PV_data['gamma_pdc'],
                                  cells_in_series= PV_data['cells_in_series'],
                                  temp_ref=PV_data['temp_ref'])
    
    #Calculate the CEC parameters at the effective irradiance
    cec_param = pvlib.pvsystem.calcparams_cec(eff_total,
                                  temp_cell,
                                  alpha_sc,
                                  a_ref,
                                  I_L_ref,
                                  I_o_ref,
                                  R_sh_ref,
                                  R_s,
                                  Adjust)
    
    #max power for single module 
    mpp = pvlib.pvsystem.max_power_point(*cec_param,method='newton')

    
    #Defining the total system of multiple modules
    system = PVSystem(modules_per_string=installation_data['modules_per_string'], strings_per_inverter=installation_data['strings_per_inverter'])
    #DC from the whole PV system without losses
    dc_scaled_no_loss = system.scale_voltage_current_power(mpp)
    
    mid_rows = PVSystem(modules_per_string=installation_data['modules_per_string'], strings_per_inverter=2)
    dc_mid_rows_no_loss = mid_rows.scale_voltage_current_power(mpp)
    
    
    #Losses for the modules
    losses = (pvlib.pvsystem.pvwatts_losses(soiling=2, shading=0, snow=0, mismatch=2, wiring=2, connections=0.5, lid=0, nameplate_rating=1, age=0, availability=0))/100
    dc_scaled = dc_scaled_no_loss*(1-losses)
    
    dc_mid_rows = dc_mid_rows_no_loss * (1-losses)
    
    #Limits the DC output. This should first be limited be the inverter 
    # but this limit can be observed on the DC input reading to the inverter
    if inverter_limit == True:
        dc_scaled = dc_scaled.clip(upper=36600)
        dc_scaled_no_loss = dc_scaled_no_loss.clip(upper=36600)
        dc_mid_rows_no_loss = dc_mid_rows_no_loss.clip(upper=18300)
        dc_mid_rows = dc_mid_rows.clip(upper=18300)
        
    
    return dc_scaled_no_loss,dc_mid_rows_no_loss, temp_cell, temp_air    
    