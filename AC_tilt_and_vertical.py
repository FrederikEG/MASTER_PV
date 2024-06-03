# -*- coding: utf-8 -*-
"""
Created on Sun May 26 09:49:39 2024

@author: frede
"""


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 
import pvlib
import numpy as np
from scipy.optimize import curve_fit
from POA_function_tilt_and_vertical import POA, POA_simple
from DC_output import DC_generation, DC_generation_temp_select, DC_generation_simple
from AC_output import AC_generation
from daily_plots import daily_plots
from daily_plots import day_plot, scatter_plot, solar_pos_scat, bar_plots, day_histo_plot, reg_line
from iam_custom import iam_custom, iam_custom_read, iam_custom_days
from sklearn.metrics import mean_squared_error
import math
from model_to_run_select import model_to_run_select, interval_select
from scipy.optimize import curve_fit



data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 

GHI_CMP6 = data[('GHI (W.m-2)')].copy()

tz='UTC' 


model_explain = False
model_explain_scatter = False
y_lines = True
filter_faulty=True #Filters out timestamps when the irradiance from ref cells or pyranometers are too high and therefore wrong
offset_correct = False #Corrects for the offset from 0 on SPN1 during night
slope_adjust = True
ref_cell_adjust = False

dpi_custom = 75

#start_date = '2023-04-12 00:00:00'
#end_date='2023-05-13 00:00:00'



# Calculating the time_index here overruels the start and end date
time_index_type = 'all_relevant'  # 'all_relevant'
time_index  = interval_select(time_index_type, data = data, filter_faulty=filter_faulty)



mount_type = 'Tilted'         # 'Tilted', 'Vertical'
model_variation = 'ACDC'         # 'DNI', 'sensor', 'transposition_simple', 'transposition_inf', 'IAM', 'spectrum'
temperature_model = 'sapm'      # 'sapm', 'PVsyst29', 'PVsyst56'

#Selects the transposition model from this face. Results are only true for this face 
trans_side = 'both_sides'   #  'Up', 'Down', 'East', 'West', 'both_sides'

interval_scat = 'afternoon' # 'false' when tilted. 'afternoon' with vertical. 'noon_exclude' also for tilted


if mount_type == 'Vertical':
    back_name = 'West'
    front_name = 'East'
    ref_front = data['Reference Cell Vertical East (W.m-2)'].copy()
    ref_back = data['Reference Cell Vertical West (W.m-2)'].copy()
    ref_global_with_bi = ref_front*0.8+ref_back
    plot_interval_front = 'morning'
    plot_interval_back = 'afternoon'
    y_lim = {'front': 1000,
             'back' : 1000}
    
    inverter_DC = data['INV-2-VBF Total input power (kW)']
    inverter_AC = data['INV-2-VBF Active power (kW)']
    grid_connect_index = data[data['VBF inverter status'] == 'Grid connected'].index
    
    AC_ref_row = data['VBF PV1 input voltage (V)'] * data['VBF PV1 input current (A)']

    
    if ref_cell_adjust == True:
        GHI_zero_index = GHI_CMP6[time_index][GHI_CMP6==0].index
        ref_front_offset = ref_front[GHI_zero_index].mean()
        ref_back_offset = ref_back[GHI_zero_index].mean()
        ref_front = ref_front - ref_front_offset
        ref_back = ref_back - ref_back_offset
    
elif mount_type=='Tilted':
    back_name = 'Down'
    front_name = 'Up'
    ref_front = data['Reference Cell Tilted facing up (W.m-2)'].copy()
    ref_back = data['Reference Cell Tilted facing down (W.m-2)'].copy()
    ref_global_with_bi = ref_front+ ref_back*0.8
    plot_interval_front = 'false'
    plot_interval_back = 'false'
    y_lim = {'front': 1200,
             'back' : 300}
    
    inverter_DC = data['INV-1-TBF Total input power (kW)']
    inverter_AC = data['INV-1-TBF Active power (kW)']
    grid_connect_index = data[data['TBF inverter status'] == 'Grid connected'].index
    
    AC_ref_row = data['TBF PV4 input voltage (V)'] * data['TBF PV4 input current (A)']
    
    if ref_cell_adjust == True:
        GHI_zero_index = GHI_CMP6[time_index][GHI_CMP6==0].index
        ref_front_offset = ref_front[GHI_zero_index].mean()
        ref_back_offset = ref_back[GHI_zero_index].mean()
        ref_front = ref_front - ref_front_offset
        ref_back = ref_back - ref_back_offset
    
    
