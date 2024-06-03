# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 13:27:33 2024

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
from model_to_run_select import model_to_run_select

"""
def POA_slope_adjust(slope, measured_value, modelled_value):
    POA_adjusted = modelled_value*slope
    from daily_plots import day_plot, scatter_plot, solar_pos_scat, bar_plots, day_histo_plot, reg_line
    scatter_plot('Ref ', 
                 y_label = 'Measured',
                 x_label = 'Modelled',
                 modelled_value = POA_adjusted, 
                 measured_value = measured_value, 
                 #start_date = start_date, 
                 #end_date=end_date,
                 start_date = start_date, 
                 end_date=end_date,
                 solar_position= solar_position1,
                 interval='afternoon',
                 color_value= solar_position1['azimuth'],
                 y_lim = 1000,
                 model_to_run = model_to_run4,
                 model_explain= model_explain_scatter,
                 elevation_min= elevation_min1)  # False to have no lower bound on elevation

"""





















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


model_explain = False
model_explain_scatter = False
y_lines = True

slope_adjust = True

start_date = '2023-04-12 00:00:00'
end_date='2023-05-13 00:00:00'



custom_label_dni = ['simple', 'dirint', 'dirindex_turbidity', 'dirindex', 'ref cell']
custom_label_sensor = ['GHI', 'SPN1','','','ref cell']
custom_label_transposition_simple = ['isotropic', 'haydavies', 'perez', '', 'ref cell']
custom_label_transposition_inf = ['isotropic', 'haydavies', '', '', 'ref cell']
custom_label_IAM = ['none', 'ashrae', 'SAPM','', 'ref cell']
custom_label_spectrum = ['none', 'Sandia', 'Gueymard', '', 'ref cell']


side_of_panel = 'West'
other_side_of_panel = 'East'

mount_type = 'Tilted'
model_variation = 'DNI'         # 'DNI', 'sensor', 'transposition_simple', 'transposition_inf', 'IAM', 'spectrum'


if mount_type == 'Vertical':
    side_of_panel = 'West'
    other_side_of_panel = 'East'
elif mount_type=='Tilted':
    side_of_panel = 'Down'
    other_side_of_panel = 'Up'


if model_variation == 'DNI':
    custom_label = custom_label_dni
elif model_variation == 'sensor':
    custom_label = custom_label_sensor
elif model_variation == 'transposition_simple':
    custom_label = custom_label_transposition_simple
elif model_variation == 'transposition_inf':
    custom_label = custom_label_transposition_inf
elif model_variation == 'IAM':
    custom_label = custom_label_IAM
elif model_variation == 'spectrum':
    custom_label = custom_label_spectrum
    
    

#%%% Importing the model_to_run


model_to_run1, model_to_run2, model_to_run3, model_to_run4 = model_to_run_select(model_variation= model_variation, mount_type=mount_type)



#%%% Create folder for the data 
from pathlib import Path

# Specify the name or path to the new directory
folder_name = './results/'+str(model_to_run1['mount_type'])+'_'+str(model_variation)

# Create the directory; parents=True allows creating parent directories if needed, exist_ok=True avoids an error if the directory already exists
try:
    Path(folder_name).mkdir(parents=True, exist_ok=True)
    print(f"Directory '{folder_name}' created successfully")
except OSError as error:
    print(f"Creation of the directory '{folder_name}' failed: {error}")


#%%%




#%%% Running the POA simple models 



if model_to_run1 != False and model_to_run1['transposition'] =='simple':
    POA_no_shad1, poa_no_shadow_east1, poa_no_shadow_west1, poa_no_shadow_both1, GHI1, dni1, solar_position1, elevation_min1, albedo_high1  = POA_simple(PV_data,
                      installation_data,
                      tz,
                      GHI_sensor= model_to_run1['GHI_sensor'],
                      model = model_to_run1['sky_model_simple'],
                      shadow_interpolate= model_to_run1['shadow_interpolate'],
                      temp_sensor = model_to_run1['temp_sensor'],
                      spectral_mismatch_model = model_to_run1['spectral_mismatch_model'],
                      RH_sensor = model_to_run1['RH_sensor'],
                      model_perez = model_to_run1['model_perez'],
                      iam_apply = model_to_run1['iam_apply'],
                      DNI_model = model_to_run1['DNI_model'],
                      mount_type = model_to_run1['mount_type'])

if model_to_run2 != False and model_to_run2['transposition'] =='simple':
    POA_no_shad2, poa_no_shadow_east2, poa_no_shadow_west2, poa_no_shadow_both2, GHI2, dni2, solar_position2, elevation_min2, albedo_high2  = POA_simple(PV_data,
                      installation_data,
                      tz,
                      GHI_sensor= model_to_run2['GHI_sensor'],
                      model = model_to_run2['sky_model_simple'],
                      shadow_interpolate= model_to_run2['shadow_interpolate'],
                      temp_sensor = model_to_run2['temp_sensor'],
                      spectral_mismatch_model = model_to_run2['spectral_mismatch_model'],
                      RH_sensor = model_to_run2['RH_sensor'],
                      model_perez = model_to_run2['model_perez'],
                      iam_apply = model_to_run2['iam_apply'],
                      DNI_model = model_to_run2['DNI_model'],
                      mount_type = model_to_run2['mount_type'])

