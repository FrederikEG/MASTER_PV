# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 11:38:07 2024

@author: frede
"""

def iam_custom(DC_mid_rows_measure, DC_mid_rows, aoi_west, solar_position, day):
    
    """Calculates a custom iam based on difference between modelled and measure DC p_mp output.
    The iam is for now diffined as an additional iam that should be applied when 
    calculating the fuel-in/ effective irradiance. 
    
    Parameters
    -------
    DC_mid_rows_measure : 
        Series of the measured DC p_mp from the two middel rows. 
            
    
    DC_mod_rows :  
        DataFrame containing the modelled DC output.   

    Day :
        The day for which the iam is diffiend.  

    Returns
    -------
    iam_custom : 
        Series with the the custom iam.
    
    """
    
    import pandas as pd
    import numpy as np
    from collections import OrderedDict
    DC_diff = (DC_mid_rows_measure - DC_mid_rows['p_mp']/1000)/(DC_mid_rows['p_mp']/1000)
    iam_cus = DC_mid_rows_measure/(DC_mid_rows['p_mp']/1000)
    #DC_diff = DC_diff[solar_position['azimuth']>180]
    tz = 'UTC'
    time_index = pd.date_range(start=day, 
                           periods=24*12*1, 
                           freq='5min',
                           tz=tz)
    
    
    iam_cus = iam_cus[time_index]
    iam_cus = iam_cus.replace([np.inf, np.nan], 1)
    iam_cus[(iam_cus > 1.3) | (iam_cus < 0.7)] = 1
    solar_azimuth = solar_position['azimuth'][time_index]
    
    iam_cus = iam_cus[(solar_azimuth>180) & (solar_azimuth<300)]
    iam_cus = iam_cus.reindex(time_index, fill_value=1)
    
    #solar_azimuth = solar_azimuth[iam_cus.index]

    
    iam_dict = OrderedDict()
    iam_dict['iam custom'] = iam_cus
    iam_dict['solar azimuth'] = solar_azimuth
    
    iam_dict = pd.DataFrame(iam_dict)
    

    # Should be made so it will write a csv file from which the
    # costum iam can be looked up. 
    
    # Maybe different iam should be made to represent different atmospheric conditions.
    

    
    return DC_diff, iam_cus, iam_dict



def iam_custom_read(iam_dict, solar_position):
    import numpy as np

    def find_closest_index(value):
        return np.abs(iam_dict['solar azimuth'] - value).idxmin()
    
    # Search for the closest match in df_short for each value in df_long
    solar_position['closest_index'] = solar_position['azimuth'].apply(find_closest_index)
    solar_pot = solar_position
    best_index = solar_position['azimuth'].apply(find_closest_index)
    iam_custom = iam_dict['iam custom'][best_index]
    
    
    return solar_pot, iam_custom


def iam_custom_days(DC_mid_rows_measure, DC_mid_rows, aoi_west, solar_position, days):
    
    """Calculates a custom iam based on difference between modelled and measure DC p_mp output.
    The iam is for now diffined as an additional iam that should be applied when 
    calculating the fuel-in/ effective irradiance. 
    
    Parameters
    -------
    DC_mid_rows_measure : 
        Series of the measured DC p_mp from the two middel rows. 
            
    
    DC_mod_rows :  
        DataFrame containing the modelled DC output.   

    Day :
        The day for which the iam is diffiend.  

    Returns
    -------
    iam_custom : 
        Series with the the custom iam.
    
    """
    
    import pandas as pd
    import numpy as np
    from collections import OrderedDict
    DC_diff = (DC_mid_rows_measure - DC_mid_rows['p_mp']/1000)/(DC_mid_rows['p_mp']/1000)
    iam_cus = DC_mid_rows_measure/(DC_mid_rows['p_mp']/1000)
    #DC_diff = DC_diff[solar_position['azimuth']>180]
    
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
    iam_cus[(iam_cus > 1.3) | (iam_cus < 0.7)] = 1
    solar_azimuth = solar_position['azimuth'][time_index_test2]
    
    iam_cus = iam_cus[(solar_azimuth>180) & (solar_azimuth<300)]
    iam_cus = iam_cus.reindex(time_index_test2, fill_value=1)
    #iam_cus_result = iam_cus

#solar_azimuth = solar_azimuth[iam_cus.index]


    iam_dict = OrderedDict()
    iam_dict['iam custom'] = iam_cus
    iam_dict['solar azimuth'] = solar_azimuth
    
    iam_dict = pd.DataFrame(iam_dict)
    

    # Should be made so it will write a csv file from which the
    # costum iam can be looked up. 
    
    # Maybe different iam should be made to represent different atmospheric conditions.
    

    
    return iam_dict

import pandas as pd
days = ['2023-05-12 00:00:00', '2023-06-14 00:00:00']
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