side_of_panel = 'front'
other_side_of_panel = 'back'




    
    

#%%% Importing the model_to_run


model_to_run1, model_to_run2, model_to_run3, model_to_run4, PV_data, installation_data = model_to_run_select(model_variation= model_variation, mount_type=mount_type, trans_side= trans_side)



#%%% Create folder for the data 
from pathlib import Path

# Specify the name or path to the new directory
folder_name_DC = './results/DC_compare_'+str(mount_type)+'_interval_'+str(interval_scat)

# Create the directory; parents=True allows creating parent directories if needed, exist_ok=True avoids an error if the directory already exists
try:
    Path(folder_name_DC).mkdir(parents=True, exist_ok=True)
    print(f"Directory '{folder_name_DC}' created successfully")
except OSError as error:
    print(f"Creation of the directory '{folder_name_DC}' failed: {error}")



#%%% POA calculation


#For the simple transposition
if model_to_run1 != False and model_to_run1['transposition'] =='simple':
    POA_no_shad1, poa_no_shadow_east1, poa_no_shadow_west, GHI1, dni1, solar_position1, elevation_min1  = POA_simple(PV_data,
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
                      mount_type = model_to_run1['mount_type'],
                      offset_correct= offset_correct)
    
    
#For the simple transposition
if model_to_run2 != False and model_to_run2['transposition'] =='simple':
    POA_no_shad2, poa_no_shadow_east2, poa_no_shadow_west2, GHI2, dni2, solar_position2, elevation_min2  = POA_simple(PV_data,
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
                      mount_type = model_to_run1['mount_type'],
                      offset_correct= offset_correct)    
    
    
#For infinite sheds