if model_to_run3 != False and model_to_run3['transposition'] =='simple':
    POA_no_shad3, poa_no_shadow_east3, poa_no_shadow_west3, poa_no_shadow_both3, GHI3, dni3, solar_position3, elevation_min3, albedo_high3  = POA_simple(PV_data,
                      installation_data,
                      tz,
                      GHI_sensor= model_to_run3['GHI_sensor'],
                      model = model_to_run3['sky_model_simple'],
                      shadow_interpolate= model_to_run3['shadow_interpolate'],
                      temp_sensor = model_to_run3['temp_sensor'],
                      spectral_mismatch_model = model_to_run3['spectral_mismatch_model'],
                      RH_sensor = model_to_run3['RH_sensor'],
                      model_perez = model_to_run3['model_perez'],
                      iam_apply = model_to_run3['iam_apply'],
                      DNI_model = model_to_run3['DNI_model'],
                      mount_type = model_to_run3['mount_type'])

if model_to_run4 != False and model_to_run4['transposition'] =='simple':
    POA_no_shad4, poa_no_shadow_east4, poa_no_shadow_west4, poa_no_shadow_both4, GHI4, dni4, solar_position4, elevation_min4, albedo_high4  = POA_simple(PV_data,
                      installation_data,
                      tz,
                      GHI_sensor= model_to_run4['GHI_sensor'],
                      model = model_to_run4['sky_model_simple'],
                      shadow_interpolate= model_to_run4['shadow_interpolate'],
                      temp_sensor = model_to_run4['temp_sensor'],
                      spectral_mismatch_model = model_to_run4['spectral_mismatch_model'],
                      RH_sensor = model_to_run4['RH_sensor'],
                      model_perez = model_to_run4['model_perez'],
                      iam_apply = model_to_run4['iam_apply'],
                      DNI_model = model_to_run4['DNI_model'],
                      mount_type = model_to_run4['mount_type'])



#%%% Running the POA inf models

if model_to_run1 != False and model_to_run1['transposition'] =='inf':
    POA1, solar_position1, albedo1, albedo_high1, GHI_inf1, aoi_west1, aoi_east1, spec_loss1, poa_infinite_sheds1, albedo_daily1, dni_inf1, elevation_min1 = POA(PV_data,
                      installation_data,
                      tz,
                      GHI_sensor= model_to_run1['GHI_sensor'],
                      model = model_to_run1['sky_model_inf'],
                      shadow_interpolate= model_to_run1['shadow_interpolate'],
                      temp_sensor = model_to_run1['temp_sensor'],
                      spectral_mismatch_model = model_to_run1['spectral_mismatch_model'],
                      RH_sensor = model_to_run1['RH_sensor'],
                      iam_apply = model_to_run1['iam_apply'],
                      DNI_model = model_to_run1['DNI_model'],
                      mount_type = model_to_run1['mount_type'])




if model_to_run2 != False and model_to_run2['transposition'] =='inf':
    POA2, solar_position2, albedo2, albedo_high2, GHI_inf2, aoi_west2, aoi_east2, spec_loss2, poa_infinite_sheds2, albedo_daily2, dni_inf2, elevation_min2 = POA(PV_data,
                      installation_data,
                      tz,
                      GHI_sensor= model_to_run2['GHI_sensor'],
                      model = model_to_run2['sky_model_inf'],
                      shadow_interpolate= model_to_run2['shadow_interpolate'],
                      temp_sensor = model_to_run2['temp_sensor'],
                      spectral_mismatch_model = model_to_run2['spectral_mismatch_model'],
                      RH_sensor = model_to_run2['RH_sensor'],
                      iam_apply = model_to_run2['iam_apply'],
                      DNI_model = model_to_run2['DNI_model'],
                      mount_type = model_to_run2['mount_type'])


if model_to_run3 != False and model_to_run3['transposition'] =='inf':
    POA3, solar_position3, albedo3, albedo_high3, GHI_inf3, aoi_west3, aoi_east3, spec_loss3, poa_infinite_sheds3, albedo_daily3, dni_inf3, elevation_min3 = POA(PV_data,
                      installation_data,
                      tz,
                      GHI_sensor= model_to_run3['GHI_sensor'],
                      model = model_to_run3['sky_model_inf'],
                      shadow_interpolate= model_to_run3['shadow_interpolate'],
                      temp_sensor = model_to_run3['temp_sensor'],
                      spectral_mismatch_model = model_to_run3['spectral_mismatch_model'],
                      RH_sensor = model_to_run3['RH_sensor'],
                      iam_apply = model_to_run3['iam_apply'],
                      DNI_model = model_to_run3['DNI_model'],
                      mount_type = model_to_run3['mount_type'])



