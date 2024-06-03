# -*- coding: utf-8 -*-
"""
Created on Sun May 12 13:55:17 2024

@author: frede
"""

# -*- coding: utf-8 -*-
"""
Created on Sun May  5 14:08:30 2024

@author: frede
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 11:07:13 2024

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
from daily_plots import day_plot, scatter_plot, solar_pos_scat, bar_plots, day_histo_plot, reg_line, day_plot_6_1
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
    fuel_in_total = POA1['POA fuel_in front'] + POA2['POA fuel_in back'] 
    fuel_in_front = POA1['POA fuel_in front']
    fuel_in_back = POA2['POA fuel_in back']
    
    
elif mount_type == 'Vertical':
    eff_front = POA1['POA fuel_in front'] * PV_data['bifaciality'] #The east facing side
    eff_back = POA2['POA fuel_in back'] 
    eff_total = eff_front+eff_back
    G_with_bi = POA1['POA front'] * PV_data['bifaciality']+ POA2['POA back']
    fuel_in_total = POA1['POA fuel_in front'] + POA2['POA fuel_in back'] 
    fuel_in_front = POA1['POA fuel_in front']
    fuel_in_back = POA2['POA fuel_in back']
  
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



    


generation_AC1 = AC_CEC1

#%%% Plots

sun_cloud_days = ['2023-05-12 00:00:00', '2023-05-17 00:00:00']

sun_cloud_days_ACDC = ['2023-05-11 00:00:00', '2023-05-12 00:00:00']

snow_days = ['2023-12-01 00:00:00', '2023-12-02 00:00:00']


# The datetimeindex for the scatter plot should be adjusted to only include 
# times when the inverter is working (grid connected)


# Finding the intersection
common_index = time_index.intersection(grid_connect_index)
common_grid_connect = time_index.intersection(grid_connect_index)


day_plot('DC generation ' + str(mount_type) + ' installation', 
            'DC power (kW)',
            value1 = generation_DC1*0.001,
            value2 = generation_DC2*0.001,
            value3 = generation_DC3*0.001,
            value4 = inverter_DC,
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days_ACDC,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            custom_label= ['SAPM','PVsyst29','PVsyst56','Inverter_DC',''],
            y_lim = 40)


"""
day_plot('DC generation ' + str(mount_type) + ' installation', 
            'DC power (kW)',
            value1 = inverter_DC,
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            custom_label= ['Inverter_DC','PVsyst29','PVsyst56','Inverter_DC',''],
            y_lim = 40)

"""



ACDC_generation = pd.DataFrame({'DC': generation_DC1, 'AC': generation_AC1})

ACDC_inverter = pd.DataFrame({'DC': inverter_DC, 'AC': inverter_AC})

"""
for i in ['DC', 'AC']:
    
    custom_label = [str(i)+' generation', str(i) + ' inverter', '', '', '']
    
    day_plot(str(i) +' generation ' + str(mount_type) + ' installation', 
                str(i) + ' power (kW)',
                value1 = ACDC_generation[i]*0.001,
                value2 = ACDC_inverter[i],
                #value5 = data['Reference Cell Vertical West (W.m-2)'],
                days = sun_cloud_days,
                model_explain= model_explain,
                solar_position = solar_position1['azimuth'],
                y_lines = y_lines,
                custom_label= custom_label,
                y_lim = 40)
    
    
    scat_index1, fit_dict1 = scatter_plot(str(i)+' generation compare ' + str(mount_type)+ ' installation', 
                y_label = 'Measured power (kW)',
                x_label = 'Modelled power (kW)',
                modelled_value = ACDC_generation[i]*0.001, 
                measured_value = ACDC_inverter[i], 
                #start_date = '2023-04-12 00:00:00', 
                #end_date=end_date,
                #start_date = start_date, 
                #end_date= end_date,
                time_index= common_index,
                solar_position= solar_position1,
                #solar_position= False,
                interval='afternoon',
                color_value= solar_position1['azimuth'],
                y_lim = 40,
                model_to_run = model_to_run1,
                model_explain= model_explain_scatter,
                elevation_min= elevation_min1)  # False to have no lower bound on elevation
   #plt.savefig(str(folder_name)+'/'+'Ref_'+ str(front_name)+'_compare_' + str(model_variation)+ '_' +str(custom_label[0]), dpi=300)


    if slope_adjust == True:
       ACDC_slope_adjust1 = (ACDC_generation[i]*fit_dict1['slope'])*0.001+fit_dict1['offset']
       scat_index, fit_dict1_ad = scatter_plot(str(i)+' generation compare ' + str(mount_type)+ ' installation adjusted', 
                    y_label = 'Measured power (kW)',
                    x_label = 'Modelled power (kW)',
                    modelled_value = ACDC_slope_adjust1, 
                    measured_value = ACDC_inverter[i], 
                    #start_date = '2023-04-12 00:00:00', 
                    #end_date=end_date,
                    time_index= scat_index1,
                    #start_date = start_date, 
                    #end_date=end_date,
                    #solar_position= False,
                    solar_position= solar_position1,
                    interval='afternoon',
                    color_value= solar_position1['azimuth'],
                    y_lim = 40,
                    model_to_run = model_to_run1,
                    model_explain= model_explain_scatter,
                    elevation_min= elevation_min1)  # False to have no lower bound on elevation
       #plt.savefig(str(folder_name)+'/'+'Ref_'+ str(front_name)+'_compare_' + str(model_variation)+ '_' +str(custom_label[0])+'_slope_adjusted', dpi=300)
 
    
 
    
