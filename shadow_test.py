# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 10:52:29 2024

@author: frede
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 09:28:03 2024

@author: frede
"""



import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 


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

installation_data =     {'lat' : 56.48985507481198, 
                        'lon' : 9.583764312381613,
                        'altitude' : 63,
                        'orientation' : 90,
                        'tilt' : 90,
                        'pitch' : 10,
                        'modules_per_string' : 20,
                        'strings_per_inverter' : 4,
                        'modules_vertical' : 2,
                        'w_vertical_structure' : 0.05,
                        'w_horizontal_structure' : 0.05}

installation_data['height'] = 2* PV_data['module_width'] + PV_data['module_width']
installation_data['gcr'] = installation_data['height'] /installation_data['pitch']
installation_data['pvrow_width'] = 10*PV_data['module_height']

tz='UTC' 


import pvlib
import numpy as np

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
n = 0

sol=solar_position['azimuth'].iloc[n]
for i in range(0,len(data)):
    #Determine the length of the shadow
    if 0 <= solar_position['azimuth'].iloc[n]<=90:
       alpha = solar_position['azimuth'].iloc[n]
       L_vertical = (w1/np.tan(np.deg2rad(alpha)))
    elif 90 < solar_position['azimuth'].iloc[n] <=180:
       alpha = 180-solar_position['azimuth'].iloc[n]
       L_vertical = (w1/np.tan(np.deg2rad(alpha)))
    elif 180 < solar_position['azimuth'].iloc[n] < 360:
       L_vertical = 0
       
    A_vertical = L_vertical* module_width 
    
    #Determine the length of the shadow
    if 0 < solar_position['elevation'].iloc[n] <=90:
        beta = 180-tilt-solar_position['elevation'].iloc[n]
        L_horizontal = (w2/np.tan(np.deg2rad(beta)))
    else:
        L_horizontal = 0
        
        
    A_horizontal = L_horizontal * (module_height-L_vertical)
    
    #if solar_position['elevation']<=0:
     #   L_horizontal = 0
    #elif 0 < solar_position['elevation'] <=90:
     #   beta = 180-tilt-solar_position['elevation']
      #  L_horizontal = (w2/np.tan(np.deg2rad(beta)))
    #elif 90 < solar_position['elevation']:
        
    # Area of shadow for a single panel     
    A_shadow = A_vertical + A_horizontal
    eta_shadow1 = (A_module-A_shadow)/A_module
    if eta_shadow1 <0:
        eta_shadow1 =0
    else:
        eta_shadow1 = eta_shadow1
            

    eta_shadow[n] = eta_shadow1
    n = n+1
    

eta_shadow = pd.Series(eta_shadow, index=data.index)


    
    
    