if model_to_run4 != False and model_to_run4['transposition'] =='inf':
    POA4, solar_position4, albedo4, albedo_high4, GHI_inf4, aoi_west4, aoi_east4, spec_loss4, poa_infinite_sheds4, albedo_daily4, dni_inf4, elevation_min4 = POA(PV_data,
                      installation_data,
                      tz,
                      GHI_sensor= model_to_run4['GHI_sensor'],
                      model = model_to_run4['sky_model_inf'],
                      shadow_interpolate= model_to_run4['shadow_interpolate'],
                      temp_sensor = model_to_run4['temp_sensor'],
                      spectral_mismatch_model = model_to_run4['spectral_mismatch_model'],
                      RH_sensor = model_to_run4['RH_sensor'],
                      iam_apply = model_to_run4['iam_apply'],
                      DNI_model = model_to_run4['DNI_model'],
                      mount_type = model_to_run4['mount_type'])


#Ensures that the code can run if not all model_to_run are used
if model_to_run1['transposition'] == 'simple':
    POA_no_shad_copy = POA_no_shad1.copy()
    POA_no_shad_copy.loc[:, :] = 0
    if model_to_run1==False:
        POA_no_shad1 = POA_no_shad_copy
    if model_to_run2==False:
        POA_no_shad2 = POA_no_shad_copy
    if model_to_run3==False:
        POA_no_shad3 = POA_no_shad_copy
    if model_to_run4==False:
        POA_no_shad4 = POA_no_shad_copy
        
if model_to_run1['transposition'] == 'inf':    
    POA_copy = POA1.copy()
    POA_copy.loc[:, :] = 0
    if model_to_run1==False:
        POA1 = POA_copy
    if model_to_run2==False:
        POA2 = POA_copy
    if model_to_run3==False:
        POA3 = POA_copy
    if model_to_run4==False:
        POA4 = POA_copy

#%%%
sun_cloud_days = ['2023-05-12 00:00:00', '2023-05-17 00:00:00']



if model_to_run1['transposition'] == 'simple':
    POA1 = POA_no_shad1
    POA2 = POA_no_shad2
    POA3 = POA_no_shad3
    POA4 = POA_no_shad4



day_plot('POA '+ str(model_variation)+' variation ' + str(side_of_panel)+' - '+ str(model_to_run1['transposition']), 
            'Irradiance',
            value1 = POA1['POA fuel_in '+ str(side_of_panel)],
            value2 = POA2['POA fuel_in '+ str(side_of_panel)],
            value3 = POA3['POA fuel_in '+ str(side_of_panel)],
            value4 = POA4['POA fuel_in '+ str(side_of_panel)],
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            value5 = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'],
            days = sun_cloud_days,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            custom_label= custom_label,
            save_plots = True,
            path = str(folder_name),
            y_lim=1000) # Adds a x-axis in the top with the solar azimuth




if model_to_run1 != False:
    scat_index, fit_dict1 = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[0]), 
                 y_label = 'Measured',
                 x_label = 'Modelled',
                 modelled_value = POA1['POA fuel_in '+ str(side_of_panel)], 
                 measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                 #start_date = '2023-04-12 00:00:00', 
                 #end_date=end_date,
                 start_date = start_date, 
                 end_date= end_date,
                 solar_position= solar_position1,
                 interval='afternoon',
                 color_value= solar_position1['azimuth'],
                 y_lim = 1000,
                 model_to_run = model_to_run1,
                 model_explain= model_explain_scatter,
                 elevation_min= elevation_min1)  # False to have no lower bound on elevation
    plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[0]), dpi=300)
    
    if slope_adjust == True:
        POA_slope_adjust1 = POA1['POA fuel_in '+ str(side_of_panel)]*fit_dict1['slope']+fit_dict1['offset']
        scat_index, fit_dict1_ad = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[0])+' slope adjusted', 
                     y_label = 'Measured',
                     x_label = 'Modelled',
                     modelled_value = POA_slope_adjust1, 
                     measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                     #start_date = '2023-04-12 00:00:00', 
                     #end_date=end_date,
                     start_date = start_date, 
                     end_date=end_date,
                     solar_position= solar_position1,
                     interval='afternoon',
                     color_value= solar_position1['azimuth'],
                     y_lim = 1000,
                     model_to_run = model_to_run1,
                     model_explain= model_explain_scatter,
                     elevation_min= elevation_min1)  # False to have no lower bound on elevation
        plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[0])+'_slope_adjusted', dpi=300)


#POA_slope_adjust(slope = fit1.loc[0]['slope'],
             #    measured_value = data['Reference Cell Vertical West (W.m-2)'], 
              #   modelled_value = POA1['POA fuel_in West'])