""" 
    
 
    
 
#DC1
scat_index1, fit_dict1 = scatter_plot('DC generation compare ' + str(mount_type)+ ' installation \n temp model: SAPM' , 
             y_label = 'Measured power (kW)',
             x_label = 'Modelled power (kW)',
             modelled_value = generation_DC1*0.001, 
             measured_value = inverter_DC, 
             #start_date = '2023-04-12 00:00:00', 
             #end_date=end_date,
             #start_date = start_date, 
             #end_date= end_date,
             time_index= common_index,
             solar_position= solar_position1,
             #solar_position= False,
             interval=interval_scat,
             color_value= solar_position1['azimuth'],
             y_lim = 40,
             model_to_run = model_to_run1,
             model_explain= model_explain_scatter,
             elevation_min= elevation_min1)  # False to have no lower bound on elevation
plt.savefig(str(folder_name_DC)+'/'+'SAPM', dpi=dpi_custom)
 
if slope_adjust == True:
   DC_slope_adjust1 = (generation_DC1*fit_dict1['slope'])*0.001+fit_dict1['offset']
   scat_index, fit_dict1_ad = scatter_plot('DC generation compare ' + str(mount_type)+ ' installation \n temp model: SAPM. Adjusted', 
                y_label = 'Measured power (kW)',
                x_label = 'Modelled power (kW)',
                modelled_value = DC_slope_adjust1, 
                measured_value = inverter_DC, 
                #start_date = '2023-04-12 00:00:00', 
                #end_date=end_date,
                time_index= common_index,
                #start_date = start_date, 
                #end_date=end_date,
                #solar_position= False,
                solar_position= solar_position1,
                interval=interval_scat,
                color_value= solar_position1['azimuth'],
                y_lim = 40,
                model_to_run = model_to_run1,
                model_explain= model_explain_scatter,
                elevation_min= elevation_min1)  # False to have no lower bound on elevation
   plt.savefig(str(folder_name_DC)+'/'+'SAPM_adjust', dpi=dpi_custom)
   
#DC 2
scat_index1, fit_dict1 = scatter_plot('DC generation compare ' + str(mount_type)+ ' installation \n temp model: PVsyst29' , 
             y_label = 'Measured power (kW)',
             x_label = 'Modelled power (kW)',
             modelled_value = generation_DC2*0.001, 
             measured_value = inverter_DC, 
             #start_date = '2023-04-12 00:00:00', 
             #end_date=end_date,
             #start_date = start_date, 
             #end_date= end_date,
             time_index= common_index,
             solar_position= solar_position1,
             #solar_position= False,
             interval=interval_scat,
             color_value= solar_position1['azimuth'],
             y_lim = 40,
             model_to_run = model_to_run1,
             model_explain= model_explain_scatter,
             elevation_min= elevation_min1)  # False to have no lower bound on elevation
plt.savefig(str(folder_name_DC)+'/'+'PVsyst29', dpi=dpi_custom)

if slope_adjust == True:
   DC_slope_adjust2 = (generation_DC2*fit_dict1['slope'])*0.001+fit_dict1['offset']
   scat_index, fit_dict1_ad = scatter_plot('DC generation compare ' + str(mount_type)+ ' installation \n temp model: PVsys29. Adjusted', 
                y_label = 'Measured power (kW)',
                x_label = 'Modelled power (kW)',
                modelled_value = DC_slope_adjust2, 
                measured_value = inverter_DC, 
                #start_date = '2023-04-12 00:00:00', 
                #end_date=end_date,
                time_index= common_index,
                #start_date = start_date, 
                #end_date=end_date,
                #solar_position= False,
                solar_position= solar_position1,
                interval=interval_scat,
                color_value= solar_position1['azimuth'],
                y_lim = 40,
                model_to_run = model_to_run1,
                model_explain= model_explain_scatter,
                elevation_min= elevation_min1)  # False to have no lower bound on elevation
   plt.savefig(str(folder_name_DC)+'/'+'PVsyst29_adjust', dpi=dpi_custom)






#DC3
scat_index1, fit_dict1 = scatter_plot('DC generation compare ' + str(mount_type)+ ' installation \n temp model: PVsyst56' , 
             y_label = 'Measured power (kW)',
             x_label = 'Modelled power (kW)',
             modelled_value = generation_DC3*0.001, 
             measured_value = inverter_DC, 
             #start_date = '2023-04-12 00:00:00', 
             #end_date=end_date,
             #start_date = start_date, 
             #end_date= end_date,
             time_index= common_index,
             solar_position= solar_position1,
             #solar_position= False,
             interval=interval_scat,
             color_value= solar_position1['azimuth'],
             y_lim = 40,
             model_to_run = model_to_run1,
             model_explain= model_explain_scatter,
             elevation_min= elevation_min1)  # False to have no lower bound on elevation
plt.savefig(str(folder_name_DC)+'/'+'PVsyst56', dpi=dpi_custom)

if slope_adjust == True:
   DC_slope_adjust3 = (generation_DC3*fit_dict1['slope'])*0.001+fit_dict1['offset']
   scat_index, fit_dict1_ad = scatter_plot('DC generation compare ' + str(mount_type)+ ' installation \n temp model: PVsyst56. Adjusted', 
                y_label = 'Measured power (kW)',
                x_label = 'Modelled power (kW)',
                modelled_value = DC_slope_adjust3, 
                measured_value = inverter_DC, 
                #start_date = '2023-04-12 00:00:00', 
                #end_date=end_date,
                time_index= common_index,
                #start_date = start_date, 
                #end_date=end_date,
                #solar_position= False,
                solar_position= solar_position1,
                interval=interval_scat,
                color_value= solar_position1['azimuth'],
                y_lim = 40,
                model_to_run = model_to_run1,
                model_explain= model_explain_scatter,
                elevation_min= elevation_min1)  # False to have no lower bound on elevation
   plt.savefig(str(folder_name_DC)+'/'+'PVsyst56_adjust', dpi=dpi_custom)







    
#Inverter efficiency

inverter_efficiency = (inverter_AC/inverter_DC)*100
inverter_efficiency_calc = (generation_AC1/generation_DC1)*100

fig1, ax1= plt.subplots()
fig1.suptitle('Inverter efficiency')
#ax1.scatter(POA_Global[common_index], inverter_efficiency[common_index],alpha=0.1, label='Original Data')
#ax1.scatter(POA_Global[common_index], inverter_efficiency_calc[common_index],alpha=0.5, label='calculated')
#ax1.scatter(x_inverter_efficiency,inverter_efficiency_grid_connect,alpha=0.5,label='Sandia model')
#ax1.scatter(x_inv_eff,inv_eff, color='red',alpha=0.5,label='Modelled inverter efficiency')
#ax1.plot(x_fit1, y_fit1, 'g-',linewidth=2, label='Log fit')
ax1.set(ylabel='Efficiency [%]')
ax1.set(xlabel='Effective irradiance [W/m2]')
ax1.set_ylim([30,105])
ax1.set_xlim([0,1200])
sc = ax1.scatter(eff_total[common_index], inverter_efficiency[common_index],c = temp_air1[common_index], cmap = 'jet',alpha=0.5)       
cbar = plt.colorbar(sc)
cbar.set_label('temp_air', fontsize=12)
ax1.scatter(eff_total[common_index], inverter_efficiency_calc[common_index],alpha=0.5, color='black', label='calculated')
ax1.legend()    
plt.grid()
plt.savefig(str(folder_name_DC)+'/'+'Inverter_efficiency', dpi=dpi_custom)



"""
scat_index1, fit_dict1 = scatter_plot(str(i)+' generation compare ' + str(mount_type)+ ' installation', 
         y_label = 'Efficiency (%)',
         x_label = 'Effective irradiance (W.m-2) total',
         modelled_value = POA_Global, 
         measured_value = inverter_efficiency, 
         #start_date = '2023-04-12 00:00:00', 
         #end_date=end_date,
         #start_date = start_date, 
         #end_date= end_date,
         time_index= common_index,
         #solar_position= solar_position1,
         solar_position= False,
         interval='false',
         color_value= solar_position1['azimuth'],
         model_to_run = model_to_run1,
         model_explain= model_explain_scatter,
         elevation_min= False)  # False to have no lower bound on elevation
#plt.savefig(str(folder_name)+'/'+'Ref_'+ str(front_name)+'_compare_' + str(model_variation)+ '_' +str(custom_label[0]), dpi=300)
"""


"""
time_index_test = pd.date_range(start='2023-05-12', 
                       periods=24*12*1, 
                       freq='5min',
                       tz=tz)

x_data = POA['POA Global'][scat_index1]
y_data = inverter_efficiency[scat_index1]
    
#Filters out times where either modelled of measured or both are nan
no_nan_or_inf_indices = x_data.notna() & y_data.notna() & np.isfinite(x_data) & np.isfinite(y_data)
x_data = x_data[no_nan_or_inf_indices]
y_data = y_data[no_nan_or_inf_indices]


def logarithmic_func1(x, a, b):
   return a + b * np.log(x)



popt, pcov = curve_fit(logarithmic_func1, x_data, y_data,maxfev=10000)


a_opt1, b_opt1 = popt



x_fit1 = np.linspace(min(x_data), max(x_data), 100)  # Generate x-values for the fitted curve
y_fit1 = logarithmic_func1(x_fit1, a_opt1, b_opt1)  # Evaluate the fitted curve



def custom_function(series_input):
    # Apply the custom function to each element of the Series
    series_output = series_input.apply(lambda x: logarithmic_func1(x, a_opt1, b_opt1) if 0 <= x <= 300 else 98.4)

    return series_output   



def invert_log_function(eff_irrad,inverter_eff,p_dc1):
   inv_eff1 = ((8*(custom_function(eff_irrad))+2*(inverter_eff*100))/10)/100
   p_ac = inv_eff1*p_dc1
   #if p_ac>40000:
    #   return 40000
   #else:
   return p_ac


p_custom = invert_log_function(POA['POA Global'],inverter_efficiency_calc,generation_DC1)


AC_custom = AC_generation(DC_generation = dc_scaled,
                          eff_irrad_total = POA['POA Global'],
                          temp_cell = temp_cell,
                          temp_air = temp_air,
                          inverter_CEC = inverter,
                          data = data,
                          model = 'custom', 
                          common_index = common_index)

