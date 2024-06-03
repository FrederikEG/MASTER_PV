# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 11:24:52 2024

@author: frede
"""

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
        eff_irrad_West = POA['POA effective West']
        eff_irrad_East = POA['POA effective East']
        eff_irrad_total = eff_irrad_West + eff_irrad_East
        POA_global = POA['POA Global_shadow']
        
    
    
    
    wind_speed = data['wind velocity (m.s-1)']
    alpha_sc = PV_data['alpha_sc']
    
    
    #Transforming the hourly measurements from 2nd weather station to 5 min interval
    temp_2nd = data['Ambient Temperature_2nd station (Deg C)']
    temp_2nd = temp_2nd.loc['2023-01-01 00:00:00+00:00' : '2023-12-31 23:55:00+00:00']
    temp_2nd = temp_2nd.dropna()
    temp_2nd = temp_2nd.asfreq('5T', method='ffill')
    
    
    # Selcting the sensor that's available
    temp_WS = data['Ambient Temperature (Deg C)']

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
    
    
    return dc_scaled,dc_mid_rows, eff_irrad_total, temp_cell, temp_air
    
        
        
        
        