if model_to_run2 != False:
    scat_index, fit_dict2 = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[1]), 
                 y_label = 'Measured',
                 x_label = 'Modelled',
                 modelled_value = POA2['POA fuel_in '+ str(side_of_panel)], 
                 measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                 #start_date = start_date, 
                 #end_date=end_date,
                 start_date = start_date, 
                 end_date=end_date,
                 solar_position= solar_position1,
                 interval='afternoon',
                 color_value= solar_position1['azimuth'],
                 y_lim = 1000,
                 model_to_run = model_to_run2,
                 model_explain= model_explain_scatter,
                 elevation_min= elevation_min1)  # False to have no lower bound on elevation
    plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[1]), dpi=300)

    if slope_adjust == True:
        POA_slope_adjust2 = POA2['POA fuel_in '+ str(side_of_panel)]*fit_dict2['slope']+ fit_dict2['offset']
        scat_index, fit_dict2_ad = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[1])+' slope adjusted', 
                     y_label = 'Measured',
                     x_label = 'Modelled',
                     modelled_value = POA_slope_adjust2, 
                     measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                     #start_date = start_date, 
                     #end_date=end_date,
                     start_date = start_date, 
                     end_date=end_date,
                     solar_position= solar_position1,
                     interval='afternoon',
                     color_value= solar_position1['azimuth'],
                     y_lim = 1000,
                     model_to_run = model_to_run1,
                     model_explain= model_explain_scatter,
                     elevation_min= elevation_min1)  # False to have no lower bound on elevation
        plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[1])+'_slope_adjusted', dpi=300)

if model_to_run3 != False:
    scat_index, fit_dict3 = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[2]), 
                 y_label = 'Measured',
                 x_label = 'Modelled',
                 modelled_value = POA3['POA fuel_in '+ str(side_of_panel)], 
                 measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                 #start_date = start_date, 
                 #end_date=end_date,
                 start_date = start_date, 
                 end_date=end_date,
                 solar_position= solar_position1,
                 interval='afternoon',
                 color_value= solar_position1['azimuth'],
                 y_lim = 1000,
                 model_to_run = model_to_run3,
                 model_explain= model_explain_scatter,
                 elevation_min= elevation_min1)  # False to have no lower bound on elevation
    plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[2]), dpi=300)

    if slope_adjust == True:
        POA_slope_adjust3 = POA3['POA fuel_in '+ str(side_of_panel)]*fit_dict3['slope']+fit_dict3['offset']
        scat_index, fit_dict3_ad = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[2])+' slope adjusted', 
                     y_label = 'Measured',
                     x_label = 'Modelled',
                     modelled_value = POA_slope_adjust3, 
                     measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                     #start_date = start_date, 
                     #end_date=end_date,
                     start_date = start_date, 
                     end_date=end_date,
                     solar_position= solar_position1,
                     interval='afternoon',
                     color_value= solar_position1['azimuth'],
                     y_lim = 1000,
                     model_to_run = model_to_run1,
                     model_explain= model_explain_scatter,
                     elevation_min= elevation_min1)  # False to have no lower bound on elevation
        plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[2])+'_slope_adjusted', dpi=300)

if model_to_run4 != False:
    scat_index, fit_dict4 = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[3]), 
                 y_label = 'Measured',
                 x_label = 'Modelled',
                 modelled_value = POA4['POA fuel_in '+ str(side_of_panel)], 
                 measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                 #start_date = start_date, 
                 #end_date=end_date,
                 start_date = start_date, 
                 end_date=end_date,
                 solar_position= solar_position1,
                 interval='afternoon',
                 color_value= solar_position1['azimuth'],
                 y_lim = 1000,
                 model_to_run = model_to_run4,
                 model_explain= model_explain_scatter,
                 elevation_min= elevation_min1)  # False to have no lower bound on elevation
    plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[3]), dpi=300)


    if slope_adjust == True:
        POA_slope_adjust4 = POA4['POA fuel_in '+ str(side_of_panel)]*fit_dict4['slope']+fit_dict4['offset']
        scat_index, fit_dict4_ad = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[3])+' slope adjusted', 
                     y_label = 'Measured',
                     x_label = 'Modelled',
                     modelled_value = POA_slope_adjust4, 
                     measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                     #start_date = start_date, 
                     #end_date=end_date,
                     start_date = start_date, 
                     end_date=end_date,
                     solar_position= solar_position1,
                     interval='afternoon',
                     color_value= solar_position1['azimuth'],
                     y_lim = 1000,
                     model_to_run = model_to_run1,
                     model_explain= model_explain_scatter,
                     elevation_min= elevation_min1)  # False to have no lower bound on elevation
        plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[3])+'_slope_adjusted', dpi=300)


#Build dataframe for the fit parameters of the different models 
if model_to_run3 ==False:
    fit_dict3 = {'nRMSE':np.nan,
                '# data points':np.nan,
                'R^2':np.nan,
                'slope':np.nan,
                'offset':np.nan} 
    
    fit_dict3_ad = {'nRMSE':np.nan,
                '# data points':np.nan,
                'R^2':np.nan,
                'slope':np.nan,
                'offset':np.nan}