"""
#%%% Efficiency of the installations

area = PV_data['module_width']*PV_data['module_height']*installation_data['modules_per_string']*installation_data['strings_per_inverter']
#eta_with_bi = ((inverter_AC*1000)/ (G_with_bi * area))*100
eta_with_bi = ((inverter_AC*1000)/ (eff_total * area))*100
eta = ((inverter_AC*1000)/ (POA_Global * area))*100

eta_measure =  ((inverter_AC*1000)/ (ref_global_with_bi * area))*100

eta_ref_row_DC = ((AC_ref_row)/ (ref_global_with_bi * (area/4)))*100

# Calculating the time_index here overruels the start and end date
time_index_type = 'all_relevant'
time_index  = interval_select(time_index_type, data = data, filter_faulty=filter_faulty)



time_index_type1 = 'interval1'
time_index1  = interval_select(time_index_type1, data = data, filter_faulty=filter_faulty)
# Finding the intersection
common_time_index1 = time_index1.intersection(grid_connect_index)
common_time_index1_grid = time_index1.intersection(grid_connect_index)


time_index_type2 = 'interval2'
time_index2  = interval_select(time_index_type2, data = data, filter_faulty=filter_faulty)
# Finding the intersection
common_time_index2 = time_index2.intersection(grid_connect_index)
common_time_index2_grid = time_index2.intersection(grid_connect_index)

time_index_type3 = 'interval3'
time_index3  = interval_select(time_index_type3, data = data, filter_faulty=filter_faulty)
# Finding the intersection
common_time_index3 = time_index3.intersection(grid_connect_index)
common_time_index3_grid = time_index3.intersection(grid_connect_index)

time_index_type4 = 'interval4'
time_index4  = interval_select(time_index_type4, data = data, filter_faulty=filter_faulty)
# Finding the intersection
common_time_index4 = time_index4.intersection(grid_connect_index)
common_time_index4_grid = time_index4.intersection(grid_connect_index)


continuous_time = range(len(common_index))
eta_lim = 50

time_index1_date = common_time_index1.strftime('%Y-%m-%d')
time_index2_date = common_time_index2.strftime('%Y-%m-%d')
time_index3_date = common_time_index3.strftime('%Y-%m-%d')
time_index4_date = common_time_index4.strftime('%Y-%m-%d')

fig1, ax1 = plt.subplots()
fig1.suptitle('Efficiency of ' + str(mount_type) + ' installation with modelled POA irradiance')
ax1.plot(continuous_time,eta_with_bi[common_index],label='Efficiency')
#ax1.set(xlabel = 'Day in the year')
ax1.set(ylabel = 'Efficiency (%)')
ax1.set_ylim([0,eta_lim])
ax1.axvline(continuous_time[len(common_time_index1)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(common_time_index1)+ len(common_time_index2)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(common_time_index1)+ len(common_time_index2) + len(common_time_index3)], color='black', linestyle = '--')
ax1.set_xticks([])  # This removes x-ticks from the plot
ax1.text(continuous_time[len(time_index1_date)]/2, -0.1*eta_lim, str(time_index1_date[0])+ '\n' + time_index1_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + round((len(common_time_index2))/2)] , -0.1*eta_lim, str(time_index2_date[0])+ '\n' + time_index2_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(common_time_index2) + round((len(common_time_index3))/2)], -0.1*eta_lim, str(time_index3_date[0])+ '\n' + time_index3_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(common_time_index2) + len(common_time_index3) + round((len(common_time_index4))/2)] + 300, -0.1*eta_lim, str(time_index4_date[0])+ '\n' + time_index4_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
plt.legend(fontsize=8)
plt.grid()
plt.savefig(str(folder_name_DC)+'/'+'Inverter_efficiency_over_time', dpi=dpi_custom)






fig1, ax1 = plt.subplots()
fig1.suptitle('Efficiency of ' + str(mount_type) + ' installation with measured POA irradiance')
ax1.plot(continuous_time,eta_measure[common_index],label='Efficiency')
#ax1.set(xlabel = 'Day in the year')
ax1.set(ylabel = 'Efficiency (%)')
ax1.set_ylim([0,eta_lim])
ax1.axvline(continuous_time[len(common_time_index1)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(common_time_index1)+ len(common_time_index2)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(common_time_index1)+ len(common_time_index2) + len(common_time_index3)], color='black', linestyle = '--')
ax1.set_xticks([])  # This removes x-ticks from the plot
ax1.text(continuous_time[len(time_index1_date)]/2, -0.1*eta_lim, str(time_index1_date[0])+ '\n' + time_index1_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + round((len(common_time_index2))/2)] , -0.1*eta_lim, str(time_index2_date[0])+ '\n' + time_index2_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(common_time_index2) + round((len(common_time_index3))/2)], -0.1*eta_lim, str(time_index3_date[0])+ '\n' + time_index3_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(common_time_index2) + len(common_time_index3) + round((len(common_time_index4))/2)] + 300, -0.1*eta_lim, str(time_index4_date[0])+ '\n' + time_index4_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
plt.legend(fontsize=8)
plt.grid()






# New index for eta calculation excluding times where eta is unrealisticly high



common_time_index1 = common_time_index1[eta_with_bi[common_time_index1]<21.66]
common_time_index2 = common_time_index2[eta_with_bi[common_time_index2]<21.66]
common_time_index3 = common_time_index3[eta_with_bi[common_time_index3]<21.66]
common_time_index4 = common_time_index4[eta_with_bi[common_time_index4]<21.66]


common_time_index1_measure = common_time_index1[eta_measure[common_time_index1]<21.66]
common_time_index2_measure = common_time_index2[eta_measure[common_time_index2]<21.66]
common_time_index3_measure = common_time_index3[eta_measure[common_time_index3]<21.66]
common_time_index4_measure = common_time_index4[eta_measure[common_time_index4]<21.66]



common_index = common_index[eta_with_bi[common_index]<21.66]
common_index_measure = common_index[eta_measure[common_index]<21.66]

time_index1_date = common_time_index1.strftime('%Y-%m-%d')
time_index2_date = common_time_index2.strftime('%Y-%m-%d')
time_index3_date = common_time_index3.strftime('%Y-%m-%d')
time_index4_date = common_time_index4.strftime('%Y-%m-%d')


time_index1_date_measure = common_time_index1_measure.strftime('%Y-%m-%d')
time_index2_date_measure = common_time_index2_measure.strftime('%Y-%m-%d')
time_index3_date_measure = common_time_index3_measure.strftime('%Y-%m-%d')
time_index4_date_measure = common_time_index4_measure.strftime('%Y-%m-%d')

continuous_time = range(len(common_index))
continuous_time_measure = range(len(common_index_measure))
eta_lim = 25



#Daily mean 
et = eta_with_bi[common_index]
eta_with_bi_daily_mean = eta_with_bi[common_index].resample('D').mean()
eta_with_bi_daily_mean = eta_with_bi_daily_mean.dropna()
eta_with_bi_daily_mean = eta_with_bi_daily_mean.reindex(common_index, method = 'ffill')

eta_measure_with_bi_daily_mean = eta_measure[common_index_measure].resample('D').mean()
eta_measure_with_bi_daily_mean = eta_measure_with_bi_daily_mean.dropna()
eta_measure_with_bi_daily_mean = eta_measure_with_bi_daily_mean.reindex(common_index_measure, method = 'ffill')




eta_with_bi_mean = eta_with_bi[common_index].mean()
eta_with_bi_mean = pd.Series(eta_with_bi_mean, index=common_index)


eta_measure_with_bi_mean = eta_measure[common_index_measure].mean()
eta_measure_with_bi_mean = pd.Series(eta_measure_with_bi_mean, index=common_index_measure)


fig1, ax1 = plt.subplots()
fig1.suptitle('Efficiency of ' + str(mount_type) + ' installation with modelled POA irradiance \n excluding too high efficiencies')
ax1.plot(continuous_time,eta_with_bi[common_index],label='Efficiency')
#ax1.set(xlabel = 'Day in the year')
ax1.set(ylabel = 'Efficiency (%)')
ax1.set_ylim([0,eta_lim])
ax1.axvline(continuous_time[len(common_time_index1)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(common_time_index1)+ len(common_time_index2)], color='black', linestyle = '--')
ax1.axvline(continuous_time[len(common_time_index1)+ len(common_time_index2) + len(common_time_index3)], color='black', linestyle = '--')
ax1.set_xticks([])  # This removes x-ticks from the plot
ax1.text(continuous_time[len(time_index1_date)]/2, -0.1*eta_lim, str(time_index1_date[0])+ '\n' + time_index1_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + round((len(common_time_index2))/2)] , -0.1*eta_lim, str(time_index2_date[0])+ '\n' + time_index2_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(common_time_index2) + round((len(common_time_index3))/2)], -0.1*eta_lim, str(time_index3_date[0])+ '\n' + time_index3_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time[len(time_index1_date) + len(common_time_index2) + len(common_time_index3) + round((len(common_time_index4))/2)] + 300 , -0.1*eta_lim, str(time_index4_date[0])+ '\n' + time_index4_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.plot(continuous_time,eta_with_bi_daily_mean[common_index],label='Efficiency daily mean')
ax1.plot(continuous_time,eta_with_bi_mean[common_index],label='Efficiency mean')
plt.legend(fontsize=8,ncol=3)
plt.grid()
plt.savefig(str(folder_name_DC)+'/'+'Inverter_efficiency_over_time_new_index', dpi=dpi_custom)






fig1, ax1 = plt.subplots()
fig1.suptitle('Efficiency of ' + str(mount_type) + ' installation with measured POA irradiance \n excluding too high efficiencies')
ax1.plot(continuous_time_measure,eta_measure[common_index_measure],label='Efficiency')
#ax1.set(xlabel = 'Day in the year')
ax1.set(ylabel = 'Efficiency (%)')
ax1.set_ylim([0,eta_lim])
ax1.axvline(continuous_time_measure[len(common_time_index1_measure)], color='black', linestyle = '--')
ax1.axvline(continuous_time_measure[len(common_time_index1_measure)+ len(common_time_index2_measure)], color='black', linestyle = '--')
ax1.axvline(continuous_time_measure[len(common_time_index1_measure)+ len(common_time_index2_measure) + len(common_time_index3_measure)], color='black', linestyle = '--')
ax1.set_xticks([])  # This removes x-ticks from the plot
ax1.text(continuous_time_measure[len(time_index1_date_measure)]/2, -0.1*eta_lim, str(time_index1_date_measure[0])+ '\n' + time_index1_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time_measure[len(time_index1_date_measure) + round((len(common_time_index2_measure))/2)] , -0.1*eta_lim, str(time_index2_date_measure[0])+ '\n' + time_index2_date_measure[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time_measure[len(time_index1_date_measure) + len(common_time_index2_measure) + round((len(common_time_index3_measure))/2)], -0.1*eta_lim, str(time_index3_date[0])+ '\n' + time_index3_date[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.text(continuous_time_measure[len(time_index1_date_measure) + len(common_time_index2_measure) + len(common_time_index3_measure) + round((len(common_time_index4_measure))/2)] + 300 , -0.1*eta_lim, str(time_index4_date_measure[0])+ '\n' + time_index4_date_measure[-1], fontsize=8, ha='center', va='center', family='sans-serif', 
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
ax1.plot(continuous_time_measure,eta_measure_with_bi_daily_mean[common_index_measure],label='Efficiency daily mean')
ax1.plot(continuous_time_measure,eta_measure_with_bi_mean[common_index_measure],label='Efficiency mean')
plt.legend(fontsize=8,ncol=3)
plt.grid()




day_plot('Efficiency of ' + str(mount_type) + ' installation', 
            'Efficiency (%)',
            value1 = eta_with_bi,
            value2 = eta_measure,
            value3 = eta_ref_row_DC,
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days_ACDC,
            #days = snow_days,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            custom_label= ['Efficiency modelled POA','Efficiency measured POA','Efficiency DC ref. row measured POA','',''],
            save_plots = True,
            path = str(folder_name_DC),
            y_lim =30 )

#%%% DC generation over time

#Losses for the modules
losses = (pvlib.pvsystem.pvwatts_losses(soiling=2, shading=3, snow=0, mismatch=2, wiring=2, connections=0.5, lid=0, nameplate_rating=0, age=0, availability=0))/100


# DC calculated from model in the periode and grid connected. In [kWh]
DC_gen_calc_common_index = (generation_DC1[common_time_index2_grid].sum()/12)*0.001
DC_gen_calc_common_index_with_losses = DC_gen_calc_common_index*(1-losses)

# DC from inverter in the periode and grid connected. In [kWh]
DC_gen_inv_common_index = inverter_DC[common_time_index2_grid].sum()/12


#%%% AC Sandia CEC over time

# DC calculated from model in the periode and grid connected. In [kWh]
AC_gen_calc_common_index = (generation_AC1[common_time_index2_grid].sum()/12)*0.001
AC_gen_calc_common_index_with_losses = AC_gen_calc_common_index*(1-losses)

# DC from inverter in the periode and grid connected. In [kWh]
AC_gen_inv_common_index = inverter_AC[common_time_index2_grid].sum()/12



#%%% AC

POA_Global = POA_Global.fillna(0)
inverter_efficiency = inverter_efficiency.fillna(0)
inverter_efficiency = inverter_efficiency.replace([float('inf'), float('-inf')], 0)
eff_total = eff_total[common_grid_connect]
inverter_efficiency = inverter_efficiency[common_grid_connect]

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def fit_logarithmic_function(x, y):
    # Define the logarithmic function
    def log_func(x, a, b, c):
        return a * np.log(x + b) + c
    
    # Fit the function to the data
    params, _ = curve_fit(log_func, x, y, p0=[20, 1, 40])
    return params, log_func

def find_transition_point(log_func, params):
    # Determine the point where log_func reaches 98.4%
    for x in np.linspace(0, 1500, 15000):  # High resolution for precision
        if log_func(x, *params) >= 98.4:
            return x
    return 1500  # Default if never reaches 98.4 within expected range

def define_piecewise_function(x, params, transition_point):
    # Piecewise function with smooth transition
    a, b, c = params
    return np.piecewise(x, [x <= transition_point, x > transition_point], [lambda x: a * np.log(x + b) + c, 98.4])

def plot_results(x, y, x_fit, y_fit):
    # Plot the original data and the fit
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, color='blue', label='Original Data')
    plt.plot(x_fit, y_fit, color='red', label='Fitted Log Function and Fixed Value')
    plt.title('Inverter Efficiency vs. POA Irradiance')
    plt.xlabel('POA Irradiance [W/m2]')
    plt.ylabel('Inverter Efficiency [%]')
    plt.legend()
    plt.grid(True)
    plt.show()

def process_data(POA_Global_eff, inverter_efficiency):
    # Filter data for the logarithmic fitting
    mask = (POA_Global_eff >= 0)
    x_data = POA_Global_eff[mask]
    y_data = inverter_efficiency[mask]

    params, log_func = fit_logarithmic_function(x_data.values, y_data.values)
    transition_point = find_transition_point(log_func, params)
    x_fit = np.linspace(0, 1500, 400)
    y_fit = define_piecewise_function(x_fit, params, transition_point)
    plot_results(x_data, y_data, x_fit, y_fit)
    return x_fit, y_fit, params, transition_point




x_fit, y_fit, params, transition_point = process_data(eff_total[common_grid_connect], inverter_efficiency[common_grid_connect])





a, b, c = params

def log_func(x, a, b, c):
    return a * np.log(x + b) + c

def calculate_efficiency(irradiance):
    """
    Calculate the inverter efficiency given a time series of irradiance.

    Parameters:
    - irradiance (pd.Series): A time series of irradiance values.

    Returns:
    - pd.Series: A time series of the corresponding inverter efficiency.
    """
    # Use apply to handle cases individually and avoid shape issues with np.piecewise
    def apply_piecewise(x):
        if x <= transition_point:
            return log_func(x, a, b, c)
        else:
            return 98.4

    efficiency = irradiance.apply(apply_piecewise)
    return efficiency

# Example usage:
# Assuming `irradiance_series` is your pd.Series with datetime index
# efficiency_series = calculate_efficiency(irradiance_series)


inv_eff_log= calculate_efficiency(eff_total)
AC_log = (inv_eff_log/100)*generation_DC1[common_grid_connect]



#%%% Create folder for the data 
from pathlib import Path

# Specify the name or path to the new directory
folder_name_AC = './results/AC_compare_'+str(mount_type)+'_interval_'+str(interval_scat)

# Create the directory; parents=True allows creating parent directories if needed, exist_ok=True avoids an error if the directory already exists
try:
    Path(folder_name_AC).mkdir(parents=True, exist_ok=True)
    print(f"Directory '{folder_name_AC}' created successfully")
except OSError as error:
    print(f"Creation of the directory '{folder_name_AC}' failed: {error}")


#AC1
scat_index1, fit_dict1 = scatter_plot('AC generation compare ' + str(mount_type)+ ' installation \n inverter model: CEC' , 
             y_label = 'Measured power (kW)',
             x_label = 'Modelled power (kW)',
             modelled_value = generation_AC1*0.001, 
             measured_value = inverter_AC, 
             #start_date = '2023-04-12 00:00:00', 
             #end_date=end_date,
             #start_date = start_date, 
             #end_date= end_date,
             time_index= common_index,
             solar_position= solar_position1,
             #solar_position= False,
             interval=interval_scat,
             color_value= solar_position1['azimuth'],
             y_lim = 40,
             model_to_run = model_to_run1,
             model_explain= model_explain_scatter,
             elevation_min= elevation_min1)  # False to have no lower bound on elevation
plt.savefig(str(folder_name_AC)+'/'+'CEC', dpi=dpi_custom)
 
if slope_adjust == True:
   AC_slope_adjust1 = (generation_AC1*fit_dict1['slope'])*0.001+fit_dict1['offset']
   scat_index, fit_dict1_ad = scatter_plot('AC generation compare ' + str(mount_type)+ ' installation \n inverter model: CEC. Adjusted', 
                y_label = 'Measured power (kW)',
                x_label = 'Modelled power (kW)',
                modelled_value = AC_slope_adjust1, 
                measured_value = inverter_AC, 
                #start_date = '2023-04-12 00:00:00', 
                #end_date=end_date,
                time_index= common_index,
                #start_date = start_date, 
                #end_date=end_date,
                #solar_position= False,
                solar_position= solar_position1,
                interval=interval_scat,
                color_value= solar_position1['azimuth'],
                y_lim = 40,
                model_to_run = model_to_run1,
                model_explain= model_explain_scatter,
                elevation_min= elevation_min1)  # False to have no lower bound on elevation
   plt.savefig(str(folder_name_AC)+'/'+'CEC_adjust', dpi=dpi_custom)




#AC2
scat_index1, fit_dict1 = scatter_plot('AC generation compare ' + str(mount_type)+ ' installation \n inverter model: Log function' , 
             y_label = 'Measured power (kW)',
             x_label = 'Modelled power (kW)',
             modelled_value = AC_log*0.001, 
             measured_value = inverter_AC, 
             #start_date = '2023-04-12 00:00:00', 
             #end_date=end_date,
             #start_date = start_date, 
             #end_date= end_date,
             time_index= common_index,
             solar_position= solar_position1,
             #solar_position= False,
             interval=interval_scat,
             color_value= solar_position1['azimuth'],
             y_lim = 40,
             model_to_run = model_to_run1,
             model_explain= model_explain_scatter,
             elevation_min= elevation_min1)  # False to have no lower bound on elevation
plt.savefig(str(folder_name_AC)+'/'+'log_function', dpi=dpi_custom)
 

if slope_adjust == True:
   AC_slope_adjust2 = (AC_log*fit_dict1['slope'])*0.001+fit_dict1['offset']
   scat_index, fit_dict1_ad = scatter_plot('AC generation compare ' + str(mount_type)+ ' installation \n inverter model: Log function. Adjusted', 
                y_label = 'Measured power (kW)',
                x_label = 'Modelled power (kW)',
                modelled_value = AC_slope_adjust2, 
                measured_value = inverter_AC, 
                #start_date = '2023-04-12 00:00:00', 
                #end_date=end_date,
                time_index= common_index,
                #start_date = start_date, 
                #end_date=end_date,
                #solar_position= False,
                solar_position= solar_position1,
                interval=interval_scat,
                color_value= solar_position1['azimuth'],
                y_lim = 40,
                model_to_run = model_to_run1,
                model_explain= model_explain_scatter,
                elevation_min= elevation_min1)  # False to have no lower bound on elevation
   plt.savefig(str(folder_name_AC)+'/'+'log_function_adjust', dpi=dpi_custom)



fig1, ax1= plt.subplots()
fig1.suptitle('Inverter efficiency '+ str(mount_type))
#ax1.scatter(POA_Global[common_index], inverter_efficiency[common_index],alpha=0.1, label='Original Data')
#ax1.scatter(POA_Global[common_index], inverter_efficiency_calc[common_index],alpha=0.5, label='calculated')
#ax1.scatter(x_inverter_efficiency,inverter_efficiency_grid_connect,alpha=0.5,label='Sandia model')
#ax1.scatter(x_inv_eff,inv_eff, color='red',alpha=0.5,label='Modelled inverter efficiency')
#ax1.plot(x_fit1, y_fit1, 'g-',linewidth=2, label='Log fit')
ax1.set(ylabel='Efficiency (%)')
ax1.set(xlabel='Effective irradiance (W/m2)')
ax1.set_ylim([30,105])
ax1.set_xlim([0,1200])
sc = ax1.scatter(eff_total[common_index], inverter_efficiency[common_index],c = temp_air1[common_index], cmap = 'jet',alpha=0.5) 
ax1.plot(x_fit,y_fit, color = 'red', linewidth = 2, label='Fitted log function')      
cbar = plt.colorbar(sc)
cbar.set_label('temp_air (°C)', fontsize=12)
ax1.scatter(eff_total[common_index], inverter_efficiency_calc[common_index],alpha=0.5, color='black', label='Sandia CEC inverter')
ax1.legend()    
plt.grid()
plt.savefig(str(folder_name_AC)+'/'+'Inverter_efficiency', dpi=dpi_custom)


fig1, ax1= plt.subplots()
fig1.suptitle('Inverter efficiency '+ str(mount_type))
#ax1.scatter(POA_Global[common_index], inverter_efficiency[common_index],alpha=0.1, label='Original Data')
#ax1.scatter(POA_Global[common_index], inverter_efficiency_calc[common_index],alpha=0.5, label='calculated')
#ax1.scatter(x_inverter_efficiency,inverter_efficiency_grid_connect,alpha=0.5,label='Sandia model')
#ax1.scatter(x_inv_eff,inv_eff, color='red',alpha=0.5,label='Modelled inverter efficiency')
#ax1.plot(x_fit1, y_fit1, 'g-',linewidth=2, label='Log fit')
ax1.set(ylabel='Efficiency (%)')
ax1.set(xlabel='Effective irradiance (W/m2)')
ax1.set_ylim([30,105])
ax1.set_xlim([0,1200])
sc = ax1.scatter(eff_total[common_index], inverter_efficiency[common_index],c = temp_air1[common_index], cmap = 'jet',alpha=0.5)    
cbar = plt.colorbar(sc)
cbar.set_label('temp_air (°C)', fontsize=12)
ax1.legend()    
plt.grid()
plt.savefig(str(folder_name_AC)+'/'+'Inverter_efficiency_original', dpi=dpi_custom)



AC_log = AC_log.reindex(index=data.index, fill_value=0)
inv_eff_log = inv_eff_log.reindex(index=data.index, fill_value=0)


day_plot('AC generation ' + str(mount_type) + ' installation', 
            'AC power (kW)',
            value1 = generation_AC1*0.001,
            value2 = AC_log*0.001,
            value3 = inverter_AC,
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days_ACDC,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            save_plots = True,
            path = str(folder_name_AC),
            custom_label= ['Sandia CEC inverter','Fitted log function','Inverter AC','',''],
            y_lim = 40)

inverter_efficiency = (inverter_AC/inverter_DC)*100
day_plot('Inverter efficiency ' + str(mount_type) + ' installation', 
            'Efficiency (%)',
            value1 = inverter_efficiency_calc,
            value2 = inv_eff_log,
            value3 = inverter_efficiency,
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days_ACDC,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            save_plots = True,
            path = str(folder_name_AC),
            custom_label= ['Sandia CEC inverter','Fitted log function','Inverter reading','',''],
            y_lim = 105)




day_plot('Temperature of cell ' + str(mount_type) + ' installation', 
            'Temperature (°C)',
            value1 = temp_cell1,
            value2 = temp_cell2,
            value3 = temp_cell3,
            value4 = temp_air1,        
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days_ACDC,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            custom_label= ['SAPM','PVsyst29','PVsyst56','Temp. air',''],
            y_lim = 65)





#%%% Plots of AC generation over the long interval
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Assuming 'generation_AC1' is your Series with a DatetimeIndex
# Create a DataFrame from the Series for easier manipulation
generation_AC1 = generation_AC1*0.001
df = generation_AC1.to_frame(name='generation_AC1')

# Add columns for day of the year and time of the day
df['day'] = df.index.dayofyear
df['time'] = df.index.time

# Pivot the DataFrame to format suitable for heatmap
result = df.pivot_table(index='time', columns='day', values='generation_AC1', aggfunc='mean')

# Generate the heatmap
plt.figure(figsize=(12, 10))  # Adjust the figure size based on your needs
ax = sns.heatmap(result, cmap='viridis', cbar_kws={'label': 'AC power [kW]'})
plt.title('AC Power Output Over the Year')
plt.xlabel('Day of the Year')
plt.ylabel('Time of Day')
plt.xticks(rotation=45)  # Optional: Rotate x labels for better readability
plt.tight_layout()  # Adjust layout to make sure everything fits

plt.show()







import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

gen_AC = generation_AC1[time_index3]



# Assuming 'generation_AC1' is your Series with a DatetimeIndex
# Create a DataFrame from the Series for easier manipulation
df = gen_AC.to_frame(name='generation_AC1')

# Add columns for day of the year and time of the day
df['day'] = df.index.dayofyear
df['time'] = df.index.time

# Pivot the DataFrame to format suitable for heatmap
result = df.pivot_table(index='time', columns='day', values='generation_AC1', aggfunc='mean')

# Generate the heatmap
plt.figure(figsize=(12, 10))  # Adjust the figure size based on your needs
ax = sns.heatmap(result, cmap='viridis', cbar_kws={'label': 'AC power [W]'})

# Set the title and labels
plt.title('AC Power Output Over the Year')
plt.xlabel('Day of the Year')
plt.ylabel('Time of Day')

# Customize the ticks for better readability
# Set ticks every 10 days on the x-axis
ax.set_xticks([x for x in range(len(result.columns)) if x % 10 == 0])
ax.set_xticklabels([result.columns[x] for x in range(len(result.columns)) if x % 10 == 0])

# Set ticks every 2 hours on the y-axis
time_ticks = pd.date_range("00:00", "23:59", freq="2H").time
ax.set_yticks([i for i, time in enumerate(result.index) if time in time_ticks])
ax.set_yticklabels([time.strftime('%H:%M') for time in time_ticks if time in result.index])

# Optional: Rotate x labels for better readability
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout to make sure everything fits

plt.show()
















import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

gen_AC = generation_AC1[time_index1]



# Assuming 'generation_AC1' is your Series with a DatetimeIndex
# Create a DataFrame from the Series for easier manipulation
df = gen_AC.to_frame(name='generation_AC1')

# Add columns for date and time of the day
df['date'] = df.index.date
df['time'] = df.index.time

# Pivot the DataFrame to format suitable for heatmap
result = df.pivot_table(index='time', columns='date', values='generation_AC1', aggfunc='mean')

# Generate the heatmap
plt.figure(figsize=(12, 10))  # Adjust the figure size based on your needs
ax = sns.heatmap(result, cmap='viridis', cbar_kws={'label': 'AC power [W]'})

# Set the title and labels
plt.title('AC Power Output Over the Year')
plt.xlabel('Date')
plt.ylabel('Time of Day')

# Customize the ticks for better readability
# Select an interval for x-ticks that gives a good balance (e.g., every 15 days)
date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='1D')
ax.set_xticks([result.columns.get_loc(date) for date in date_range if date in result.columns])
ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in date_range if date in result.columns])

# Set ticks for every 2 hours on the y-axis
time_ticks = pd.date_range("00:00", "23:59", freq="2H").time
ax.set_yticks([i for i, time in enumerate(result.index) if time in time_ticks])
ax.set_yticklabels([time.strftime('%H:%M') for time in time_ticks if time in result.index])

# Optional: Rotate x labels for better readability
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout to make sure everything fits

plt.show()

"""