if model_to_run1 != False and model_to_run1['transposition'] =='inf':
    POA1, solar_position1, albedo1, GHI_inf1, aoi_west1, aoi_east1, spec_loss1, poa_infinite_sheds1, albedo_daily1, dni_inf1, elevation_min1 = POA(PV_data,
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
    POA2, solar_position2, albedo2, GHI_inf2, aoi_west2, aoi_east2, spec_loss2, poa_infinite_sheds2, albedo_daily2, dni_inf2, elevation_min2 = POA(PV_data,
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
    
    
    
# Making the name of POA independent on the transposition method

if model_to_run1['transposition'] =='inf' and model_to_run2['transposition'] =='inf':
    POA1 = POA1
    POA2 = POA2
    POA_component_front = poa_infinite_sheds1
    POA_component_back = poa_infinite_sheds2
    POA_sky_diffuse_total = poa_infinite_sheds1['poa_front_sky_diffuse'] + poa_infinite_sheds2['poa_back_sky_diffuse']
    POA_ground_diffuse_total = poa_infinite_sheds1['poa_front_ground_sky_diffuse'] + poa_infinite_sheds2['poa_back_ground_sky_diffuse'] 
    POA_direct_total = poa_infinite_sheds1['poa_front_direct'] + poa_infinite_sheds2['poa_back_direct']
elif model_to_run1['transposition'] =='simple' and model_to_run2['transposition'] =='simple':
    POA1 = POA_no_shad1
    POA2 = POA_no_shad2
    POA_component_front = poa_no_shadow_east1
    POA_component_back = poa_no_shadow_west2
    POA_sky_diffuse_total = poa_no_shadow_east1['poa_sky_diffuse'] + poa_no_shadow_west2['poa_sky_diffuse']
    POA_ground_diffuse_total = poa_no_shadow_east1['poa_ground_diffuse'] + poa_no_shadow_west2['poa_ground_diffuse']
    POA_direct_total = poa_no_shadow_east1['poa_direct'] + poa_no_shadow_west2['poa_direct']
elif model_to_run1['transposition'] =='simple' and model_to_run2['transposition'] =='inf': 
        POA1 = POA_no_shad1
        POA2 = POA2
        POA_component_front = poa_no_shadow_east1
        POA_component_back = poa_infinite_sheds2
        POA_sky_diffuse_total = poa_no_shadow_east1['poa_sky_diffuse']  + poa_infinite_sheds2['poa_back_sky_diffuse']
        POA_ground_diffuse_total = poa_no_shadow_east1['poa_ground_diffuse'] + poa_infinite_sheds2['poa_back_ground_diffuse']
        POA_direct_total = poa_no_shadow_east1['poa_direct'] + poa_infinite_sheds2['poa_back_direct']
elif model_to_run1['transposition'] =='inf' and model_to_run2['transposition'] =='simple': 
        POA1 = POA1
        POA2 = POA_no_shad2
        POA_component_front = poa_infinite_sheds1
        POA_component_back = poa_no_shadow_west2
        POA_sky_diffuse_total = poa_infinite_sheds1['poa_front_sky_diffuse'] + poa_no_shadow_west2['poa_sky_diffuse']
        POA_ground_diffuse_total = poa_infinite_sheds1['poa_front_ground_sky_diffuse'] + poa_no_shadow_west2['poa_ground_diffuse']
        POA_direct_total = poa_infinite_sheds1['poa_front_direct'] + poa_no_shadow_west2['poa_direct']
        
    
    

    
    
#Global irradiance both sides    
POA_Global = POA1['POA front']+ POA2['POA back']
    
   #Applies the bifaciality to the right faces  
   #Combines the two model_to_run so the right transposition and IAM 
   # and spectral modifier are applied to the right faces 
if mount_type == 'Tilted':
    eff_front = POA1['POA fuel_in front']
    eff_back = POA2['POA fuel_in back'] * PV_data['bifaciality']
    eff_total = eff_front+eff_back
    G_with_bi = POA1['POA front']+ POA2['POA back']* PV_data['bifaciality']
    
    
    
elif mount_type == 'Vertical':
    eff_front = POA1['POA fuel_in front'] * PV_data['bifaciality'] #The east facing side
    eff_back = POA2['POA fuel_in back'] 
    eff_total = eff_front+eff_back
    G_with_bi = POA1['POA front'] * PV_data['bifaciality']+ POA2['POA back']
  
    #Calculating DC
dc_scaled1, dc_mid_rows1, temp_cell1, temp_air1  = DC_generation_simple(POA_Global, eff_total,
                          PV_data, 
                          installation_data, 
                          temp_sensor = model_to_run1['temp_sensor'],
                          wind_sensor= model_to_run1['wind_sensor'], 
                          inverter_limit = model_to_run1['inverter_limit'],
                          temperature_model = temperature_model) 


dc_scaled2, dc_mid_rows2, temp_cell2, temp_air2  = DC_generation_simple(POA_Global, eff_total,
                          PV_data, 
                          installation_data, 
                          temp_sensor = model_to_run1['temp_sensor'],
                          wind_sensor= model_to_run1['wind_sensor'], 
                          inverter_limit = model_to_run1['inverter_limit'],
                          temperature_model = 'PVsyst29') 

dc_scaled3, dc_mid_rows3, temp_cell3, temp_air3  = DC_generation_simple(POA_Global, eff_total,
                          PV_data, 
                          installation_data, 
                          temp_sensor = model_to_run1['temp_sensor'],
                          wind_sensor= model_to_run1['wind_sensor'], 
                          inverter_limit = model_to_run1['inverter_limit'],
                          temperature_model = 'PVsyst56') 

 
    
generation_DC1 = dc_scaled1['p_mp']
generation_DC2 = dc_scaled2['p_mp']
generation_DC3 = dc_scaled3['p_mp']

#Calculating AC
"""
AC = AC_generation(DC_generation = dc_scaled,
                   eff_irrad_total,
                   temp_cell,
                   temp_air,
                   inverter_CEC,
                   data,model):
"""


#Inverter from CEC
CEC_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')
inverter = CEC_inverters[installation_data['inverter']] # This is the US version - wrong voltage and maybe more

#AC output from inverter
AC_CEC1 = pvlib.inverter.sandia(v_dc = dc_scaled1.v_mp,
                                      p_dc = dc_scaled1.p_mp,
                                      inverter=inverter)



    


generation_AC_tilted = AC_CEC1


#%%%    Vertical installation



mount_type = 'Vertical'         # 'Tilted', 'Vertical'
model_variation = 'ACDC'         # 'DNI', 'sensor', 'transposition_simple', 'transposition_inf', 'IAM', 'spectrum'
temperature_model = 'sapm'      # 'sapm', 'PVsyst29', 'PVsyst56'

#Selects the transposition model from this face. Results are only true for this face 
trans_side = 'both_sides'   #  'Up', 'Down', 'East', 'West', 'both_sides'

interval_scat = 'afternoon' # 'false' when tilted. 'afternoon' with vertical. 'noon_exclude' also for tilted


if mount_type == 'Vertical':
    back_name = 'West'
    front_name = 'East'
    ref_front = data['Reference Cell Vertical East (W.m-2)'].copy()
    ref_back = data['Reference Cell Vertical West (W.m-2)'].copy()
    ref_global_with_bi = ref_front*0.8+ref_back
    plot_interval_front = 'morning'
    plot_interval_back = 'afternoon'
    y_lim = {'front': 1000,
             'back' : 1000}
    
    inverter_DC = data['INV-2-VBF Total input power (kW)']
    inverter_AC = data['INV-2-VBF Active power (kW)']
    grid_connect_index = data[data['VBF inverter status'] == 'Grid connected'].index
    
    AC_ref_row = data['VBF PV1 input voltage (V)'] * data['VBF PV1 input current (A)']

    
    if ref_cell_adjust == True:
        GHI_zero_index = GHI_CMP6[time_index][GHI_CMP6==0].index
        ref_front_offset = ref_front[GHI_zero_index].mean()
        ref_back_offset = ref_back[GHI_zero_index].mean()
        ref_front = ref_front - ref_front_offset
        ref_back = ref_back - ref_back_offset
    
elif mount_type=='Tilted':
    back_name = 'Down'
    front_name = 'Up'
    ref_front = data['Reference Cell Tilted facing up (W.m-2)'].copy()
    ref_back = data['Reference Cell Tilted facing down (W.m-2)'].copy()
    ref_global_with_bi = ref_front+ ref_back*0.8
    plot_interval_front = 'false'
    plot_interval_back = 'false'
    y_lim = {'front': 1200,
             'back' : 300}
    
    inverter_DC = data['INV-1-TBF Total input power (kW)']
    inverter_AC = data['INV-1-TBF Active power (kW)']
    grid_connect_index = data[data['TBF inverter status'] == 'Grid connected'].index
    
    AC_ref_row = data['TBF PV4 input voltage (V)'] * data['TBF PV4 input current (A)']
    
    if ref_cell_adjust == True:
        GHI_zero_index = GHI_CMP6[time_index][GHI_CMP6==0].index
        ref_front_offset = ref_front[GHI_zero_index].mean()
        ref_back_offset = ref_back[GHI_zero_index].mean()
        ref_front = ref_front - ref_front_offset
        ref_back = ref_back - ref_back_offset
    
    
side_of_panel = 'front'
other_side_of_panel = 'back'




    
    

#%%% Importing the model_to_run


model_to_run1, model_to_run2, model_to_run3, model_to_run4, PV_data, installation_data = model_to_run_select(model_variation= model_variation, mount_type=mount_type, trans_side= trans_side)



#%%% Create folder for the data 
from pathlib import Path

# Specify the name or path to the new directory
folder_name_DC = './results/DC_compare_'+str(mount_type)+'_interval_'+str(interval_scat)

# Create the directory; parents=True allows creating parent directories if needed, exist_ok=True avoids an error if the directory already exists
try:
    Path(folder_name_DC).mkdir(parents=True, exist_ok=True)
    print(f"Directory '{folder_name_DC}' created successfully")
except OSError as error:
    print(f"Creation of the directory '{folder_name_DC}' failed: {error}")



#%%% POA calculation


#For the simple transposition
if model_to_run1 != False and model_to_run1['transposition'] =='simple':
    POA_no_shad1, poa_no_shadow_east1, poa_no_shadow_west, GHI1, dni1, solar_position1, elevation_min1  = POA_simple(PV_data,
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
                      mount_type = model_to_run1['mount_type'],
                      offset_correct= offset_correct)
    
    
#For the simple transposition
if model_to_run2 != False and model_to_run2['transposition'] =='simple':
    POA_no_shad2, poa_no_shadow_east2, poa_no_shadow_west2, GHI2, dni2, solar_position2, elevation_min2  = POA_simple(PV_data,
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
                      mount_type = model_to_run1['mount_type'],
                      offset_correct= offset_correct)    
    
    
#For infinite sheds

if model_to_run1 != False and model_to_run1['transposition'] =='inf':
    POA1, solar_position1, albedo1, GHI_inf1, aoi_west1, aoi_east1, spec_loss1, poa_infinite_sheds1, albedo_daily1, dni_inf1, elevation_min1 = POA(PV_data,
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
    POA2, solar_position2, albedo2, GHI_inf2, aoi_west2, aoi_east2, spec_loss2, poa_infinite_sheds2, albedo_daily2, dni_inf2, elevation_min2 = POA(PV_data,
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
    
    
    
# Making the name of POA independent on the transposition method

if model_to_run1['transposition'] =='inf' and model_to_run2['transposition'] =='inf':
    POA1 = POA1
    POA2 = POA2
    POA_component_front = poa_infinite_sheds1
    POA_component_back = poa_infinite_sheds2
    POA_sky_diffuse_total = poa_infinite_sheds1['poa_front_sky_diffuse'] + poa_infinite_sheds2['poa_back_sky_diffuse']
    POA_ground_diffuse_total = poa_infinite_sheds1['poa_front_ground_sky_diffuse'] + poa_infinite_sheds2['poa_back_ground_sky_diffuse'] 
    POA_direct_total = poa_infinite_sheds1['poa_front_direct'] + poa_infinite_sheds2['poa_back_direct']
elif model_to_run1['transposition'] =='simple' and model_to_run2['transposition'] =='simple':
    POA1 = POA_no_shad1
    POA2 = POA_no_shad2
    POA_component_front = poa_no_shadow_east1
    POA_component_back = poa_no_shadow_west2
    POA_sky_diffuse_total = poa_no_shadow_east1['poa_sky_diffuse'] + poa_no_shadow_west2['poa_sky_diffuse']
    POA_ground_diffuse_total = poa_no_shadow_east1['poa_ground_diffuse'] + poa_no_shadow_west2['poa_ground_diffuse']
    POA_direct_total = poa_no_shadow_east1['poa_direct'] + poa_no_shadow_west2['poa_direct']
elif model_to_run1['transposition'] =='simple' and model_to_run2['transposition'] =='inf': 
        POA1 = POA_no_shad1
        POA2 = POA2
        POA_component_front = poa_no_shadow_east1
        POA_component_back = poa_infinite_sheds2
        POA_sky_diffuse_total = poa_no_shadow_east1['poa_sky_diffuse']  + poa_infinite_sheds2['poa_back_sky_diffuse']
        POA_ground_diffuse_total = poa_no_shadow_east1['poa_ground_diffuse'] + poa_infinite_sheds2['poa_back_ground_diffuse']
        POA_direct_total = poa_no_shadow_east1['poa_direct'] + poa_infinite_sheds2['poa_back_direct']
elif model_to_run1['transposition'] =='inf' and model_to_run2['transposition'] =='simple': 
        POA1 = POA1
        POA2 = POA_no_shad2
        POA_component_front = poa_infinite_sheds1
        POA_component_back = poa_no_shadow_west2
        POA_sky_diffuse_total = poa_infinite_sheds1['poa_front_sky_diffuse'] + poa_no_shadow_west2['poa_sky_diffuse']
        POA_ground_diffuse_total = poa_infinite_sheds1['poa_front_ground_sky_diffuse'] + poa_no_shadow_west2['poa_ground_diffuse']
        POA_direct_total = poa_infinite_sheds1['poa_front_direct'] + poa_no_shadow_west2['poa_direct']
        
    
    

    
    
#Global irradiance both sides    
POA_Global = POA1['POA front']+ POA2['POA back']
    
   #Applies the bifaciality to the right faces  
   #Combines the two model_to_run so the right transposition and IAM 
   # and spectral modifier are applied to the right faces 
if mount_type == 'Tilted':
    eff_front = POA1['POA fuel_in front']
    eff_back = POA2['POA fuel_in back'] * PV_data['bifaciality']
    eff_total = eff_front+eff_back
    G_with_bi = POA1['POA front']+ POA2['POA back']* PV_data['bifaciality']
    
    
    
elif mount_type == 'Vertical':
    eff_front = POA1['POA fuel_in front'] * PV_data['bifaciality'] #The east facing side
    eff_back = POA2['POA fuel_in back'] 
    eff_total = eff_front+eff_back
    G_with_bi = POA1['POA front'] * PV_data['bifaciality']+ POA2['POA back']
  
    #Calculating DC
dc_scaled1, dc_mid_rows1, temp_cell1, temp_air1  = DC_generation_simple(POA_Global, eff_total,
                          PV_data, 
                          installation_data, 
                          temp_sensor = model_to_run1['temp_sensor'],
                          wind_sensor= model_to_run1['wind_sensor'], 
                          inverter_limit = model_to_run1['inverter_limit'],
                          temperature_model = temperature_model) 


dc_scaled2, dc_mid_rows2, temp_cell2, temp_air2  = DC_generation_simple(POA_Global, eff_total,
                          PV_data, 
                          installation_data, 
                          temp_sensor = model_to_run1['temp_sensor'],
                          wind_sensor= model_to_run1['wind_sensor'], 
                          inverter_limit = model_to_run1['inverter_limit'],
                          temperature_model = 'PVsyst29') 

dc_scaled3, dc_mid_rows3, temp_cell3, temp_air3  = DC_generation_simple(POA_Global, eff_total,
                          PV_data, 
                          installation_data, 
                          temp_sensor = model_to_run1['temp_sensor'],
                          wind_sensor= model_to_run1['wind_sensor'], 
                          inverter_limit = model_to_run1['inverter_limit'],
                          temperature_model = 'PVsyst56') 

 
    
generation_DC1 = dc_scaled1['p_mp']
generation_DC2 = dc_scaled2['p_mp']
generation_DC3 = dc_scaled3['p_mp']

#Calculating AC
"""
AC = AC_generation(DC_generation = dc_scaled,
                   eff_irrad_total,
                   temp_cell,
                   temp_air,
                   inverter_CEC,
                   data,model):
"""


#Inverter from CEC
CEC_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')
inverter = CEC_inverters[installation_data['inverter']] # This is the US version - wrong voltage and maybe more

#AC output from inverter
AC_CEC1 = pvlib.inverter.sandia(v_dc = dc_scaled1.v_mp,
                                      p_dc = dc_scaled1.p_mp,
                                      inverter=inverter)



    


generation_AC_vertical = AC_CEC1




#%%% PLots


sun_cloud_days_ACDC = ['2023-05-11 00:00:00', '2023-05-12 00:00:00']



day_plot('AC power generation - modelled and measured', 
            'AC power (kW)',
            value1 = generation_AC_tilted*0.001,
            value2 = generation_AC_vertical*0.001,
            value3 = data['INV-1-TBF Active power (kW)'],
            value4 = data['INV-2-VBF Active power (kW)'],
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days_ACDC,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            save_plots = False,
            custom_label= ['AC tilted modelled','AC vertical modelled','AC tilted measured','AC vertical measured',''],
            y_lim = 40)