if model_to_run4 ==False:
    fit_dict4 = {'nRMSE':np.nan,
                '# data points':np.nan,
                'R^2':np.nan,
                'slope':np.nan,
                'offset':np.nan} 
    
    fit_dict4_ad = {'nRMSE':np.nan,
                '# data points':np.nan,
                'R^2':np.nan,
                'slope':np.nan,
                'offset':np.nan}



fit1_dict = {
    'model': [str(custom_label[0])+str(side_of_panel),str(custom_label[1])+str(side_of_panel),str(custom_label[2])+str(side_of_panel), str(custom_label[3])+str(side_of_panel)],
    'number data': [fit_dict1['# data points'], fit_dict2['# data points'], fit_dict3['# data points'],fit_dict4['# data points']],
    'nRMSE': [fit_dict1['nRMSE'], fit_dict2['nRMSE'], fit_dict3['nRMSE'],fit_dict4['nRMSE']],
    'R^2': [fit_dict1['R^2'], fit_dict2['R^2'], fit_dict3['R^2'],fit_dict4['R^2']],
    'slope' : [fit_dict1['slope'], fit_dict2['slope'], fit_dict3['slope'],fit_dict4['slope']],
    'offset' : [fit_dict1['offset'], fit_dict2['offset'], fit_dict3['offset'],fit_dict4['offset']],
    'nRMSE_adjusted': [fit_dict1_ad['nRMSE'], fit_dict2_ad['nRMSE'], fit_dict3_ad['nRMSE'],fit_dict4_ad['nRMSE']]
    }

fit1=pd.DataFrame(fit1_dict)




model_variations = [model_to_run1, model_to_run2, model_to_run3, model_to_run4]

# Adjusting the file path for clarity
#csv_file_path_with_header = "./results/combined_data_with_header_and_explanations.csv"

#csv_file_path_with_header = './results/'+str(model_variation)+str(model_to_run1['mount_type'])+'.csv'
csv_file_path_with_header = str(folder_name)+'/fit_data'+str(side_of_panel)+'.csv'


# Since I can't directly run file operations or simulate the exact structure here, 
# the concept would involve iterating over both the DataFrame and the dictionaries
# Writing the CSV with the new header, dictionary explanations for each row, and DataFrame data

"""
with open(csv_file_path_with_header, 'w') as file:
    # Writing the header string
    header_string = f'Model variation {model_variation}'  # Assuming model_variation is defined
    file.write(f"{header_string}\n\n")
    
    for index, row in fit1.iterrows():
        model_dict = model_variations[index]
        # Writing dictionary explanations for the current row
        for key, value in model_dict.items():
            file.write(f"# {key}: {value}\n")
        # Writing the current row to the CSV
        row.to_csv(file, header=False, index=True)
        file.write("\n")  # Add a newline for separation if needed  
    
"""   
    
    


with open(csv_file_path_with_header, 'w') as file:
    # Writing the header string
    header_string = f'Model variation {model_variation}'  # Assuming model_variation is defined
    file.write(f"{header_string}\n\n")
    
    for index, row in fit1.iterrows():
        model_dict = model_variations[index]
        # Check if model_dict is a dictionary before iterating over its items
        if isinstance(model_dict, dict):
            # Writing dictionary explanations for the current row
            for key, value in model_dict.items():
                file.write(f"# {key}: {value}\n")
        else:
            # Handle the case where model_dict is not a dictionary
            # For now, we'll just write a placeholder or you can choose to skip/adjust as needed
            file.write("# model_dict is not a dictionary, skipping...\n")
        # Writing the current row to the CSV
        row.to_csv(file, header=False, index=True)
        file.write("\n")  # Add a newline for separation if needed  

#%%% The same plots for East
side_of_panel = other_side_of_panel


day_plot('POA '+ str(side_of_panel)+' - '+ str(model_variation)+' variation ' + str(model_to_run1['transposition']), 
            'Irradiance',
            value1 = POA1['POA fuel_in '+ str(side_of_panel)],
            value2 = POA2['POA fuel_in '+ str(side_of_panel)],
            value3 = POA3['POA fuel_in '+ str(side_of_panel)],
            value4 = POA4['POA fuel_in '+ str(side_of_panel)],
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            value5 = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'],
            days = sun_cloud_days,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            custom_label= custom_label,
            save_plots = True,
            path = str(folder_name),
            y_lim=1000) # Adds a x-axis in the top with the solar azimuth


