# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 13:41:57 2024

@author: frede
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec 
import pvlib
import numpy as np
from scipy.optimize import curve_fit

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
                        'w_vertical_structure' : 0.1,
                        'w_horizontal_structure' : 0.1,
                        'inverter' : 'Huawei_Technologies_Co___Ltd___SUN2000_40KTL_US__480V_'}

installation_data['height'] = 2* PV_data['module_width'] + PV_data['module_width']
installation_data['gcr'] = installation_data['height'] /installation_data['pitch']
installation_data['pvrow_width'] = 10*PV_data['module_height']

tz='UTC' 



#test of functions
from POA_function import POA
from DC_output import DC_generation
from AC_output import AC_generation


POA_iso = POA(PV_data,
                  installation_data,
                  tz,
                  GHI_sensor='GHI_SPN1',
                  model = 'isotropic')

DC_output_iso = DC_generation(POA_iso,
                              PV_data,
                              installation_data,
                              temp_sensor='2nd weather_station',
                              shadow='True')



POA = POA(PV_data,
                  installation_data,
                  tz,
                  GHI_sensor='GHI_SPN1',
                  model = 'haydavies')

DC_output, eff_irrad_total, temp_cell, temp_air = DC_generation(POA,
                          PV_data,
                          installation_data,
                          temp_sensor='2nd weather_station',
                          shadow = 'True')

AC_output11, pac_log = AC_generation(DC_output, 
                          eff_irrad_total,
                          temp_cell,
                          temp_air,
                          installation_data['inverter'],
                          data,
                          model = 'Sandia')



inverter = installation_data['inverter']
#Inverter from CEC
CEC_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')
inverter = CEC_inverters[inverter] # This is the US version - wrong voltage and maybe more

#AC output from inverter
AC_CEC = pvlib.inverter.sandia(v_dc = DC_output.v_mp,
                                      p_dc = DC_output.p_mp,
                                      inverter=inverter)

#%%%




#%%% Plots




active_pos = data['INV-2-VBF Active power (kW)'][data['INV-2-VBF Active power (kW)']>0]

#Efficiency calculations
A_vertical_mono = PV_data['cell_height'] * PV_data['cell_width']* PV_data['cells_in_series']*installation_data['modules_per_string']*installation_data['strings_per_inverter']
eta = DC_output['p_mp'] / ((POA['POA front']*PV_data['bifaciality'] + POA['POA back'])*A_vertical_mono)

diff = ((DC_output['p_mp']/1000 - data['INV-2-VBF Active power (kW)'])/ (DC_output['p_mp']/1000))*100

from shadow import shadow
from draw_shadow import draw_shadow

eta_shadow= shadow(PV_data, installation_data, tz, data)

sunny_day = '2023-06-22 11:15:00'

sunny_index = pd.date_range('2023-05-12 11:10:00','2023-05-12 11:20:00',freq='5T', tz=tz)

L_horizontal = eta_shadow['L_horizontal'][sunny_day]
L_vertical = eta_shadow['L_vertical'][sunny_day]
solar_azimuth = eta_shadow['azimuth'][sunny_day]

draw_shadow(0, 0, PV_data['module_width'], PV_data['module_height'], L_vertical, -L_horizontal,solar_azimuth)






start_date = '2023-05-01 00:00:00'
end_date = '2023-05-18 00:00:00'

time_index_day = pd.date_range(start=start_date, 
                                 end=end_date, 
                                 freq='D',  
                                 tz=tz)
"""
for day in time_index_day:
    time_index = pd.date_range(start=day, 
                           periods=24*12*1, 
                           freq='5min',
                           tz=tz)

    #FG changes - plot of ref cells
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    ax0.plot(POA['POA fuel_in East'][time_index], 
              color='dodgerblue',
              label='Fuel_in east (W.m-2)')
    ax0.plot(data['Reference Cell Vertical East (W.m-2)'][time_index], 
              color='red',
              label='Reference Cell Vertical East (W.m-2)')
    ax0.plot(POA['POA fuel_in West'][time_index], 
              color='orange',
              label='Fuel_in west (W.m-2)')
    ax0.plot(data['Reference Cell Vertical West (W.m-2)'][time_index], 
              color='green',
              label='Reference Cell Vertical West (W.m-2)')
    ax0.set_ylim([0,1000])
    ax0.set_ylabel('Irradiance (W.m-2)')
    plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
    ax0.grid('--')
    ax0.legend()
    plt.savefig('Figures/daily_profiles/modelled_ref_cells_{}_{}_{}.jpg'.format(day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                dpi=100, bbox_inches='tight')    
"""