"""





import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

gen_AC = generation_AC1[time_index1]



# Assuming 'generation_AC1' is your Series with a DatetimeIndex
# Create a DataFrame from the Series for easier manipulation
df = gen_AC.to_frame(name='generation_AC1')

# Add columns for date and time of the day
df['date'] = df.index.date
df['time'] = df.index.time

# Pivot the DataFrame to format suitable for heatmap
result = df.pivot_table(index='time', columns='date', values='generation_AC1', aggfunc='mean')

# Generate the heatmap
plt.figure(figsize=(12, 10))
ax = sns.heatmap(result, cmap='viridis', cbar_kws={'label': 'AC power [W]'})

# Set the title and labels
plt.title('AC Power Output Over the Year')
plt.xlabel('Date')
plt.ylabel('Time of Day')

# Customize the ticks for better readability
# Collect all unique dates and sample them for ticks (e.g., every 15th date)
all_dates = result.columns
sampled_dates = all_dates[::5]  # Adjust this slicing based on your dataset size and date range

ax.set_xticks([all_dates.get_loc(date) for date in sampled_dates])
ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in sampled_dates])

# Set ticks for every 2 hours on the y-axis
time_ticks = pd.date_range("00:00", "23:59", freq="2H").time
ax.set_yticks([i for i, time in enumerate(result.index) if time in time_ticks])
ax.set_yticklabels([time.strftime('%H:%M') for time in time_ticks if time in result.index])

# Optional: Rotate x labels for better readability
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout to make sure everything fits

plt.show()

































import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


gen_AC1 = generation_AC1[time_index1]
gen_AC2 = generation_AC1[time_index2]

# Assuming both 'generation_AC1' and 'generation_AC2' are Series with a DatetimeIndex
# Resample both series to a common interval, here I choose hourly for example
# You might adjust the 'H' to a suitable frequency based on your specific intervals
df1 = gen_AC1.resample('5T').mean().to_frame(name='generation_AC1')
df2 = gen_AC2.resample('5T').mean().to_frame(name='generation_AC2')

# Merge the two dataframes
df_combined = pd.concat([df1, df2], axis=1)

# Add columns for date and time of the day
df_combined['date'] = df_combined.index.date
df_combined['time'] = df_combined.index.time

# Pivot the DataFrame to format suitable for heatmap
# Here, you might decide to display one or both of the series
result = df_combined.pivot_table(index='time', columns='date', values=['generation_AC1', 'generation_AC2'], aggfunc='mean')

# Generate the heatmap
plt.figure(figsize=(18, 10))  # Increased figure size for better visibility
ax = sns.heatmap(result, cmap='viridis', cbar_kws={'label': 'AC power [W]'})

# Set the title and labels
plt.title('AC Power Output Over the Year (Both Intervals)')
plt.xlabel('Date')
plt.ylabel('Time of Day')

# Customize the ticks for better readability
date_range = pd.date_range(start=df_combined.index.min(), end=df_combined.index.max(), freq='15D')
ax.set_xticks([result.columns.get_loc((slice(None), date), method='nearest') for date in date_range if date in df_combined.index.date])
ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in date_range if date in df_combined.index.date])

# Set ticks for every 2 hours on the y-axis
time_ticks = pd.date_range("00:00", "23:59", freq="2H").time
ax.set_yticks([i for i, time in enumerate(result.index) if time in time_ticks])
ax.set_yticklabels([time.strftime('%H:%M') for time in time_ticks if time in result.index])

# Optional: Rotate x labels for better readability
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout to make sure everything fits

plt.show()





















import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



gen_AC1 = generation_AC1[time_index1]*0.001
gen_AC2 = generation_AC1[time_index2]*0.001
gen_AC3 = generation_AC1[time_index3]*0.001
gen_AC4 = generation_AC1[time_index4]*0.001

# Assuming both 'generation_AC1' and 'generation_AC2' are Series with a DatetimeIndex
# Resample both series to a common interval, here I choose hourly for example
# You might adjust the 'H' to a suitable frequency based on your specific intervals
df1 = gen_AC1.resample('5T').mean().to_frame(name='generation_AC1')
df2 = gen_AC2.resample('5T').mean().to_frame(name='generation_AC2')
df3 = gen_AC3.resample('5T').mean().to_frame(name='generation_AC3')
df4 = gen_AC3.resample('5T').mean().to_frame(name='generation_AC4')



# Merge all dataframes
df_combined = pd.concat([df1, df2, df3, df4], axis=1)

# Add columns for date and time of the day
df_combined['date'] = df_combined.index.date
df_combined['time'] = df_combined.index.time

# Pivot the DataFrame to format suitable for heatmap
result = df_combined.pivot_table(index='time', columns='date', values=['generation_AC1', 'generation_AC2', 'generation_AC3', 'generation_AC4'], aggfunc='mean')

# Generate the heatmap
plt.figure(figsize=(20, 12))  # Adjust figure size for clarity
ax = sns.heatmap(result, cmap='viridis', cbar_kws={'label': 'AC power [kW]'})

# Set the title and labels
plt.title('AC Power Output Over the Year (All Intervals)')
plt.xlabel('Date')
plt.ylabel('Time of Day')

# Customize the ticks for better readability
date_range = pd.date_range(start=df_combined.index.min(), end=df_combined.index.max(), freq='15D')
ax.set_xticks([result.columns.get_loc((slice(None), date), method='nearest') for date in date_range if date in df_combined.index.date])
ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in date_range if date in df_combined.index.date])

# Set ticks for every 2 hours on the y-axis
time_ticks = pd.date_range("00:00", "23:59", freq="2H").time
ax.set_yticks([i for i, time in enumerate(result.index) if time in time_ticks])
ax.set_yticklabels([time.strftime('%H:%M') for time in time_ticks if time in result.index])

# Optional: Rotate x labels for better readability
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout to make sure everything fits

plt.show()








import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

gen_AC1 = generation_AC1[time_index1]*0.001
gen_AC2 = generation_AC1[time_index2]*0.001
gen_AC3 = generation_AC1[time_index3]*0.001
gen_AC4 = generation_AC1[time_index4]*0.001

# Resample the series to a common interval
df1 = gen_AC1.resample('5T').mean().to_frame(name='generation_AC1')
df2 = gen_AC2.resample('5T').mean().to_frame(name='generation_AC2')
df3 = gen_AC3.resample('5T').mean().to_frame(name='generation_AC3')
df4 = gen_AC4.resample('5T').mean().to_frame(name='generation_AC4')

# Merge all dataframes
df_combined = pd.concat([df1, df2, df3, df4], axis=1)

# Add columns for date and time of the day
df_combined['date'] = df_combined.index.date
df_combined['time'] = df_combined.index.time

# Pivot the DataFrame to format suitable for heatmap
result = df_combined.pivot_table(index='time', columns='date', values=['generation_AC1', 'generation_AC2', 'generation_AC3', 'generation_AC4'], aggfunc='mean')

# Generate the heatmap
plt.figure(figsize=(24, 14))
ax = sns.heatmap(result, cmap='viridis', cbar_kws={'label': 'AC power [kW]'})

# Set the title and labels with very large fonts
ax.set_title('AC Power Output Over the Year (All Intervals)', fontsize=24)
ax.set_xlabel('Date', fontsize=20)
ax.set_ylabel('Time of Day', fontsize=20)

# Customize the ticks for better readability and larger fonts
date_range = pd.date_range(start=df_combined.index.min(), end=df_combined.index.max(), freq='15D')
ax.set_xticks([result.columns.get_loc((slice(None), date), method='nearest') for date in date_range if date in df_combined.index.date])
ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in date_range if date in df_combined.index.date], fontsize=18)

time_ticks = pd.date_range("00:00", "23:59", freq="2H").time
ax.set_yticks([i for i, time in enumerate(result.index) if time in time_ticks])
ax.set_yticklabels([time.strftime('%H:%M') for time in time_ticks if time in result.index], fontsize=18)

# Color bar font size adjustment
cbar = ax.collections[0].colorbar
cbar.ax.set_ylabel('AC power [kW]', fontsize=22)
cbar.ax.tick_params(labelsize=20)

# Optional: Rotate x labels for better readability
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust layout to make sure everything fits

plt.show()






import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

gen_AC1 = generation_AC1[time_index1]*0.001
gen_AC2 = generation_AC1[time_index2]*0.001
gen_AC3 = generation_AC1[time_index3]*0.001
gen_AC4 = generation_AC1[time_index4]*0.001

# Resample the series to a common interval
df1 = gen_AC1.resample('5T').mean().to_frame(name='generation_AC1')
df2 = gen_AC2.resample('5T').mean().to_frame(name='generation_AC2')
df3 = gen_AC3.resample('5T').mean().to_frame(name='generation_AC3')
df4 = gen_AC4.resample('5T').mean().to_frame(name='generation_AC4')

# Merge all dataframes
df_combined = pd.concat([df1, df2, df3, df4], axis=1)

# Add columns for date and time of the day
df_combined['date'] = df_combined.index.date
df_combined['time'] = df_combined.index.time

# Pivot the DataFrame to format suitable for heatmap
result = df_combined.pivot_table(index='time', columns='date', values=['generation_AC1', 'generation_AC2', 'generation_AC3', 'generation_AC4'], aggfunc='mean')

# Generate the heatmap
plt.figure(figsize=(24, 14))
ax = sns.heatmap(result, cmap='viridis', cbar_kws={'label': 'AC power [kW]'})

# Set the title and labels with very large fonts
ax.set_title('AC Power Output Over the Year (All Intervals)', fontsize=24)
ax.set_xlabel('Date', fontsize=20)
ax.set_ylabel('Time of Day', fontsize=20)

# Customize the ticks for better readability and larger fonts
# Make sure that the date range includes all dates in the index
date_ticks = [date.strftime('%Y-%m-%d') for date in result.columns.levels[1]]  # Assuming multi-level index after pivot
ax.set_xticks(range(len(date_ticks)))
ax.set_xticklabels(date_ticks, rotation=45, fontsize=18)


time_ticks = pd.date_range("00:00", "23:59", freq="2H").time
ax.set_yticks([i for i, time in enumerate(result.index) if time in time_ticks])
ax.set_yticklabels([time.strftime('%H:%M') for time in time_ticks if time in result.index], fontsize=18)

# Color bar font size adjustment
cbar = ax.collections[0].colorbar
cbar.ax.set_ylabel('AC power [kW]', fontsize=22)
cbar.ax.tick_params(labelsize=20)

plt.tight_layout()  # Adjust layout to make sure everything fits

plt.show()



"""













