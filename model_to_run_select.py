# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 12:18:29 2024

@author: frede
"""

def model_to_run_select(model_variation, mount_type, trans_side):
    if model_variation == 'DNI':
        model_to_run1 = {'GHI_sensor':'GHI',                     # 'GHI', 'SPN1', 'GHI_2nd' (only hour mean)
                        'sky_model_inf':'isotropic',            # 'isotropic', 'haydavies'
                        'sky_model_simple' : 'isotropic',           # 'isotropic', 'haydavies', 'perez' ......
                        'shadow_interpolate' : 'true',          # 'true', 'false'
                        'temp_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station' 
                        'spectral_mismatch_model' : None,   # 'Sandia','Gueymard', None 
                        'wind_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station'
                        'RH_sensor' : 'default',                # 'default', 'weather_station', '2nd weather_station'  
                        'shadow' : 'False',                     # 'True', 'False'
                        'inverter_model' : 'Sandia',            # 'Sandia', 
                        'model_perez' : 'allsitescomposite1990',
                        'mount_type' : 'Vertical',              # 'Tilted', 'Vertical'
                        'iam_apply' : False,                   # 'ashrae', 'SAPM' and False 
                        'inverter_limit' : True,
                        'DNI_model': 'simple',                   #  'dirint', 'dirindex_turbidity', 'dirindex', 'simple'                      
                        'transposition' : 'simple'}                 # 'simple', 'inf'
        
        if mount_type =='Tilted':
            model_to_run1['mount_type'] = 'Tilted'
        
        model_to_run2 = model_to_run1.copy()
        model_to_run2['DNI_model'] = 'dirint'
        
        model_to_run3 = model_to_run1.copy()
        model_to_run3['DNI_model'] = 'dirindex_turbidity'
        
        model_to_run4 = False
        

        
    if model_variation == 'sensor':
        # Remember to update with the best fit DHI model
        model_to_run1 = {'GHI_sensor':'GHI',                     # 'GHI', 'SPN1', 'GHI_2nd' (only hour mean)
                        'sky_model_inf':'isotropic',            # 'isotropic', 'haydavies'
                        'sky_model_simple' : 'isotropic',           # 'isotropic', 'haydavies', 'perez' ......
                        'shadow_interpolate' : 'true',          # 'true', 'false'
                        'temp_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station' 
                        'spectral_mismatch_model' : None,   # 'Sandia','Gueymard', None 
                        'wind_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station'
                        'RH_sensor' : 'default',                # 'default', 'weather_station', '2nd weather_station'  
                        'shadow' : 'False',                     # 'True', 'False'
                        'inverter_model' : 'Sandia',            # 'Sandia', 
                        'model_perez' : 'allsitescomposite1990',
                        'mount_type' : 'Vertical',              # 'Tilted', 'Vertical'
                        'iam_apply' : False,                   # 'ashrae', 'SAPM' and False 
                        'inverter_limit' : True,
                        'DNI_model': 'simple',                  #  'dirint', 'dirindex_turbidity', 'dirindex', 'simple'                      
                        'transposition' : 'simple'}                  # 'simple', 'inf'
        
        if mount_type =='Tilted':
            model_to_run1['mount_type'] = 'Tilted'
        
        model_to_run2 = model_to_run1.copy()
        model_to_run2['GHI_sensor'] = 'SPN1'
        
        model_to_run3 = False
        model_to_run4 = False
    
    if model_variation == 'transposition_simple':
        # Remember to update with the best model from previous model_to_run
        model_to_run1 = {'GHI_sensor':'SPN1',                     # 'GHI', 'SPN1', 'GHI_2nd' (only hour mean)
                        'sky_model_inf':'isotropic',            # 'isotropic', 'haydavies'
                        'sky_model_simple' : 'isotropic',           # 'isotropic', 'haydavies', 'perez' ......
                        'shadow_interpolate' : 'true',          # 'true', 'false'
                        'temp_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station' 
                        'spectral_mismatch_model' : None,   # 'Sandia','Gueymard', None 
                        'wind_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station'
                        'RH_sensor' : 'default',                # 'default', 'weather_station', '2nd weather_station'  
                        'shadow' : 'False',                     # 'True', 'False'
                        'inverter_model' : 'Sandia',            # 'Sandia', 
                        'model_perez' : 'allsitescomposite1990',
                        'mount_type' : 'Vertical',              # 'Tilted', 'Vertical'
                        'iam_apply' : False,                   # 'ashrae', 'SAPM' and False 
                        'inverter_limit' : True,
                        'DNI_model': 'simple',                  #  'dirint', 'dirindex_turbidity', 'dirindex', 'simple'                      
                        'transposition' : 'simple'}             # 'simple', 'inf'          
        
        if mount_type =='Tilted':
            model_to_run1['mount_type'] = 'Tilted'
        
        model_to_run2 = model_to_run1.copy()
        model_to_run2['sky_model_simple'] = 'haydavies'
        
        model_to_run3 = model_to_run1.copy()
        model_to_run3['sky_model_simple'] = 'perez'
        
        model_to_run4 = False
    
    
    
    if model_variation == 'transposition_inf':
        # Remember to update with the best model from previous model_to_run
        model_to_run1 = {'GHI_sensor':'SPN1',                     # 'GHI', 'SPN1', 'GHI_2nd' (only hour mean)
                        'sky_model_inf':'isotropic',            # 'isotropic', 'haydavies'
                        'sky_model_simple' : 'isotropic',           # 'isotropic', 'haydavies', 'perez' ......
                        'shadow_interpolate' : 'true',          # 'true', 'false'
                        'temp_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station' 
                        'spectral_mismatch_model' : None,   # 'Sandia','Gueymard', None 
                        'wind_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station'
                        'RH_sensor' : 'default',                # 'default', 'weather_station', '2nd weather_station'  
                        'shadow' : 'False',                     # 'True', 'False'
                        'inverter_model' : 'Sandia',            # 'Sandia', 
                        'model_perez' : 'allsitescomposite1990',
                        'mount_type' : 'Vertical',              # 'Tilted', 'Vertical'
                        'iam_apply' : False,                   # 'ashrae', 'SAPM' and False 
                        'inverter_limit' : True,
                        'DNI_model': 'simple',                  #  'dirint', 'dirindex_turbidity', 'dirindex', 'simple' 
                        'transposition' : 'inf'}             # 'simple', 'inf'                                  
        
        if mount_type =='Tilted':
            model_to_run1['mount_type'] = 'Tilted'
        
        model_to_run2 = model_to_run1.copy()
        model_to_run2['sky_model_inf'] = 'haydavies'
        
        model_to_run3 = False
        model_to_run4 = False
        
        
        
    if model_variation == 'IAM':
        model_to_run1 = {'GHI_sensor':'SPN1',                     # 'GHI', 'SPN1', 'GHI_2nd' (only hour mean)
                        'sky_model_inf':'isotropic',            # 'isotropic', 'haydavies'
                        'sky_model_simple' : 'isotropic',           # 'isotropic', 'haydavies', 'perez' ......
                        'shadow_interpolate' : 'true',          # 'true', 'false'
                        'temp_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station' 
                        'spectral_mismatch_model' : None,   # 'Sandia','Gueymard', None 
                        'wind_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station'
                        'RH_sensor' : 'default',                # 'default', 'weather_station', '2nd weather_station'  
                        'shadow' : 'False',                     # 'True', 'False'
                        'inverter_model' : 'Sandia',            # 'Sandia', 
                        'model_perez' : 'allsitescomposite1990',
                        'mount_type' : 'Vertical',              # 'Tilted', 'Vertical'
                        'iam_apply' : False,                   # 'ashrae', 'SAPM' and False 
                        'inverter_limit' : True,
                        'DNI_model': 'simple',                   #  'dirint', 'dirindex_turbidity', 'dirindex', 'simple'                      
                        'transposition' : 'simple'}                 # 'simple', 'inf'
        
        if mount_type =='Tilted':
            model_to_run1['mount_type'] = 'Tilted'
            
        if trans_side =='Up':
            model_to_run1['sky_model_simple'] = 'isotropic'
            model_to_run1['transposition'] = 'simple'
            
        if trans_side =='Down':
            model_to_run1['sky_model_inf'] = 'haydavies'
            model_to_run1['transposition'] = 'inf'
            
        if trans_side =='East':
            model_to_run1['sky_model_simple'] = 'perez'
            model_to_run1['transposition'] = 'simple'   
            
        if trans_side =='West':
            model_to_run1['sky_model_inf'] = 'isotropic'
            model_to_run1['transposition'] = 'inf'      
        
        model_to_run2 = model_to_run1.copy()
        model_to_run2['iam_apply'] = 'ashrae'
        
        model_to_run3 = model_to_run1.copy()
        model_to_run3['iam_apply'] = 'SAPM'
        
        model_to_run4 = False
    
    
    
    
    if model_variation == 'spectrum':
        model_to_run1 = {'GHI_sensor':'SPN1',                     # 'GHI', 'SPN1', 'GHI_2nd' (only hour mean)
                        'sky_model_inf':'isotropic',            # 'isotropic', 'haydavies'
                        'sky_model_simple' : 'isotropic',           # 'isotropic', 'haydavies', 'perez' ......
                        'shadow_interpolate' : 'true',          # 'true', 'false'
                        'temp_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station' 
                        'spectral_mismatch_model' : None,   # 'Sandia','Gueymard', None 
                        'wind_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station'
                        'RH_sensor' : 'default',                # 'default', 'weather_station', '2nd weather_station'  
                        'shadow' : 'False',                     # 'True', 'False'
                        'inverter_model' : 'Sandia',            # 'Sandia', 
                        'model_perez' : 'allsitescomposite1990',
                        'mount_type' : 'Vertical',              # 'Tilted', 'Vertical'
                        'iam_apply' : 'SAPM',                   # 'ashrae', 'SAPM' and False 
                        'inverter_limit' : True,
                        'DNI_model': 'simple',                   #  'dirint', 'dirindex_turbidity', 'dirindex', 'simple'                      
                        'transposition' : 'simple'}                 # 'simple', 'inf'
        
        if mount_type =='Tilted':
            model_to_run1['mount_type'] = 'Tilted'
              
        if trans_side =='Up':
            model_to_run1['sky_model_simple'] = 'isotropic'
            model_to_run1['transposition'] = 'simple'
            
        if trans_side =='Down':
            model_to_run1['sky_model_inf'] = 'haydavies'
            model_to_run1['transposition'] = 'inf'
            
        if trans_side =='East':
            model_to_run1['sky_model_simple'] = 'perez'
            model_to_run1['transposition'] = 'simple'   
            
        if trans_side =='West':
            model_to_run1['sky_model_inf'] = 'isotropic'
            model_to_run1['transposition'] = 'inf'        
            
        
        model_to_run2 = model_to_run1.copy()
        model_to_run2['spectral_mismatch_model'] = 'Sandia'
        
        model_to_run3 = model_to_run1.copy()
        model_to_run3['spectral_mismatch_model'] = 'Gueymard'
        
        model_to_run4 = False
        
        
        
    if model_variation == 'DC':
        model_to_run1 = {'GHI_sensor':'SPN1',                     # 'GHI', 'SPN1', 'GHI_2nd' (only hour mean)
                        'sky_model_inf':'isotropic',            # 'isotropic', 'haydavies'
                        'sky_model_simple' : 'isotropic',           # 'isotropic', 'haydavies', 'perez' ......
                        'shadow_interpolate' : 'true',          # 'true', 'false'
                        'temp_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station' 
                        'spectral_mismatch_model' : 'Sandia',   # 'Sandia','Gueymard', None 
                        'wind_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station'
                        'RH_sensor' : 'default',                # 'default', 'weather_station', '2nd weather_station'  
                        'shadow' : 'False',                     # 'True', 'False'
                        'inverter_model' : 'Sandia',            # 'Sandia', 
                        'model_perez' : 'allsitescomposite1990',
                        'mount_type' : 'Vertical',              # 'Tilted', 'Vertical'
                        'iam_apply' : 'SAPM',                   # 'ashrae', 'SAPM' and False 
                        'inverter_limit' : True,
                        'DNI_model': 'simple',                   #  'dirint', 'dirindex_turbidity', 'dirindex', 'simple'                      
                        'transposition' : 'simple'}                 # 'simple', 'inf'
        
        if mount_type =='Tilted':
            model_to_run1['mount_type'] = 'Tilted'
        

        model_to_run2 = False
        model_to_run3 = False
        model_to_run4 = False
        
        
    if model_variation == 'AC':
        model_to_run1 = {'GHI_sensor':'SPN1',                     # 'GHI', 'SPN1', 'GHI_2nd' (only hour mean)
                        'sky_model_inf':'isotropic',            # 'isotropic', 'haydavies'
                        'sky_model_simple' : 'isotropic',           # 'isotropic', 'haydavies', 'perez' ......
                        'shadow_interpolate' : 'true',          # 'true', 'false'
                        'temp_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station' 
                        'spectral_mismatch_model' : 'Sandia',   # 'Sandia','Gueymard', None 
                        'wind_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station'
                        'RH_sensor' : 'default',                # 'default', 'weather_station', '2nd weather_station'  
                        'shadow' : 'False',                     # 'True', 'False'
                        'inverter_model' : 'Sandia',            # 'Sandia', 
                        'model_perez' : 'allsitescomposite1990',
                        'mount_type' : 'Vertical',              # 'Tilted', 'Vertical'
                        'iam_apply' : 'SAPM',                   # 'ashrae', 'SAPM' and False 
                        'inverter_limit' : True,
                        'DNI_model': 'simple',                   #  'dirint', 'dirindex_turbidity', 'dirindex', 'simple'                      
                        'transposition' : 'simple'}                 # 'simple', 'inf'
        
        if mount_type =='Tilted':
            model_to_run1['mount_type'] = 'Tilted'
        

        model_to_run2 = False
        model_to_run3 = False
        model_to_run4 = False
    
    
    if model_variation == 'ACDC':
        model_to_run1 = {'GHI_sensor':'SPN1',                     # 'GHI', 'SPN1', 'GHI_2nd' (only hour mean)
                        'sky_model_inf':'isotropic',            # 'isotropic', 'haydavies'
                        'sky_model_simple' : 'isotropic',           # 'isotropic', 'haydavies', 'perez' ......
                        'shadow_interpolate' : 'true',          # 'true', 'false'
                        'temp_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station' 
                        'spectral_mismatch_model' : None,   # 'Sandia','Gueymard', None 
                        'wind_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station'
                        'RH_sensor' : 'default',                # 'default', 'weather_station', '2nd weather_station'  
                        'shadow' : 'False',                     # 'True', 'False'
                        'inverter_model' : 'Sandia',            # 'Sandia', 
                        'model_perez' : 'allsitescomposite1990',
                        'mount_type' : 'Vertical',              # 'Tilted', 'Vertical'
                        'iam_apply' : 'SAPM',                   # 'ashrae', 'SAPM' and False 
                        'inverter_limit' : True,
                        'DNI_model': 'simple',                   #  'dirint', 'dirindex_turbidity', 'dirindex', 'simple'                      
                        'transposition' : 'simple'}                 # 'simple', 'inf'
        
        if mount_type =='Tilted':
            model_to_run1['mount_type'] = 'Tilted'
            model_to_run2 = model_to_run1.copy()
                  
            #Tilt up
            model_to_run1['sky_model_simple'] = 'isotropic'
            model_to_run1['transposition'] = 'simple'
            model_to_run1['spectral_mismatch_model'] = None
            
            # Tilt down
            model_to_run2['sky_model_inf'] = 'haydavies'
            model_to_run2['transposition'] = 'inf'
            model_to_run2['spectral_mismatch_model'] = 'Gueymard'
           
        if mount_type =='Vertical':
            model_to_run2 = model_to_run1.copy()
            
            #East
            model_to_run1['sky_model_simple'] = 'perez'
            model_to_run1['transposition'] = 'simple'
            model_to_run1['spectral_mismatch_model'] = 'Gueymard'
            
            # West
            model_to_run2['sky_model_inf'] = 'isotropic'
            model_to_run2['transposition'] = 'inf' 
            model_to_run2['spectral_mismatch_model'] = None
        
        

    
        model_to_run3 = False
        model_to_run4 = False
    
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


    if mount_type == 'Tilted':
        #Adding all data for the installation to one dict
        installation_data =     {'lat' : 56.493786, 
                                'lon' : 9.560852,
                                'altitude' : 47,
                                'orientation' : 184,
                                'tilt' : 25,
                                'pitch' : 12.058,
                                'row_spacing' : 9.41,
                                'modules_per_string' : 20,
                                'strings_per_inverter' : 4,
                                'modules_vertical' : 2,
                                'w_vertical_structure' : 0.1,
                                'w_horizontal_structure' : 0.1,
                                'inverter' : 'Huawei_Technologies_Co___Ltd___SUN2000_40KTL_US__480V_'}
    
        #installation_data['height'] = 2* PV_data['module_width'] + PV_data['module_width']
        #installation_data['gcr'] = installation_data['height'] /installation_data['pitch']
        installation_data['pvrow_width'] = 20*PV_data['module_width']
        installation_data['height'] = 1.664
        installation_data['gcr'] = (PV_data['module_height']) /installation_data['pitch']
        
    elif mount_type == 'Vertical':
        #Adding all data for the installation to one dict
        installation_data =     {'lat' : 56.493786, 
                                'lon' : 9.560852,
                                'altitude' : 47,
                                'orientation' : 97,
                                'tilt' : 90,
                                'pitch' : 11.013,
                                'row_spacing' : 10.61,
                                'modules_per_string' : 20,
                                'strings_per_inverter' : 4,
                                'modules_vertical' : 2,
                                'w_vertical_structure' : 0.1,
                                'w_horizontal_structure' : 0.1,
                                'inverter' : 'Huawei_Technologies_Co___Ltd___SUN2000_40KTL_US__480V_'}
    
        #installation_data['height'] = 2* PV_data['module_width'] + PV_data['module_width']
        #installation_data['gcr'] = installation_data['height'] /installation_data['pitch']
        installation_data['pvrow_width'] = 10*PV_data['module_height']
        installation_data['height'] = 2.948
        installation_data['gcr'] = 2.638 /installation_data['pitch']

    
    return model_to_run1, model_to_run2, model_to_run3, model_to_run4, PV_data, installation_data



def interval_select(interval_type, data,filter_faulty):
    import pandas as pd
    
    
    tz='UTC' 
    
            
    start_date1 = '2023-05-01 00:00:00'
    end_date1 = '2023-05-17 23:55:00'
    
    start_date2 = '2023-10-10 00:00:00'
    end_date2 = '2023-11-18 23:55:00'
    
    start_date3 = '2023-11-29 00:00:00'
    end_date3 = '2023-12-25 23:55:00'
    
    start_date4 = '2024-01-17 00:00:00'
    end_date4 = '2024-02-02 23:55:00'
    
    
    time_index1 = pd.date_range(start=start_date1, 
                                     end=end_date1, 
                                     freq='5min',  
                                         tz=tz)
    
    time_index2 = pd.date_range(start=start_date2, 
                                     end=end_date2, 
                                     freq='5min',  
                                         tz=tz)
    
    time_index3 = pd.date_range(start=start_date3, 
                                     end=end_date3, 
                                     freq='5min',  
                                         tz=tz)
    
    time_index4 = pd.date_range(start=start_date4, 
                                     end=end_date4, 
                                     freq='5min',  
                                         tz=tz)
    
    if interval_type == 'all_relevant':
        #The intervals - construction of time_index
    
        # Concatenating the DatetimeIndex objects
        combined_index = pd.concat([pd.Series(time_index1), pd.Series(time_index2), pd.Series(time_index3), pd.Series(time_index4)]).reset_index(drop=True)
        
        # Converting back to DatetimeIndex if necessary
        time_index = pd.DatetimeIndex(combined_index)
        
        
    elif interval_type == 'interval1':
        time_index = time_index1
        
    elif interval_type == 'interval2':
        time_index = time_index2
        
    elif interval_type == 'interval3':
        time_index = time_index3
        
    elif interval_type == 'interval4':
        time_index = time_index4
            
        
    elif interval_type == 'sunny':
        start_date = '2023-05-12 00:00:00'
        end_date='2023-05-12 23:55:00'
        
        time_index = pd.date_range(start=start_date, 
                                         end=end_date, 
                                         freq='5min',  
                                             tz=tz)
        
    elif interval_type == 'cloudy':
        start_date = '2023-05-17 00:00:00'
        end_date='2023-05-17 23:55:00'
        
        time_index = pd.date_range(start=start_date, 
                                         end=end_date, 
                                         freq='5min',  
                                             tz=tz)
        
    """    
    #Only the specified time index
    GHI_CMP6 = pd.to_numeric(data[('GHI (W.m-2)')])[time_index]
    GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')])[time_index]
    GHI_2nd = pd.to_numeric(data[('GHI_2nd station (W.m-2)')])[time_index]
    DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])[time_index]
    """    
    
    
    #Only the specified time index
    GHI_CMP6 = data[('GHI (W.m-2)')].copy()[time_index]
    GHI_SPN1 = data[('GHI_SPN1 (W.m-2)')].copy()[time_index]
    GHI_2nd = data[('GHI_2nd station (W.m-2)')].copy()[time_index]
    DHI_SPN1 = data[('DHI_SPN1 (W.m-2)')].copy()[time_index]
    
    ref_up = data['Reference Cell Tilted facing up (W.m-2)'].copy()[time_index]
    ref_down = data['Reference Cell Tilted facing down (W.m-2)'].copy()[time_index]
    
    ref_East = data['Reference Cell Vertical East (W.m-2)'].copy()[time_index]
    ref_West = data['Reference Cell Vertical West (W.m-2)'].copy()[time_index]
    
    
    # Filter out faulty measurements
    if filter_faulty == True:
        irrad_max = 1200
        
        #GHI_CMP6 = GHI_CMP6[(GHI_CMP6 <= irrad_max) &(DHI_SPN1 <= irrad_max)]
        #GHI_SPN1 = GHI_SPN1[(GHI_SPN1 <= irrad_max) & (DHI_SPN1 <= irrad_max)]
        #GHI_2nd = GHI_2nd[(GHI_2nd <= irrad_max) & (DHI_SPN1 <= irrad_max)]
        #DHI_SPN1 = DHI_SPN1[DHI_SPN1 <= irrad_max]
        
        #GHI_CMP6 = GHI_CMP6[(GHI_CMP6 <= irrad_max) &(DHI_SPN1 <= irrad_max) & (GHI_SPN1 <= irrad_max)]
        
        ref_up = ref_up[(ref_up <= irrad_max) & (ref_down <= irrad_max) & (ref_East <= irrad_max) & (ref_West <= irrad_max) & (GHI_CMP6 <= irrad_max) &(DHI_SPN1 <= irrad_max) & (GHI_SPN1 <= irrad_max) ]
        
        
        
        time_index = ref_up.index
        
    return time_index
        