if model_to_run1 != False:
    scat_index, fit_dict1 = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[0]), 
                 y_label = 'Measured',
                 x_label = 'Modelled',
                 modelled_value = POA1['POA fuel_in '+ str(side_of_panel)], 
                 measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                 #start_date = start_date, 
                 #end_date=end_date,
                 start_date = start_date, 
                 end_date=end_date,
                 solar_position= solar_position1,
                 interval='morning',
                 color_value= solar_position1['azimuth'],
                 y_lim = 1000,
                 model_to_run = model_to_run1,
                 model_explain= model_explain_scatter,
                 elevation_min= elevation_min1)  # False to have no lower bound on elevation
    plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[0]), dpi=300)

    if slope_adjust == True:
        POA_slope_adjust1 = POA1['POA fuel_in '+ str(side_of_panel)]*fit_dict1['slope']+fit_dict1['offset']
        scat_index, fit_dict1_ad = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[0])+' slope adjusted', 
                     y_label = 'Measured',
                     x_label = 'Modelled',
                     modelled_value = POA_slope_adjust1, 
                     measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                     #start_date = start_date, 
                     #end_date=end_date,
                     start_date = start_date, 
                     end_date=end_date,
                     solar_position= solar_position1,
                     interval='morning',
                     color_value= solar_position1['azimuth'],
                     y_lim = 1000,
                     model_to_run = model_to_run1,
                     model_explain= model_explain_scatter,
                     elevation_min= elevation_min1)  # False to have no lower bound on elevation
        plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[0])+'_slope_adjusted', dpi=300)


if model_to_run2 != False:
    scat_index, fit_dict2 = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[1]), 
                 y_label = 'Measured',
                 x_label = 'Modelled',
                 modelled_value = POA2['POA fuel_in '+ str(side_of_panel)], 
                 measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                 #start_date = start_date, 
                 #end_date=end_date,
                 start_date = start_date, 
                 end_date=end_date,
                 solar_position= solar_position1,
                 interval='morning',
                 color_value= solar_position1['azimuth'],
                 y_lim = 1000,
                 model_to_run = model_to_run2,
                 model_explain= model_explain_scatter,
                 elevation_min= elevation_min1)  # False to have no lower bound on elevation
    plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[1]), dpi=300)

    if slope_adjust == True:
        POA_slope_adjust2 = POA2['POA fuel_in '+ str(side_of_panel)]*fit_dict2['slope']+ fit_dict2['offset']
        scat_index, fit_dict2_ad = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[1])+' slope adjusted', 
                     y_label = 'Measured',
                     x_label = 'Modelled',
                     modelled_value = POA_slope_adjust2, 
                     measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                     #start_date = start_date, 
                     #end_date=end_date,
                     start_date = start_date, 
                     end_date=end_date,
                     solar_position= solar_position1,
                     interval='morning',
                     color_value= solar_position1['azimuth'],
                     y_lim = 1000,
                     model_to_run = model_to_run1,
                     model_explain= model_explain_scatter,
                     elevation_min= elevation_min1)  # False to have no lower bound on elevation
        plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[1])+'_slope_adjusted', dpi=300)


if model_to_run3 != False:
    scat_index, fit_dict3 = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[2]), 
                 y_label = 'Measured',
                 x_label = 'Modelled',
                 modelled_value = POA3['POA fuel_in '+ str(side_of_panel)], 
                 measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                 #start_date = start_date, 
                 #end_date=end_date,
                 start_date = start_date, 
                 end_date=end_date,
                 solar_position= solar_position1,
                 interval='morning',
                 color_value= solar_position1['azimuth'],
                 y_lim = 1000,
                 model_to_run = model_to_run3,
                 model_explain= model_explain_scatter,
                 elevation_min= elevation_min1)  # False to have no lower bound on elevation
    plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[2]), dpi=300)

    if slope_adjust == True:
        POA_slope_adjust3 = POA3['POA fuel_in '+ str(side_of_panel)]*fit_dict3['slope']+ fit_dict3['offset']
        scat_index, fit_dict3_ad = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[2])+' slope adjusted', 
                     y_label = 'Measured',
                     x_label = 'Modelled',
                     modelled_value = POA_slope_adjust3, 
                     measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                     #start_date = start_date, 
                     #end_date=end_date,
                     start_date = start_date, 
                     end_date=end_date,
                     solar_position= solar_position1,
                     interval='morning',
                     color_value= solar_position1['azimuth'],
                     y_lim = 1000,
                     model_to_run = model_to_run1,
                     model_explain= model_explain_scatter,
                     elevation_min= elevation_min1)  # False to have no lower bound on elevation
        plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[2])+'_slope_adjusted', dpi=300)