#gen_AC_tilt = pd.read_csv("./gen_AC_tilt.csv",index_col=0)

#gen_AC_tilt = gen_AC_tilt['0']


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Example data setup -- Assuming generation_AC1 is defined and time_index variables are set
gen_AC1 = generation_AC1[time_index1]*0.001
gen_AC2 = generation_AC1[time_index2]*0.001
gen_AC3 = generation_AC1[time_index3]*0.001
gen_AC4 = generation_AC1[time_index4]*0.001




# Resample the series to a common interval
df1 = gen_AC1.resample('5T').mean().to_frame(name='generation_AC1')
df2 = gen_AC2.resample('5T').mean().to_frame(name='generation_AC2')
df3 = gen_AC3.resample('5T').mean().to_frame(name='generation_AC3')
df4 = gen_AC4.resample('5T').mean().to_frame(name='generation_AC4')

# Merge all dataframes
df_combined = pd.concat([df1, df2, df3, df4], axis=1)

# Add columns for date and time of the day
df_combined['date'] = df_combined.index.date
df_combined['time'] = df_combined.index.time

# Pivot the DataFrame to format suitable for heatmap
result = df_combined.pivot_table(index='time', columns='date', values=['generation_AC1', 'generation_AC2', 'generation_AC3', 'generation_AC4'], aggfunc='mean')

