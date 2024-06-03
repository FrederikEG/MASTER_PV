# -*- coding: utf-8 -*-
"""
Created on Wed May  8 14:33:21 2024

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
elif model_to_run1['transposition'] =='simple' and model_to_run2['transposition'] =='simple':
    POA1 = POA_no_shad1
    POA2 = POA_no_shad2
elif model_to_run1['transposition'] =='simple' and model_to_run2['transposition'] =='inf': 
        POA1 = POA_no_shad1
        POA2 = POA2
elif model_to_run1['transposition'] =='inf' and model_to_run2['transposition'] =='simple': 
        POA1 = POA1
        POA2 = POA_no_shad2
    
    
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



    


generation_AC1 = AC_CEC1

#%%% Plots

sun_cloud_days = ['2023-05-12 00:00:00', '2023-05-17 00:00:00']



# The datetimeindex for the scatter plot should be adjusted to only include 
# times when the inverter is working (grid connected)


# Finding the intersection
common_index = time_index.intersection(grid_connect_index)
common_grid_connect = time_index.intersection(grid_connect_index)



    
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
sc = ax1.scatter(POA_Global[common_index], inverter_efficiency[common_index],c = temp_air1[common_index], cmap = 'jet',alpha=0.5)       
cbar = plt.colorbar(sc)
cbar.set_label('temp_air', fontsize=12)
#ax1.scatter(POA_Global[common_index], inverter_efficiency_calc[common_index],alpha=0.5, color='black', label='calculated')
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



# New index for eta calculation excluding times where eta is unrealisticly high





#%%% AC


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


#%%%

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
ax1.plot(x_fit,y_fit, color = 'red', linewidth = 2, label='Fitted log function')
sc = ax1.scatter(eff_total[common_index], inverter_efficiency[common_index],c = temp_air1[common_index], cmap = 'jet',alpha=0.5)       
cbar = plt.colorbar(sc)
cbar.set_label('temp_air', fontsize=12)
#ax1.scatter(POA_Global[common_index], inverter_efficiency_calc[common_index],alpha=0.5, color='black', label='calculated')
ax1.legend()    
plt.grid()
plt.savefig(str(folder_name_DC)+'/'+'Inverter_efficiency', dpi=dpi_custom)




import numpy as np
import pandas as pd

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


ww= calculate_efficiency(eff_total)
