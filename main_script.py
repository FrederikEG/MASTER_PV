# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 13:51:07 2024

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


model_to_run = {'GHI_sensor':'GHI',                     # 'GHI', 'SPN1', 'GHI_2nd' (only hour mean)
                'sky_model_inf':'isotropic',            # 'isotropic', 'haydavies'
                'sky_model_simple' : 'isotropic',           # 'isotropic', 'haydavies', 'perez' ......
                'shadow_interpolate' : 'true',          # 'true', 'false'
                'temp_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station' 
                'spectral_mismatch_model' : 'Sandia',   # 'Sandia', 'Gueymard', None
                'wind_sensor' : 'default',              # 'default', 'weather_station', '2nd weather_station'
                'RH_sensor' : 'default',                # 'default', 'weather_station', '2nd weather_station'  
                'shadow' : 'False',                     # 'True', 'False'
                'inverter_model' : 'Sandia',            # 'Sandia', 
                'model_perez' : 'allsitescomposite1990',
                'mount_type' : 'Vertical',              # 'Tilted', 'Vertical'
                'iam_apply' : 'SAPM',                   # 'ashrae', 'SAPM' and False 
                'inverter_limit' : True,
                'DNI_model': 'simple'}                  #  'dirint', 'dirindex_turbidity', 'dirindex', 'simple'                      

model_explain = False
y_lines = True

#%%%

POA, solar_position, albedo, GHI_inf, aoi_west, aoi_east, spec_loss, poa_infinite_sheds, albedo_daily, dni_inf, elevation_min = POA(PV_data,
                  installation_data,
                  tz,
                  GHI_sensor= model_to_run['GHI_sensor'],
                  model = model_to_run['sky_model_inf'],
                  shadow_interpolate= model_to_run['shadow_interpolate'],
                  temp_sensor = model_to_run['temp_sensor'],
                  spectral_mismatch_model = model_to_run['spectral_mismatch_model'],
                  RH_sensor = model_to_run['RH_sensor'],
                  iam_apply = model_to_run['iam_apply'],
                  DNI_model = model_to_run['DNI_model'],
                  mount_type = model_to_run['mount_type'])


#Uses the temp and wind sensor that works
DC_output, DC_mid_rows, eff_irrad_total, temp_cell, temp_air = DC_generation_temp_select(POA,
                          PV_data,
                          installation_data,
                          temp_sensor= model_to_run['temp_sensor'],
                          wind_sensor= model_to_run['wind_sensor'],
                          shadow = model_to_run['shadow'],
                          pyranometer = True,   #Using pyranometer as input
                          mount_type = model_to_run['mount_type'])


AC_output= AC_generation(DC_output, 
                          eff_irrad_total,
                          temp_cell,
                          temp_air,
                          installation_data['inverter'],
                          data,
                          model = model_to_run['inverter_model'])

#%%% The simple approach where the calculations assume a single unobstructed row




POA_no_shad, poa_no_shadow_east, poa_no_shadow_west, poa_no_shadow_both, GHI_simple, dni_simple, solar_position, elevation_min  = POA_simple(PV_data,
                  installation_data,
                  tz,
                  GHI_sensor= model_to_run['GHI_sensor'],
                  model = model_to_run['sky_model_simple'],
                  shadow_interpolate= model_to_run['shadow_interpolate'],
                  temp_sensor = model_to_run['temp_sensor'],
                  spectral_mismatch_model = model_to_run['spectral_mismatch_model'],
                  RH_sensor = model_to_run['RH_sensor'],
                  model_perez = model_to_run['model_perez'],
                  iam_apply = model_to_run['iam_apply'],
                  DNI_model = model_to_run['DNI_model'],
                  mount_type = model_to_run['mount_type'])


#Uses the temp and wind sensor that works
DC_output_no_shad, DC_mid_rows_no_shad, eff_irrad_total_no_shad, temp_cell_no_shad, temp_air_no_shad = DC_generation_temp_select(POA_no_shad,
                          PV_data,
                          installation_data,
                          temp_sensor= model_to_run['temp_sensor'],
                          wind_sensor= model_to_run['wind_sensor'],
                          shadow = model_to_run['shadow'],
                          mount_type= model_to_run['mount_type'])