for day in time_index_day:
    time_index = pd.date_range(start=day, 
                           periods=24*12*1, 
                           freq='5min',
                           tz=tz)

    #FG changes - plot of ref cells
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    ax0.plot((DC_output['p_mp']/1000)[time_index], 
              color='dodgerblue',
              label='DC ')
    ax0.plot((DC_output_iso['p_mp']/1000)[time_index], 
              color='red',
              label='DC iso ')
    ax0.plot(data['INV-2-VBF Active power (kW)'][time_index], 
              color='green',
              label='Active power inverter kW, vertical')  
    #ax0.plot(diff[time_index], 
     #         color='red',
      #        label='mismatch')    
    ax0.set_ylim([0,40])
    ax0.set_ylabel('Irradiance (W.m-2)')
    plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
    ax0.grid('--')
    ax0.legend()
    plt.savefig('Figures/daily_profiles/modelled_DC_{}_{}_{}.jpg'.format(day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                dpi=100, bbox_inches='tight')    
    
    
    

    
    
    
"""
for day in time_index_day:
    time_index = pd.date_range(start=day, 
                           periods=24*12*1, 
                           freq='5min',
                           tz=tz)

    #FG changes - plot of ref cells
    plt.figure(figsize=(8, 6))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    ax0.plot(eta[time_index], 
              color='dodgerblue',
              label='Calculated efficiency')
   # ax0.plot(data['Reference Cell Vertical East (W.m-2)'][time_index], 
    ##         label='Reference Cell Vertical East (W.m-2)')
    #ax0.plot(POA['POA fuel_in West'][time_index], 
             # color='orange',
             # label='Fuel_in west (W.m-2)')
    #ax0.plot(data['Reference Cell Vertical West (W.m-2)'][time_index], 
     #         color='green',
      #        label='Reference Cell Vertical West (W.m-2)') 
    ax0.set_ylim([0,1])
    ax0.set_ylabel('Efficiency []')
    plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
    ax0.grid('--')
    ax0.legend()
    plt.savefig('Figures/daily_profiles/eta_{}_{}_{}.jpg'.format(day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                dpi=100, bbox_inches='tight')        

 
for day in time_index_day:
     time_index = pd.date_range(start=day, 
                            periods=24*12*1, 
                            freq='5min',
                            tz=tz)

     #FG changes - plot of ref cells
     plt.figure(figsize=(8, 6))
     gs1 = gridspec.GridSpec(1, 1)
     ax0 = plt.subplot(gs1[0,0])
    # ax0.plot(data['Reference Cell Vertical East (W.m-2)'][time_index], 
     ##         label='Reference Cell Vertical East (W.m-2)')
     #ax0.plot(POA['POA fuel_in West'][time_index], 
              # color='orange',
              # label='Fuel_in west (W.m-2)')
     #ax0.plot(data['Reference Cell Vertical West (W.m-2)'][time_index], 
      #         color='green',
       #        label='Reference Cell Vertical West (W.m-2)') 
     ax0.plot(diff[time_index], 
               color='red',
               label='mismatch')    
     ax0.set_ylim([0,100])
     ax0.set_ylabel('Irradiance (W.m-2)')
     plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
     ax0.grid('--')
     ax0.legend()
     plt.savefig('Figures/daily_profiles/modelled_DC_{}_{}_{}.jpg'.format(day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                 dpi=100, bbox_inches='tight')   
     
"""


#%%%

inv_eff_calculated = AC_CEC/DC_output.p_mp

active_pos = data['INV-2-VBF Active power (kW)'][data['INV-2-VBF Active power (kW)']>0]

# Calculations can only be made when all data is available. 
# now we find the common index of the inverter and ambient temperature

common_index = active_pos.index.intersection(temp_air.index)

time_inverter = common_index

inv_eff_data = data['INV-2-VBF Active power (kW)'] / data['INV-2-VBF Total input power (kW)']

x_data = eff_irrad_total[time_inverter]
x = np.nan_to_num(x_data, nan=0)
z = temp_cell[time_inverter]
y_data = inv_eff_data[time_inverter]
y = y_data.values.astype(float)

# Sample dataset
data_sample = {'X': x,
        'Y': y,
        'Z':z,
        'temp':temp_air[time_inverter]}

df = pd.DataFrame(data_sample)

# Remove data points where X is below 10
#df_filtered = df[df['X'] >= 10]
""" """
# Fit a 4th order polynomial
#coefficients = np.polynomial.Polynomial.fit(x_data, y_data, deg=4)

# Define the 4th order polynomial function
#fourth_order_polynomial = np.polynomial.Polynomial(coefficients)
#y_fit = fourth_order_polynomial(x_data)

""""""

def logarithmic_func1(x, a, b):
   return a + b * np.log(x)


popt, pcov = curve_fit(logarithmic_func1, x, y,maxfev=10000)


a_opt1, b_opt1 = popt

x_fit1 = np.linspace(min(x), max(x), 100)  # Generate x-values for the fitted curve
y_fit1 = logarithmic_func1(x_fit1, a_opt1, b_opt1)  # Evaluate the fitted curve


def inverter_efficiency_function(x):
    if 0 <= x <= 300:
        # Logarithmic function for values between 0 and 300
        return (logarithmic_func1(x, a_opt1, b_opt1))  
    else:
        # Fixed value for values above 300
        return 98  # You can replace this with your desired fixed value
    
    
    
def custom_function(series_input):
    # Apply the custom function to each element of the Series
    series_output = series_input.apply(lambda x: logarithmic_func1(x, a_opt1, b_opt1) if 0 <= x <= 300 else 98.4)

    return series_output     



inv_eff = (8*(custom_function(eff_irrad_total))+2*(inv_eff_calculated*100))/10
#inv_eff=custom_function(effective_irradiance_infinite_sheds)
inv_eff = inv_eff[time_inverter]
inv_eff = inv_eff[inv_eff>0]
x_inv_eff = eff_irrad_total[inv_eff.index] #Effective irradiance when the calculated inverter efficiency is above 0


def invert_log_function(eff_irrad,inverter_eff,p_dc1):
   inv_eff1 = ((8*(custom_function(eff_irrad))+2*(inverter_eff*100))/10)/100
   p_ac = inv_eff1*p_dc1
   #if p_ac>40000:
    #   return 40000
   #else:
   return p_ac
   
p_ac_log = invert_log_function(eff_irrad_total,inv_eff_calculated,DC_generation.p_mp )
p_ac_log = p_ac_log.fillna(0)