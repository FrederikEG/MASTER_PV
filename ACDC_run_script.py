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


#start_date = '2023-04-12 00:00:00'
#end_date='2023-05-13 00:00:00'



# Calculating the time_index here overruels the start and end date
time_index_type = 'all_relevant'
time_index  = interval_select(time_index_type, data = data, filter_faulty=filter_faulty)



mount_type = 'Vertical'         # 'Tilted', 'Vertical'
model_variation = 'ACDC'         # 'DNI', 'sensor', 'transposition_simple', 'transposition_inf', 'IAM', 'spectrum'
temperature_model = 'sapm'      # 'sapm', 'PVsyst29', 'PVsyst56'

#Selects the transposition model from this face. Results are only true for this face 
trans_side = 'West'   #  'Up', 'Down', 'East', 'West', 'both_sides'



if mount_type == 'Vertical':
    back_name = 'West'
    front_name = 'East'
    ref_front = data['Reference Cell Vertical East (W.m-2)'].copy()
    ref_back = data['Reference Cell Vertical West (W.m-2)'].copy()
    plot_interval_front = 'morning'
    plot_interval_back = 'afternoon'
    y_lim = {'front': 1000,
             'back' : 1000}
    
    inverter_DC = data['INV-2-VBF Total input power (kW)']
    inverter_AC = data['INV-2-VBF Active power (kW)']
    grid_connect_index = data[data['VBF inverter status'] == 'Grid connected'].index

    
    if ref_cell_adjust == True:
        GHI_zero_index = GHI_CMP6[time_index][GHI_CMP6==0].index
        ref_front_offset = ref_front[GHI_zero_index].mean()
        ref_back_offset = ref_back[GHI_zero_index].mean()
        ref_front = ref_front - ref_front_offset
        ref_back = ref_back - ref_back_offset
    
elif mount_type=='Tilted':
    back_name = 'Down'
    front_name = 'Up'
    ref_front = data['Reference Cell Tilted facing up (W.m-2)']
    ref_back = data['Reference Cell Tilted facing down (W.m-2)']
    plot_interval_front = 'false'
    plot_interval_back = 'false'
    y_lim = {'front': 1200,
             'back' : 300}
    
    inverter_DC = data['INV-1-TBF Total input power (kW)']
    inverter_AC = data['INV-1-TBF Active power (kW)']
    grid_connect_index = data[data['TBF inverter status'] == 'Grid connected'].index

    
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
    
    
    
#For infinite sheds

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
    
    
    
# Making the name of POA independent on the transposition method

if model_to_run1['transposition'] =='inf':
    POA = POA1
elif model_to_run1['transposition'] =='simple':  
    POA = POA_no_shad1
    
   #Applies the bifaciality to the right faces  
if mount_type == 'Tilted':
    eff_front = POA['POA fuel_in front']
    eff_back = POA['POA fuel_in back'] * PV_data['bifaciality']
    eff_total = eff_front+eff_back
    G_with_bi = POA['POA front']+ POA['POA back']* PV_data['bifaciality']
    
    
elif mount_type == 'Vertical':
    eff_front = POA['POA fuel_in front'] * PV_data['bifaciality'] #The east facing side
    eff_back = POA['POA fuel_in back'] 
    eff_total = eff_front+eff_back
    G_with_bi = POA['POA front'] * PV_data['bifaciality']+ POA['POA back']
  
    #Calculating DC
dc_scaled1, dc_mid_rows1, temp_cell1, temp_air1  = DC_generation_simple(POA, eff_total,
                          PV_data, 
                          installation_data, 
                          temp_sensor = model_to_run1['temp_sensor'],
                          wind_sensor= model_to_run1['wind_sensor'], 
                          inverter_limit = model_to_run1['inverter_limit'],
                          temperature_model = temperature_model) 


dc_scaled2, dc_mid_rows2, temp_cell2, temp_air2  = DC_generation_simple(POA, eff_total,
                          PV_data, 
                          installation_data, 
                          temp_sensor = model_to_run1['temp_sensor'],
                          wind_sensor= model_to_run1['wind_sensor'], 
                          inverter_limit = model_to_run1['inverter_limit'],
                          temperature_model = 'PVsyst29') 