AC_output_no_shad = AC_generation(DC_generation = DC_output_no_shad, 
                          eff_irrad_total = eff_irrad_total_no_shad,
                          temp_cell = temp_cell_no_shad,
                          temp_air = temp_air_no_shad,
                          inverter_CEC = installation_data['inverter'],
                          data = data,
                          model = model_to_run['inverter_model'])



#%%% Calculating DC and AC based on input from the reference cells



DC_output_ref_cell, DC_mid_rows_ref_cell, eff_irrad_total_ref_cell, temp_cell_ref_cell, temp_air_ref_cell = DC_generation_temp_select(POA_no_shad,
                          PV_data,
                          installation_data,
                          temp_sensor= model_to_run['temp_sensor'],
                          wind_sensor= model_to_run['wind_sensor'],
                          shadow = model_to_run['shadow'],
                          pyranometer=False,    # Meaning using ref cells
                          mount_type= model_to_run['mount_type'])








#%%% Calculations for ploting / midrows and azimuth adjustment

DC_mid_rows_measure = ((data['VBF PV2 input current (A)']*data['VBF PV2 input voltage (V)']) + (data['VBF PV3 input current (A)']*data['VBF PV3 input voltage (V)']))/1000

DC_diff, iam_cus1, iam_dict = iam_custom(DC_mid_rows_measure, DC_mid_rows, aoi_west, solar_position, day='2023-05-12')
days = ['2023-05-12 00:00:00', '2023-06-14 00:00:00']
iam_days_dict = iam_custom_days(DC_mid_rows_measure, DC_mid_rows, aoi_west, solar_position, days)

sol_pot, iam_cus_read = iam_custom_read(iam_dict, solar_position)
iam_copy=iam_cus_read.copy()
iam_copy.index=solar_position.index

DC_mid_rows['p_mp'] = DC_mid_rows['p_mp'].fillna(0)
DC_mid_rows_p_mp_azimuth_correct = DC_mid_rows['p_mp'] * iam_copy


#%%% plots
"""
daily_plots('Power generation test', 
            'DC Power (kW)',
            data['INV-1-TBF Total input power (kW)'], 
            data['INV-2-VBF Total input power (kW)'], 
            '2023-05-05 00:00:00', 
            '2023-05-10 00:00:00')
"""

# Plots for sunny and cloudy days
sun_cloud_days = ['2023-05-12 00:00:00', '2023-05-17 00:00:00']
sun_cloud_days1 = ['2023-05-12 00:00:00+00:00', '2023-05-17 00:00:00+00:00']

snow_nonsnow_days = ['2023-12-09 00:00:00', '2023-12-10 00:00:00']

day_plot('Power generation', 
            'DC Power (kW)',
            value1 = data['INV-2-VBF Total input power (kW)'],
            value2 =data['INV-1-TBF Total input power (kW)'],
            days = sun_cloud_days,
            y_lim=40,
            model_to_run = model_to_run,
            model_explain= model_explain)

day_plot('POA East', 
            'Irradiance',
            value1 = POA['POA fuel_in East'],
            value2 = data['Reference Cell Vertical East (W.m-2)'],
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain= model_explain)

day_plot('POA West', 
            'Irradiance',
            value1 = POA['POA fuel_in West'],
            value2 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain= model_explain)


day_plot('POA West - inf and no shadow', 
            'Irradiance',
            value1 = POA['POA fuel_in West'],
            value2 = data['Reference Cell Vertical West (W.m-2)'],
            value3 = POA_no_shad['POA fuel_in West'],
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain= model_explain,
            solar_position = solar_position['azimuth'],
            y_lines = y_lines) # Adds a x-axis in the top with the solar azimuth


day_plot('POA East - inf and no shadow', 
            'Irradiance',
            value1 = POA['POA fuel_in East'],
            value2 = data['Reference Cell Vertical East (W.m-2)'],
            value3 = POA_no_shad['POA fuel_in East'],
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain= model_explain,
            solar_position = solar_position['azimuth'],
            y_lines= y_lines,
            custom_label= ['POA inf.', 'ref cell', 'POA simple','', ''])