if model_to_run4 != False:
    scat_index, fit_dict4 = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[3]), 
                 y_label = 'Measured',
                 x_label = 'Modelled',
                 modelled_value = POA4['POA fuel_in '+ str(side_of_panel)], 
                 measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                 #start_date = start_date, 
                 #end_date=end_date,
                 start_date = start_date, 
                 end_date=end_date,
                 solar_position= solar_position1,
                 interval='morning',
                 color_value= solar_position1['azimuth'],
                 y_lim = 1000,
                 model_to_run = model_to_run4,
                 model_explain= model_explain_scatter,
                 elevation_min= elevation_min1)  # False to have no lower bound on elevation
    plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[3]), dpi=300)


    if slope_adjust == True:
        POA_slope_adjust4 = POA4['POA fuel_in '+ str(side_of_panel)]*fit_dict4['slope'] + fit_dict4['offset']
        scat_index, fit_dict4_ad = scatter_plot('Ref '+ str(side_of_panel)+' compare, ' + str(model_variation)+ ': ' +str(custom_label[3])+' slope adjusted', 
                     y_label = 'Measured',
                     x_label = 'Modelled',
                     modelled_value = POA_slope_adjust4, 
                     measured_value = data['Reference Cell Vertical '+ str(side_of_panel)+' (W.m-2)'], 
                     #start_date = start_date, 
                     #end_date=end_date,
                     start_date = start_date, 
                     end_date=end_date,
                     solar_position= solar_position1,
                     interval='morning',
                     color_value= solar_position1['azimuth'],
                     y_lim = 1000,
                     model_to_run = model_to_run1,
                     model_explain= model_explain_scatter,
                     elevation_min= elevation_min1)  # False to have no lower bound on elevation
        plt.savefig(str(folder_name)+'/'+'Ref_'+ str(side_of_panel)+'_compare_' + str(model_variation)+ '_' +str(custom_label[3])+'_slope_adjusted', dpi=300)


if model_to_run3 ==False:
    fit_dict3 = {'nRMSE':np.nan,
                '# data points':np.nan,
                'R^2':np.nan,
                'slope': np.nan,
                'offset':np.nan} 
    
    fit_dict3_ad = {'nRMSE':np.nan,
                '# data points':np.nan,
                'R^2':np.nan,
                'slope': np.nan,
                'offset':np.nan}

if model_to_run4 ==False:
    fit_dict4 = {'nRMSE':np.nan,
                '# data points':np.nan,
                'R^2':np.nan,
                'slope':np.nan,
                'offset':np.nan}
    
    fit_dict4_ad = {'nRMSE':np.nan,
                '# data points':np.nan,
                'R^2':np.nan,
                'slope':np.nan,
                'offset':np.nan}

fit2_dict = {
    'model': [str(custom_label[0])+str(side_of_panel),str(custom_label[1])+str(side_of_panel),str(custom_label[2])+str(side_of_panel), str(custom_label[3])+str(side_of_panel)],
    'number data': [fit_dict1['# data points'], fit_dict2['# data points'], fit_dict3['# data points'],fit_dict4['# data points']],
    'nRMSE': [fit_dict1['nRMSE'], fit_dict2['nRMSE'], fit_dict3['nRMSE'],fit_dict4['nRMSE']],
    'R^2': [fit_dict1['R^2'], fit_dict2['R^2'], fit_dict3['R^2'],fit_dict4['R^2']],
    'slope' : [fit_dict1['slope'], fit_dict2['slope'], fit_dict3['slope'],fit_dict4['slope']],
    'offset' : [fit_dict1['offset'], fit_dict2['offset'], fit_dict3['offset'],fit_dict4['offset']],
    'nRMSE_adjusted': [fit_dict1_ad['nRMSE'], fit_dict2_ad['nRMSE'], fit_dict3_ad['nRMSE'],fit_dict4_ad['nRMSE']]
    }

fit2=pd.DataFrame(fit2_dict)

csv_file_path_with_header = str(folder_name)+'/fit_data'+str(side_of_panel)+'.csv'

with open(csv_file_path_with_header, 'w') as file:
    # Writing the header string
    header_string = f'Model variation {model_variation}'  # Assuming model_variation is defined
    file.write(f"{header_string}\n\n")
    
    for index, row in fit2.iterrows():
        model_dict = model_variations[index]
        # Check if model_dict is a dictionary before iterating over its items
        if isinstance(model_dict, dict):
            # Writing dictionary explanations for the current row
            for key, value in model_dict.items():
                file.write(f"# {key}: {value}\n")
        else:
            # Handle the case where model_dict is not a dictionary
            # For now, we'll just write a placeholder or you can choose to skip/adjust as needed
            file.write("# model_dict is not a dictionary, skipping...\n")
        # Writing the current row to the CSV
        row.to_csv(file, header=False, index=True)
        file.write("\n")  # Add a newline for separation if needed  


#%%%

if model_variation == 'sensor':
    day_plot('GHI', 
                'Irradiance',
                value1 = data[('GHI (W.m-2)')],
                value2= data[('GHI_SPN1 (W.m-2)')],
                value3 = GHI1,
                value4 = GHI2,
                days = sun_cloud_days,
                model_explain= model_explain,
                solar_position = solar_position1['azimuth'],
                y_lines = y_lines,
                y_lim = 1000,
                save_plots = True,
                path = str(folder_name),
                custom_label= ['CMP6', 'SPN1', 'CMP6_interpolated','SPN1_interpolated',''])
    #plt.savefig(str(folder_name)+'/'+'GHI'+ str(model_variation), dpi=300)