dc_scaled3, dc_mid_rows3, temp_cell3, temp_air3  = DC_generation_simple(POA, eff_total,
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



# The datetimeindex for the scatter plot should be adjusted to only include 
# times when the inverter is working (grid connected)


# Finding the intersection
common_index = time_index.intersection(grid_connect_index)


day_plot('DC generation ' + str(mount_type) + ' installation', 
            'DC power (kW)',
            value1 = generation_DC1*0.001,
            value2 = generation_DC2*0.001,
            value3 = generation_DC3*0.001,
            value4 = inverter_DC,
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            custom_label= ['sapm','PVsyst29','PVsyst56','Inverter_DC',''],
            y_lim = 40)



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


ACDC_generation = pd.DataFrame({'DC': generation_DC1, 'AC': generation_AC1})

ACDC_inverter = pd.DataFrame({'DC': inverter_DC, 'AC': inverter_AC})


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
                #solar_position= solar_position1,
                solar_position= False,
                interval='false',
                color_value= solar_position1['azimuth'],
                model_to_run = model_to_run1,
                model_explain= model_explain_scatter,
                elevation_min= False)  # False to have no lower bound on elevation
   #plt.savefig(str(folder_name)+'/'+'Ref_'+ str(front_name)+'_compare_' + str(model_variation)+ '_' +str(custom_label[0]), dpi=300)



    if slope_adjust == True:
       ACDC_slope_adjust1 = (ACDC_generation[i]*fit_dict1['slope']+fit_dict1['offset'])*0.001
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
                    solar_position= False,
                    interval='false',
                    color_value= solar_position1['azimuth'],
                    y_lim = 40,
                    model_to_run = model_to_run1,
                    model_explain= model_explain_scatter,
                    elevation_min= elevation_min1)  # False to have no lower bound on elevation
       #plt.savefig(str(folder_name)+'/'+'Ref_'+ str(front_name)+'_compare_' + str(model_variation)+ '_' +str(custom_label[0])+'_slope_adjusted', dpi=300)
 
    
 
    
#Inverter efficiency

inverter_efficiency = (inverter_AC/inverter_DC)*100
inverter_efficiency_calc = (generation_AC1/generation_DC1)*100

fig1, ax1= plt.subplots()
fig1.suptitle('Inverter efficiency')
ax1.scatter(POA['POA Global'][common_index], inverter_efficiency[common_index],alpha=0.1, label='Original Data')
#ax1.scatter(POA['POA Global'][common_index], inverter_efficiency_calc[common_index],alpha=0.5, label='calculated')
#ax1.scatter(x_inverter_efficiency,inverter_efficiency_grid_connect,alpha=0.5,label='Sandia model')
#ax1.scatter(x_inv_eff,inv_eff, color='red',alpha=0.5,label='Modelled inverter efficiency')
#ax1.plot(x_fit1, y_fit1, 'g-',linewidth=2, label='Log fit')
ax1.set(ylabel='Efficiency [%]')
ax1.set(xlabel='Effective irradiance [W/m2]')
ax1.set_ylim([30,105])
ax1.legend()    
sc = ax1.scatter(POA['POA Global'][common_index], inverter_efficiency[common_index],c = temp_air1[common_index], cmap = 'jet',alpha=0.5)       
cbar = plt.colorbar(sc)
cbar.set_label('temp_air', fontsize=12)


"""
scat_index1, fit_dict1 = scatter_plot(str(i)+' generation compare ' + str(mount_type)+ ' installation', 
         y_label = 'Efficiency (%)',
         x_label = 'Effective irradiance (W.m-2) total',
         modelled_value = POA['POA Global'], 
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

"""
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
eta_with_bi = ((inverter_AC*1000)/ (G_with_bi * area))*100
eta = ((inverter_AC*1000)/ (POA['POA Global'] * area))*100