# Generate the heatmap
plt.figure(figsize=(24, 14))
ax = sns.heatmap(result, cmap='viridis', cbar_kws={'label': 'AC power [kW]'})

# Set the title and labels with very large fonts
ax.set_title('AC Power Output for the Tilted installation', fontsize=40)
ax.set_xlabel('Date', fontsize=25)
ax.set_ylabel('Time of Day', fontsize=25)

# Customize the ticks for better readability and larger fonts
date_ticks = [date.strftime('%Y-%m-%d') for date in result.columns.levels[1]]  # Assuming multi-level index after pivot

# Show a date label for every 7 days
date_interval = 7  # Adjust this as needed for the desired frequency
ax.set_xticks(range(0, len(date_ticks), date_interval))
ax.set_xticklabels(date_ticks[::date_interval], rotation=45, fontsize=25)

time_ticks = pd.date_range("00:00", "23:59", freq="2H").time
ax.set_yticks([i for i, time in enumerate(result.index) if time in time_ticks])
ax.set_yticklabels([time.strftime('%H:%M') for time in time_ticks if time in result.index], fontsize=25)

# Color bar font size adjustment
cbar = ax.collections[0].colorbar
cbar.ax.set_ylabel('AC power [kW]', fontsize=22)
cbar.ax.tick_params(labelsize=20)

