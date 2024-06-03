# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 09:28:03 2024

@author: frede
"""

import pandas as pd
from model_to_run_select import model_to_run_select, interval_select

data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 


tz='UTC' 





# The mount type and model variation doesn't matter - only used to extract installation data
mount_type = 'Tilted'
model_variation = 'sensor'         # 'DNI', 'sensor', 'transposition_simple', 'transposition_inf', 'IAM', 'spectrum'
model_to_run1, model_to_run2, model_to_run3, model_to_run4, PV_data, installation_data = model_to_run_select(model_variation= model_variation, mount_type=mount_type, trans_side='both_sides')


def shadow(PV_data, installation_data, tz,data):
    import pvlib
    import numpy as np
    import pandas as pd
    from collections import OrderedDict

    #Location of PV installation - AU Foulum
    lat = installation_data['lat']
    lon = installation_data['lon']
    altitude= installation_data['altitude']
    pitch = installation_data['pitch']
    gcr = installation_data['gcr']
    tilt = installation_data['tilt']
    orientation = installation_data['orientation']

    location = pvlib.location.Location(lat, lon, tz=tz)


    #The structure holding the panels
    w1 = installation_data['w_vertical_structure']
    w2 = installation_data['w_horizontal_structure']

    #The module
    module_width = PV_data['module_width']
    module_height = PV_data['module_height']
    A_module = module_height *  module_width

    # calculate Sun's coordinates
    solar_position = location.get_solarposition(times=data.index) 

    eta_shadow = np.zeros(len(data))
    L_vertical_array = np.zeros(len(data))
    L_horizontal_array = np.zeros(len(data))
    alpha_array = np.zeros(len(data))
    beta_array = np.zeros(len(data))
    
    n = 0

    for i in range(0,len(data)):
        #Determine the length of the shadow
        if 0 <= solar_position['azimuth'].iloc[n]<=90 and 0 < solar_position['elevation'].iloc[n] <=90 :
           alpha = solar_position['azimuth'].iloc[n]
           L_vertical = (w1/np.tan(np.deg2rad(alpha)))
        elif 90 < solar_position['azimuth'].iloc[n] <=180 and 0 < solar_position['elevation'].iloc[n] <=90:
           alpha = 180-solar_position['azimuth'].iloc[n]
           L_vertical = (w1/np.tan(np.deg2rad(alpha)))
        elif 180 < solar_position['azimuth'].iloc[n] < 360:
           L_vertical = 0
           alpha = 500
        else: 
           L_vertical = 0
           alpha = 500
           
           
        if L_vertical > module_height:
            L_vertical=module_height
        
           
        A_vertical = L_vertical* module_width 
        
        #Determine the length of the shadow
        if 0 < solar_position['elevation'].iloc[n] <=90 and 0 < solar_position['azimuth'].iloc[n] <=180:
            beta = 180-tilt-solar_position['elevation'].iloc[n]
            L_horizontal = (w2/np.tan(np.deg2rad(beta)))
        else:
            L_horizontal = 0
            beta = 500
       
        if L_horizontal > module_width:
           L_horizontal=module_width
       
            
        A_horizontal = L_horizontal * (module_height-L_vertical)
        
            
        # Area of shadow for a single panel     
        A_shadow = A_vertical + A_horizontal
        eta_shadow1 = (A_module-A_shadow)/A_module
        
        #The shadowed area can not be larger than the module
        #if eta_shadow1 <0:
         #   eta_shadow1 =0
        #else:
         #   eta_shadow1 = eta_shadow1
                

        eta_shadow[n] = eta_shadow1
        L_horizontal_array[n] = L_horizontal
        L_vertical_array[n] = L_vertical
        alpha_array[n] = alpha
        beta_array[n] = beta
        
        n = n+1
        

    eta_shadow = pd.Series(eta_shadow, index=data.index)
    L_horizontal_array = pd.Series(L_horizontal_array, index = data.index)
    L_vertical_array = pd.Series(L_vertical_array, index = data.index)
    alpha_array = pd.Series(alpha_array, index = data.index)
    beta_array = pd.Series(beta_array, index = data.index)
    
    shadow_dict = OrderedDict()
    shadow_dict['eta_shadow'] = eta_shadow
    shadow_dict['L_horizontal'] = L_horizontal_array
    shadow_dict['L_vertical'] = L_vertical_array
    shadow_dict['alpha'] = alpha_array
    shadow_dict['beta'] = beta_array
    shadow_dict['azimuth'] = solar_position['azimuth']
    
    shadow_dict = pd.DataFrame(shadow_dict)
    
    return shadow_dict
    

#eta_shadow,L_horizontal_array,L_vertical_array
    
    
shadow_dict = shadow(PV_data, installation_data, tz,data)