# Calculating the time_index here overruels the start and end date
time_index_type = 'all_relevant'
time_index  = interval_select(time_index_type, data = data, filter_faulty=filter_faulty)



time_index_type1 = 'interval1'
time_index1  = interval_select(time_index_type1, data = data, filter_faulty=filter_faulty)
# Finding the intersection
common_time_index1 = time_index1.intersection(grid_connect_index)

time_index_type2 = 'interval2'
time_index2  = interval_select(time_index_type2, data = data, filter_faulty=filter_faulty)
# Finding the intersection
common_time_index2 = time_index2.intersection(grid_connect_index)

time_index_type3 = 'interval3'
time_index3  = interval_select(time_index_type3, data = data, filter_faulty=filter_faulty)
# Finding the intersection
common_time_index3 = time_index3.intersection(grid_connect_index)

time_index_type4 = 'interval4'
time_index4  = interval_select(time_index_type4, data = data, filter_faulty=filter_faulty)
# Finding the intersection
common_time_index4 = time_index4.intersection(grid_connect_index)


continuous_time = range(len(common_index))
eta_lim = 50

time_index1_date = common_time_index1.strftime('%Y-%m-%d')
time_index2_date = common_time_index2.strftime('%Y-%m-%d')
time_index3_date = common_time_index3.strftime('%Y-%m-%d')
time_index4_date = common_time_index4.strftime('%Y-%m-%d')

fig1, ax1 = plt.subplots()
fig1.suptitle('Efficiency of ' + str(mount_type) + ' installation')
ax1.plot(continuous_time,eta_with_bi[common_index],label='Eta with bifaciality')
#ax1.set(xlabel = 'Day in the year')
ax1.set(ylabel = 'Eta [%]')
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
plt.legend()


# New index for eta calculation excluding times where eta is unrealisticly high



common_time_index1 = common_time_index1[eta_with_bi[common_time_index1]<21.66]
common_time_index2 = common_time_index2[eta_with_bi[common_time_index2]<21.66]
common_time_index3 = common_time_index3[eta_with_bi[common_time_index3]<21.66]
common_time_index4 = common_time_index4[eta_with_bi[common_time_index4]<21.66]

common_index = common_index[eta_with_bi[common_index]<21.66]

time_index1_date = common_time_index1.strftime('%Y-%m-%d')
time_index2_date = common_time_index2.strftime('%Y-%m-%d')
time_index3_date = common_time_index3.strftime('%Y-%m-%d')
time_index4_date = common_time_index4.strftime('%Y-%m-%d')

continuous_time = range(len(common_index))
eta_lim = 25



#Daily mean 
et = eta_with_bi[common_index]
eta_with_bi_daily_mean = eta_with_bi[common_index].resample('D').mean()
eta_with_bi_daily_mean = eta_with_bi_daily_mean.dropna()
eta_with_bi_daily_mean = eta_with_bi_daily_mean.reindex(common_index, method = 'ffill')

eta_with_bi_mean = eta_with_bi[common_index].mean()
eta_with_bi_mean = pd.Series(eta_with_bi_mean, index=common_index)

fig1, ax1 = plt.subplots()
fig1.suptitle('Efficiency of ' + str(mount_type) + ' installation - new index')
ax1.plot(continuous_time,eta_with_bi[common_index],label='Eta with bifaciality')
#ax1.set(xlabel = 'Day in the year')
ax1.set(ylabel = 'Eta [%]')
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
ax1.plot(continuous_time,eta_with_bi_daily_mean[common_index],label='Eta with bifaciality daily mean')
ax1.plot(continuous_time,eta_with_bi_mean[common_index],label='Eta with bifaciality mean')
plt.legend()


day_plot('Efficiency of ' + str(mount_type) + ' installation', 
            'Eta (%)',
            value1 = eta_with_bi,
            value2 = eta,
            #value5 = data['Reference Cell Vertical West (W.m-2)'],
            days = sun_cloud_days,
            model_explain= model_explain,
            solar_position = solar_position1['azimuth'],
            y_lines = y_lines,
            custom_label= ['Eta_with_bi','Eta','','',''],
            y_lim =30 )