plt.tight_layout()  # Adjust layout to make sure everything fits

plt.show()









import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Assuming generation_AC1 is defined and time_index1 is set
gen_AC1 = generation_AC1[time_index1]*0.001

# Resample the series to a common interval
df1 = gen_AC1.resample('5T').mean().to_frame(name='generation_AC1')

# Add columns for date and time of the day
df1['date'] = df1.index.date
df1['time'] = df1.index.time

# Pivot the DataFrame to format suitable for heatmap
result = df1.pivot_table(index='time', columns='date', values='generation_AC1', aggfunc='mean')

# Generate the heatmap
plt.figure(figsize=(24, 14))
ax = sns.heatmap(result, cmap='viridis', cbar_kws={'label': 'AC power [kW]'})

# Set the title and labels with very large fonts
ax.set_title('AC Power Output for the Tilted installation', fontsize=40)
ax.set_xlabel('Date', fontsize=25)
ax.set_ylabel('Time of Day', fontsize=25)

# Customize the ticks for better readability and larger fonts
date_ticks = [date.strftime('%Y-%m-%d') for date in result.columns]  # Simplified index handling
date_interval = 7  # Show a date label for every 7 days
ax.set_xticks(range(0, len(date_ticks), date_interval))
ax.set_xticklabels(date_ticks[::date_interval], rotation=45, fontsize=25)