day_plot('DC generation vertical', 
            'DC Power (kW)',
            value1 = data['INV-2-VBF Total input power (kW)'],
            value2 = DC_output['p_mp']/1000,
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain= model_explain,
            solar_position = solar_position['azimuth'],
            y_lines = y_lines)


day_plot('DC generation vertical', 
            'DC Power (kW)',
            value1 = data['INV-2-VBF Total input power (kW)'],
            value2 = DC_output['p_mp']/1000,
            value3 = DC_output_no_shad['p_mp']/1000,
            value4 = DC_output_ref_cell['p_mp']/1000,
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain= model_explain,
            custom_label=['INV-2-VBF Total input power (kW)', 'p_mp inf.', 'p_mp no_shad', 'p_mp ref cell',''],
            zoom = False,
            solar_position = solar_position['azimuth'],
            y_lines = y_lines)

day_plot('DC middel rows vertical', 
            'DC Power (kW)',
            value1 = DC_mid_rows_measure,
            value2 = DC_mid_rows['p_mp']/1000,
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain= model_explain,
            #poa_direct = False, 
            poa_direct = poa_infinite_sheds['poa_back_direct'], 
            poa_sky_diffuse = poa_infinite_sheds['poa_back_sky_diffuse'], 
            poa_ground_diffuse = poa_infinite_sheds['poa_back_ground_diffuse'], 
            poa_global = poa_infinite_sheds['poa_back'],
            zoom = False)

day_plot('DC middel rows vertical', 
            'DC Power (kW)',
            value1 = DC_mid_rows_measure,
            value2 = DC_mid_rows['p_mp']/1000,
            days = ['2023-06-14 00:00:00', '2023-05-17 00:00:00'],
            model_to_run = model_to_run,
            model_explain= model_explain)

day_plot('DC middel rows vertical azimuth corrected', 
            'DC Power (kW)',
            value1 = DC_mid_rows_measure,
            value2 = DC_mid_rows_p_mp_azimuth_correct/1000,
            days = ['2023-05-12 00:00:00', '2023-05-17 00:00:00'],
            model_to_run = model_to_run,
            model_explain= model_explain)


day_plot('AC generation vertical', 
            'AC Power (kW)',
            value1 = data['INV-2-VBF Active power (kW)'],
            value2 = AC_output/1000,
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain= model_explain)


day_plot('Albedo profile', 
            'Albedo [-]',
            value1 = albedo,
            days = sun_cloud_days,
            y_lim=1,
            model_to_run = model_to_run,
            model_explain= model_explain,
            custom_label = ['Albedo','','','',''])


day_plot('Albedo profile', 
            'Albedo [-]',
            value1 = albedo,
            value2 = albedo_daily,
            #days = snow_nonsnow_days,
            days = sun_cloud_days,
            y_lim=1,
            model_to_run = model_to_run,
            model_explain= model_explain,
            solar_position = solar_position['elevation'],
            y_lines = y_lines,
            custom_label = ['Albedo','Albedo_10°_avg','','',''])


day_plot('GHI', 
            'Irradiance',
            value1 = data[('GHI (W.m-2)')],
            value2 = GHI_simple,
            value3= data[('DHI_SPN1 (W.m-2)')],
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain= model_explain,
            solar_position = solar_position['azimuth'],
            y_lines = y_lines)

day_plot('DNI', 
            'Irradiance [W.m-2]',
            value1 = dni_inf,
            value2 = dni_simple,
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain= model_explain,
            zoom = False,
            solar_position = solar_position['azimuth'],
            y_lines = y_lines,
            y_lim = 1000)


"""
scatter_plot('Ref model compare West', 
             y_label = 'measured',
             x_label = 'Modelled',
             value1 = POA['POA fuel_in West'], 
             value2 = data['Reference Cell Vertical West (W.m-2)'], 
             start_date = '2023-04-12 00:00:00', 
             end_date='2023-05-17 00:00:00',
             y_lim = 1000) 
"""

