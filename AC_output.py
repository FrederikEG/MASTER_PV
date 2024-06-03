# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 09:25:39 2024

@author: frede
"""

def AC_generation(DC_generation,eff_irrad_total,temp_cell,temp_air,inverter_CEC,data,model, common_index):
    
    import pvlib
    import numpy as np
    import pandas as pd
    from scipy.optimize import curve_fit
    
    """Calculates the generated AC from the DC generation
    
    Parameters
    -------
    DC generation : 
        Series with the scaled DC generation.
        
            
    Model :
        Specifies the model used to calculate the AC             
 
    
    Installation_data :  
        dict containing the data for the installation  

    Returns
    -------
    AC_output : 
        Output is a series with the generated AC  
    """
    
    
    #Inverter from CEC
    CEC_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')
    inverter = CEC_inverters['Huawei_Technologies_Co___Ltd___SUN2000_40KTL_US__480V_'] # This is the US version - wrong voltage and maybe more

    #AC output from inverter
    AC_CEC = pvlib.inverter.sandia(v_dc = DC_generation.v_mp,
                                          p_dc = DC_generation.p_mp,
                                          inverter=inverter)
    

    inv_eff_calculated = AC_CEC/DC_generation.p_mp
    

    
    #%%%
    
    if model == 'custom' :
        # Sample data points
        
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
        df_filtered = df[df['X'] >= 10]
        """ """
        # Fit a 4th order polynomial
        coefficients = np.polynomial.Polynomial.fit(x_data, y, deg=4)
        
        # Define the 4th order polynomial function
        fourth_order_polynomial = np.polynomial.Polynomial(coefficients)
        y_fit = fourth_order_polynomial(x_data)
        
        """"""
        
        def logarithmic_func1(x, a, b):
           return a + b * np.log(x)
        
        
        popt, pcov = curve_fit(logarithmic_func1, df_filtered['X'], df_filtered['Y'],maxfev=10000)
        
        
        a_opt1, b_opt1 = popt
        
        x_fit1 = np.linspace(min(df_filtered['X']), max(df_filtered['X']), 100)  # Generate x-values for the fitted curve
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
            
          
     
    if model == 'Sandia':    
        AC_output = AC_CEC
    elif model == 'custom':
        AC_output =  p_ac_log     
    return AC_output     