time_ticks = pd.date_range("00:00", "23:59", freq="2H").time
ax.set_yticks([i for i, time in enumerate(result.index) if time in time_ticks])
ax.set_yticklabels([time.strftime('%H:%M') for time in time_ticks if time in result.index], fontsize=25)

# Color bar font size adjustment
cbar = ax.collections[0].colorbar
cbar.ax.set_ylabel('AC power [kW]', fontsize=22)
cbar.ax.tick_params(labelsize=20)

plt.tight_layout()  # Adjust layout to make sure everything fits
plt.show()





#gen_AC_tilt = generation_AC1.copy()
# Saving the Series to a CSV file
#gen_AC_tilt.to_csv("./gen_AC_tilt.csv", index=True)



"""
array_length = 8760
hour_in_day = [(i % 24) + 1 for i in range(array_length)]
day_in_year = [(i // 24 % 365) + 1 for i in range(array_length)]
day_grid = np.zeros(365)
hour_grid = np.zeros(24)



# Determine the shape of the 2D array based on the maximum x and y coordinates
shape = (np.max(hour_in_day) + 1, np.max(day_in_year) + 1)

# Create a 2D array filled with zeros
result = np.zeros(shape, dtype=ac_power.dtype)

# Fill the 2D array with values from the 1D array based on coordinates
for i in range(len(ac_power)):
    result[hour_in_day[i], day_in_year[i]] = ac_power[i]

result_reduced = result[1:, 1:]
result_reduced_without_nan = np.nan_to_num(result_reduced, nan=0)





# Create a 2D array filled with zeros
result_mono = np.zeros(shape, dtype=ac_power_mono.dtype)

# Fill the 2D array with values from the 1D array based on coordinates
for i in range(len(ac_power_mono)):
    result_mono[hour_in_day[i], day_in_year[i]] = ac_power_mono[i]

result_reduced_mono = result_mono[1:, 1:]
result_reduced_without_nan_mono = np.nan_to_num(result_reduced_mono, nan=0)


difference_ac_power = result_reduced_without_nan - result_reduced_without_nan_mono


# Assuming you have your data in x, y, and z
# Replace these with your actual data or generate sample data

# Create a grid of x and y values
x_grid, y_grid = np.meshgrid(day_grid, hour_grid)

# Create the contour plot
fig5, ax5 = plt.subplots()
fig5.suptitle('AC power output')
contour_plot = ax5.contourf(result_reduced_without_nan, cmap='inferno')
colorbar = plt.colorbar(contour_plot, label='AC power [W]')
ax5.set(ylabel='Hour in the day')
ax5.set(xlabel = 'Day in the year')

"""




eff_total = eff_total.reindex(data.index, method = 'ffill')
eff_front = eff_front.reindex(data.index, method = 'ffill')
eff_back = eff_back.reindex(data.index, method = 'ffill')

ref_total = ref_front + ref_back
ref_total.name = 'Total Reflection'






day_plot('Effective POA irradiance from Performance Model', 
            'Irradiance (W.m-2)',
            value1 = eff_total,
            value2 = eff_front,
            value3 = eff_back,
            value4 = ref_front,
            value5 = ref_back,
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            custom_label= ['Total',str(front_name) ,str(back_name),'Ref.','r',],
            save_plots = False,
            y_lim=1400) # Adds a x-axis in the top with the solar azimuth






day_plot_6_1('Effective POA irradiance for the Tilted installation', 
            'Irradiance (W.m-2)',
            value1 = fuel_in_total,
            value2 = fuel_in_front,
            value3 = fuel_in_back,
            value4 = ref_front,
            value5 = ref_back,
            value6 = ref_total,
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            custom_label= ['Total model','Front model','Back model','Ref. front','Ref. back', 'Ref. total'],
            save_plots = False,
            zoom = (3,20),
            y_lim=1400) # Adds a x-axis in the top with the solar azimuth





#kWh/m2
POA_sky_diffuse_grid = (POA_sky_diffuse_total[common_grid_connect].sum()/12)*0.001

POA_ground_diffuse_grid = (POA_ground_diffuse_total[common_grid_connect].sum()/12)*0.001

POA_direct_grid = (POA_direct_total[common_grid_connect].sum()/12)*0.001

POA_total_grid = POA_sky_diffuse_grid + POA_ground_diffuse_grid + POA_direct_grid