scat_index = scatter_plot('Ref model compare West color inf', 
             y_label = 'measured',
             x_label = 'Modelled',
             modelled_value = POA['POA fuel_in West'], 
             measured_value = data['Reference Cell Vertical West (W.m-2)'], 
             #start_date = '2023-04-12 00:00:00', 
             #end_date='2023-05-13 00:00:00',
             start_date = '2023-04-12 00:00:00', 
             end_date='2023-05-13 00:00:00',
             solar_position= solar_position,
             interval='afternoon',
             color_value= solar_position['azimuth'],
             y_lim = 1000,
             model_to_run = model_to_run,
             model_explain= model_explain,
             elevation_min= elevation_min)  # False to have no lower bound on elevation

scat_index = scatter_plot('Ref model compare West color simple', 
             y_label = 'measured',
             x_label = 'Modelled',
             modelled_value = POA_no_shad['POA fuel_in West'], 
             measured_value = data['Reference Cell Vertical West (W.m-2)'], 
             start_date = '2023-04-12 00:00:00', 
             end_date='2023-05-13 00:00:00',
             solar_position= solar_position,
             interval='false',
             color_value= solar_position['azimuth'],
             y_lim = 1000,
             model_to_run = model_to_run,
             model_explain= model_explain,
             regression_line = True) 


scat_index = scatter_plot('Ref model compare East color inf', 
             y_label = 'measured',
             x_label = 'Modelled',
             modelled_value = POA['POA fuel_in East'], 
             measured_value = data['Reference Cell Vertical East (W.m-2)'], 
             start_date = '2023-04-12 00:00:00', 
             end_date='2023-05-13 00:00:00',
             solar_position= solar_position,
             interval='morning',
             color_value= solar_position['azimuth'],
             y_lim = 1000,
             model_to_run = model_to_run,
             model_explain= model_explain) 



scat_index = scatter_plot('Ref model compare East color simple', 
             y_label = 'measured',
             x_label = 'Modelled',
             modelled_value = POA_no_shad['POA fuel_in East'], 
             measured_value = data['Reference Cell Vertical East (W.m-2)'], 
             start_date = '2023-04-12 00:00:00', 
             end_date='2023-05-13 00:00:00',
             solar_position= solar_position,
             interval='morning',
             color_value= solar_position['azimuth'],
             y_lim = 1000,
             model_to_run = model_to_run,
             model_explain= model_explain) 


RMSE = math.sqrt(np.square(np.subtract(POA['POA fuel_in West'][scat_index],data['Reference Cell Vertical West (W.m-2)'][scat_index])).mean())
nRMSE = RMSE/POA['POA fuel_in West'][scat_index].mean()


scat_index = scatter_plot('DC generation compare inf', 
             y_label = 'Measured (kW)',
             x_label = 'Modelled (kW)',
             modelled_value = DC_output['p_mp']/1000, 
             measured_value = data['INV-2-VBF Total input power (kW)'], 
             start_date = '2023-04-12 00:00:00', 
             end_date='2023-05-13 00:00:00',
             solar_position= solar_position,
             interval='afternoon',
             color_value= solar_position['azimuth'],
             model_to_run = model_to_run,
             model_explain= model_explain) 


scat_index = scatter_plot('DC generation compare simple', 
             y_label = 'Measured (kW)',
             x_label = 'Modelled (kW)',
             modelled_value = DC_output_no_shad['p_mp']/1000, 
             measured_value = data['INV-2-VBF Total input power (kW)'], 
             start_date = '2023-04-12 00:00:00', 
             end_date='2023-05-13 00:00:00',
             solar_position= solar_position,
             interval='afternoon',
             color_value= solar_position['azimuth'],
             model_to_run = model_to_run,
             model_explain= model_explain) 


scat_index = scatter_plot('DC generation compare ref_cell', 
             y_label = 'Measured (kW)',
             x_label = 'Modelled (kW)',
             modelled_value = DC_output_ref_cell['p_mp']/1000, 
             measured_value = data['INV-2-VBF Total input power (kW)'], 
             start_date = '2023-04-12 00:00:00', 
             end_date='2023-05-13 00:00:00',
             solar_position= solar_position,
             interval='afternoon',
             color_value= solar_position['azimuth'],
             model_to_run = model_to_run,
             model_explain= model_explain,
             y_lim=40) 