if model_variation == 'DNI':
    day_plot('DNI', 
                'Irradiance [W.m-2]',
                value1 = dni1,
                value2 = dni2,
                value3 = dni3,
                value4 = dni4,
                days = sun_cloud_days,
                model_explain= model_explain,
                zoom = False,
                solar_position = solar_position1['azimuth'],
                y_lines = y_lines,
                y_lim = 1000,
                save_plots = True,
                path = str(folder_name),
                custom_label = custom_label)
    #plt.savefig(str(folder_name)+'/'+'DNI'+ str(model_variation), dpi=300)




  
"""
    
#Save the data in a csv file

# Placeholder header string (Please replace this with the actual header string you want)
header_string = 'Model variation '+str(model_variation)

# Adjusting the previous file path for clarity
csv_file_path_with_header = "./results/combined_data_with_header_and_explanations.csv"

# Writing the CSV with the new header, dictionary explanations, and DataFrame data
with open(csv_file_path_with_header, 'w') as file:
    # Writing the header string
    file.write(f"{header_string}\n\n")
    # Writing dictionary explanations
    for key, value in model_to_run1.items():
        file.write(f"# {key}: {value}\n")
    # Adding a separator/comment between explanations and data
    file.write("# Data Below\n")
    # Writing the DataFrame to the same file
    fit1.to_csv(file, index=False)

csv_file_path_with_header


"""   
  






#model_variations = [model_to_run1, model_to_run2, model_to_run3, model_to_run4]

# Adjusting the file path for clarity
#csv_file_path_with_header = "./results/combined_data_with_header_and_explanations.csv"

#csv_file_path_with_header = './results/'+str(model_variation)+str(model_to_run1['mount_type'])+'.csv'


#csv_file_path_with_header = str(folder_name)+'/fit_data'+str(side_of_panel)+'.csv'

"""
# Since I can't directly run file operations or simulate the exact structure here, 
# the concept would involve iterating over both the DataFrame and the dictionaries
# Writing the CSV with the new header, dictionary explanations for each row, and DataFrame data
with open(csv_file_path_with_header, 'w') as file:
    # Writing the header string
    header_string = f'Model variation {model_variation}'  # Assuming model_variation is defined
    file.write(f"{header_string}\n\n")
    
    for index, row in fit2.iterrows():
        model_dict = model_variations[index]
        # Writing dictionary explanations for the current row
        for key, value in model_dict.items():
            file.write(f"# {key}: {value}\n")
        # Writing the current row to the CSV
        row.to_csv(file, header=False, index=True)
        file.write("\n")  # Add a newline for separation if needed  
    
"""   
    
    
    
    
    








"""

day_plot('GHI', 
            'Irradiance',
            value1 = data[('GHI (W.m-2)')],
            value2= data[('GHI_SPN1 (W.m-2)')],
            value3 = GHI_inf1,
            value4 = GHI_inf2,
            days = sun_cloud_days,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            y_lim = 1000,
            custom_label= ['CMP6', 'SPN1', 'CMP6_interpolated','SPN1_interpolated',''])

"""















"""

GHI_CMP6 = pd.to_numeric(data[('GHI (W.m-2)')])
GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')])
GHI_2nd = pd.to_numeric(data[('GHI_2nd station (W.m-2)')])
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
Albedometer = pd.to_numeric(data[('Albedometer (W.m-2)')])


#Takes the average of the albedo when the solar elevation is above 10 deg and uses that average for the whole day
albedo = Albedometer/GHI_SPN1
albedo_fil = albedo[solar_position1['elevation']>10]
albedo_daily_mid_day_mean = albedo_fil.resample('D').mean()
albedo_daily = albedo_daily_mid_day_mean.reindex(albedo.index, method='ffill')


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

""" 

        






"""
import pandas as pd

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

# Ensure timezone information is consistent
#extended_datetime_index = extended_datetime_index.tz_localize('UTC')


# calculate Sun's coordinates
solar_position = location.get_solarposition(times=data.index) 

albedo_in_shadow = albedo_fil[(solar_position['azimuth']<290) & (solar_position['azimuth']>270)]
albedo_high = albedo_in_shadow[albedo_in_shadow>0.3].index
start_date = albedo_high[0]-pd.Timedelta(minutes=5)
end_date = albedo_high[-1]+pd.Timedelta(minutes=5)
start_diff = GHI_SPN1[start_date]-GHI_CMP6[start_date]
#GHI[start_date:end_date] = GHI_CMP6[start_date:end_date]
s=GHI_SPN1
for idx in extended_datetime_index:
        #s.loc[idx] = (s.loc[idx - pd.Timedelta(minutes=5)] + s.loc[idx + pd.Timedelta(minutes=5)]) / 2
        #s.loc[idx] = s.loc[idx-pd.Timedelta(minutes=5)] + ((s.loc[idx + pd.Timedelta(minutes=15)] - s.loc[idx + pd.Timedelta(minutes=5)]) /4 ) * 1
        s.loc[idx] = GHI_CMP6[idx] + start_diff
        GHI = s
        
"""     