scat_index = scatter_plot('DC generation mid rows compare', 
             y_label = 'Measured (kW)',
             x_label = 'Modelled (kW)',
             modelled_value = DC_mid_rows['p_mp']/1000, 
             measured_value = DC_mid_rows_measure, 
             start_date = '2023-06-14 00:00:00', 
             end_date='2023-06-15 00:00:00',
             solar_position= solar_position,
             interval='afternoon',
             color_value= aoi_west,
             model_to_run = model_to_run,
             model_explain= model_explain) 

scat_index = scatter_plot('DC generation mid rows compare azimuth correct', 
             y_label = 'Measured (kW)',
             x_label = 'Modelled (kW)',
             modelled_value = DC_mid_rows_p_mp_azimuth_correct/1000, 
             measured_value = DC_mid_rows_measure, 
             start_date = '2023-06-14 00:00:00', 
             end_date='2023-06-15 00:00:00',
             solar_position= solar_position,
             interval='morning',
             color_value= aoi_west,
             model_to_run = model_to_run,
             model_explain= model_explain) 


solar_pos_scat('DC diff', 
             y_label = 'Diff',
             x_label = 'solar azimuth',
             value1 = solar_position['azimuth'], 
             #value2 = DC_diff*100, 
             value2=iam_cus1,
             start_date = '2023-05-12 00:00:00', 
             end_date='2023-05-13 00:00:00',
             solar_position= solar_position,
             interval='afternoon',
             color_value= temp_air,
             y_lim = [0.5,1.5],
             x_lim = [180,360],
             model_to_run = model_to_run,
             model_explain= model_explain)

solar_pos_scat('DC diff iam_custom', 
             y_label = 'Diff',
             x_label = 'solar azimuth',
             value1 = solar_position['azimuth'], 
             #value2 = DC_diff*100, 
             value2=iam_copy,
             start_date = '2023-06-14 00:00:00', 
             end_date='2023-06-15 00:00:00',
             solar_position= solar_position,
             interval='afternoon',
             color_value= temp_air,
             y_lim = [0.5,1.5],
             x_lim = [180,360],
             model_to_run = model_to_run,
             model_explain= model_explain)


bar_plots(poa_model= 'infinite_sheds',
          poa_data = poa_infinite_sheds,
          model_to_run = model_to_run,
          days=sun_cloud_days1, 
          model_explain= model_explain)


bar_plots(poa_model= 'simple',
          poa_data = poa_no_shadow_both,
          model_to_run = model_to_run,
          days=sun_cloud_days1, 
          model_explain= model_explain)


day_histo_plot(Title = 'POA components for the day inf west', 
               y_label= 'percentage',
               days = sun_cloud_days, 
               model_to_run = model_to_run, 
               model_explain= model_explain,
               poa_direct = poa_infinite_sheds['poa_back_direct'], 
               poa_sky_diffuse = poa_infinite_sheds['poa_back_sky_diffuse'], 
               poa_ground_diffuse = poa_infinite_sheds['poa_back_ground_diffuse'], 
               poa_global = poa_infinite_sheds['poa_back'],
               zoom=False)

day_histo_plot(Title = 'POA components for the day inf east', 
               y_label= 'percentage',
               days = sun_cloud_days, 
               model_to_run = model_to_run, 
               model_explain= model_explain,
               poa_direct = poa_infinite_sheds['poa_front_direct'], 
               poa_sky_diffuse = poa_infinite_sheds['poa_front_sky_diffuse'], 
               poa_ground_diffuse = poa_infinite_sheds['poa_front_ground_diffuse'], 
               poa_global = poa_infinite_sheds['poa_front'],
               zoom=False)

# The simple is swithced for east and west
day_histo_plot(Title = 'POA components for the day east simple', 
               y_label= 'percentage',
               days = sun_cloud_days, 
               model_to_run = model_to_run, 
               model_explain= model_explain,
               poa_direct = poa_no_shadow_east['poa_direct'], 
               poa_sky_diffuse = poa_no_shadow_east['poa_sky_diffuse'], 
               poa_ground_diffuse = poa_no_shadow_east['poa_ground_diffuse'], 
               poa_global = poa_no_shadow_east['poa_global'],
               zoom=False)


# The simple is swithced for east and west
day_histo_plot(Title = 'POA components for the day west simple', 
               y_label= 'percentage',
               days = sun_cloud_days, 
               model_to_run = model_to_run, 
               model_explain= model_explain,
               poa_direct = poa_no_shadow_west['poa_direct'], 
               poa_sky_diffuse = poa_no_shadow_west['poa_sky_diffuse'], 
               poa_ground_diffuse = poa_no_shadow_west['poa_ground_diffuse'], 
               poa_global = poa_no_shadow_west['poa_global'],
               zoom=False)


#%%%
"""
iam_cus = DC_mid_rows_measure/(DC_mid_rows['p_mp']/1000)
# The days are sunny
days = ['2023-05-07 00:00:00', '2023-05-08 00:00:00','2023-05-12 00:00:00', '2023-06-10 00:00:00','2023-06-11 00:00:00','2023-06-12 00:00:00' ,'2023-06-14 00:00:00']
tz = 'UTC'
i=0
time_index_test2= pd.DatetimeIndex([])
#Creates datetimeinedx for the periods of the days
for day in days:
    time_index_test = pd.date_range(start=days[i], 
                           periods=24*12*1, 
                           freq='5min',
                           tz=tz)
    time_index_test2 = time_index_test2.append(time_index_test)
    i=i+1
    
iam_cus = iam_cus[time_index_test2]
iam_cus = iam_cus.replace([np.inf, np.nan], 1)
iam_cus[(iam_cus > 1.5) | (iam_cus < 0.6)] = 1
solar_azimuth = solar_position['azimuth'][time_index_test2]

iam_cus = iam_cus[(solar_azimuth>180) & (solar_azimuth<300)]
iam_cus_non1 = iam_cus[(solar_azimuth>180) & (solar_azimuth<300)]
solar_azimuth_non1 = solar_azimuth[iam_cus_non1.index]
iam_cus = iam_cus.reindex(time_index_test2, fill_value=1)    



# Perform polynomial regression
degree = 10  # Degree of the polynomial
coefficients = np.polyfit(solar_azimuth, iam_cus, degree)

# Generate polynomial function from coefficients
polynomial_func = np.poly1d(coefficients)

plt.figure(figsize=(8, 8))
gs1 = gridspec.GridSpec(1, 1)
ax0 = plt.subplot(gs1[0,0])
ax0.scatter(solar_azimuth.iloc[0:288], iam_cus.iloc[0:288],c='red')
ax0.scatter(solar_azimuth.iloc[288:576], iam_cus.iloc[288:576],c='blue')
ax0.scatter(solar_azimuth.iloc[576:864], iam_cus.iloc[576:864],c='green')
ax0.scatter(solar_azimuth.iloc[864:1152], iam_cus.iloc[864:1152],c='orange')
ax0.scatter(solar_azimuth.iloc[1152:1440], iam_cus.iloc[1152:1440],c='black')
ax0.scatter(solar_azimuth.iloc[1440:1728], iam_cus.iloc[1440:1728],c='purple')
ax0.plot(solar_azimuth, polynomial_func(solar_azimuth), color='red', label='Fitted polynomial')
ax0.set_xlim([0,360])
ax0.set_ylim([0.5,1.3])

tt = solar_azimuth.iloc[0:288]



# Perform polynomial regression
degree = 5  # Degree of the polynomial
coefficients_non1 = np.polyfit(solar_azimuth_non1, iam_cus_non1, degree)

# Generate polynomial function from coefficients
polynomial_func_non1 = np.poly1d(coefficients_non1)

plt.figure(figsize=(8, 8))
gs1 = gridspec.GridSpec(1, 1)
ax0 = plt.subplot(gs1[0,0])
ax0.scatter(solar_azimuth_non1, iam_cus_non1,c='blue')
ax0.plot(solar_azimuth, polynomial_func_non1(solar_azimuth), color='red', label='Fitted polynomial')
ax0.set_xlim([180,300])
ax0.set_ylim([0.5,1.3])


aoi_west.to_csv("my_series.csv", index=True)


"""


















"""

GHI_sensor= model_to_run['GHI_sensor']
model = model_to_run['sky_model_simple']
shadow_interpolate= model_to_run['shadow_interpolate']
temp_sensor = model_to_run['temp_sensor']
spectral_mismatch_model = model_to_run['spectral_mismatch_model']
RH_sensor = model_to_run['RH_sensor']
model_perez = model_to_run['model_perez']




GHI = pd.to_numeric(data[('GHI (W.m-2)')])
GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')])
GHI_2nd = pd.to_numeric(data[('GHI_2nd station (W.m-2)')])
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
DHI_SPN1 = pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])
Albedometer = pd.to_numeric(data[('Albedometer (W.m-2)')])

poa_no_shadow_west = pvlib.irradiance.get_total_irradiance(surface_tilt = 180 - installation_data['tilt'], 
                                                      surface_azimuth = installation_data['orientation'] + 180, 
                                                      solar_zenith = solar_position['apparent_zenith'], 
                                                      solar_azimuth = solar_position['azimuth'], 
                                                      dni = GHI,
                                                      dni_extra= GHI,
                                                      ghi = GHI, 
                                                      dhi = DHI_SPN1,
                                                      model = model,
                                                      model_perez = model_perez)


poa_west = poa_no_shadow_west['poa_direct'] + poa_no_shadow_west['poa_diffuse'] + poa_no_shadow_west['poa_sky_diffuse'] + poa_no_shadow_west['poa_ground_diffuse']









"""

    
modelled_value = POA['POA fuel_in West']
measured_value = data['Reference Cell Vertical West (W.m-2)'] 

reg_line(modelled_value, measured_value, scat_index)
iam_west = pvlib.iam.ashrae(aoi_west)




#%%%  PVfactor model


"""
from pvlib.bifacial.pvfactors import pvfactors_timeseries


pvrow_height = 1
pvrow_width = 10

#Location of PV installation - AU Foulum
lat = installation_data['lat']
lon = installation_data['lon']
altitude= installation_data['altitude']
pitch = installation_data['pitch']
gcr = installation_data['gcr']
tilt = installation_data['tilt']
orientation = installation_data['orientation']

location = pvlib.location.Location(lat, lon, tz=tz)



pressure = pvlib.atmosphere.alt2pres(installation_data['altitude'])
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


time_index = pd.date_range(start='2023-05-12 00:00:00', 
                                 end='2023-05-18 00:00:00', 
                                 freq='5min',  
                                     tz=tz)


irrad = pvfactors_timeseries(
    solar_azimuth=solar_position['azimuth'][time_index],
    solar_zenith=solar_position['apparent_zenith'][time_index],
    surface_azimuth=installation_data['orientation'],  # south-facing array
    surface_tilt=installation_data['tilt'],
    axis_azimuth=installation_data['orientation']+90,  # 90 degrees off from surface_azimuth.  270 is ok too
    timestamps=time_index,
    dni=dni[time_index],
    dhi=pd.to_numeric(data[('DHI_SPN1 (W.m-2)')])[time_index],
    gcr=installation_data['gcr'],
    pvrow_height=pvrow_height,
    pvrow_width=pvrow_width,
    albedo=0.2,
    n_pvrows=4,
    index_observed_pvrow=1
)

irrad_in_front = irrad[0]
irrad_in_back = irrad[1]


day_plot('POA - pvfactors', 
            'Irradiance',
            value1 = irrad_in_front,
            value2 = irrad_in_back,
            days = sun_cloud_days,
            model_to_run = model_to_run,
            model_explain= model_explain,
            solar_position = solar_position['azimuth'],
            y_lines = y_lines) # Adds a x-axis in the top with the solar azimuth



#irrad[['total_inc_back', 'total_abs_back']].plot()
#irrad[['total_inc_front', 'total_abs_front']].plot()

"""



