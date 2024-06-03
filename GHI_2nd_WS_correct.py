# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 16:32:23 2024

@author: frede
"""

def GHI_2nd_WS_correct(data):
    import pandas as pd
    import numpy as np
    data.index = pd.to_datetime(data.index, utc=True) 


    GHI_2nd = pd.to_numeric(data[('GHI_2nd station (W.m-2)')])
    GHI_2nd = GHI_2nd.dropna()
    GHI_2nd = GHI_2nd.asfreq('5T', method='ffill')
    GHI_2nd.index = GHI_2nd.index - pd.Timedelta(hours=1) #Shifted one hour

        

    GHI = pd.to_numeric(data[('GHI (W.m-2)')])[GHI_2nd.index]
    #GHI_SPN1 = pd.to_numeric(data[('GHI_SPN1 (W.m-2)')])[GHI_2nd.index]
    #ref_up = data['Reference Cell Tilted facing up (W.m-2)']

    GHI_hour = GHI.resample('H').mean()
   # GHI_SPN1_hour = GHI_SPN1.resample('H').mean()
    #ref_up_hour = data['Reference Cell Tilted facing up (W.m-2)'].resample('H').mean()


    GHI_5min = GHI_hour.asfreq('5T', method='ffill')
    #GHI_SPN1_5min = GHI_SPN1_hour.asfreq('5T', method='ffill')
    #ref_up_5min = ref_up_hour.asfreq('5T', method='ffill')


    mag_factor = GHI_2nd/GHI_5min
    mag_factor.replace([np.inf, -np.inf, np.nan], 1, inplace=True)

    mag_factor_smooth = mag_factor.rolling(window=12, min_periods=1).mean()

    GHI_mag = GHI*mag_factor_smooth
    
    #GHI = (GHI + GHI_mag)/2
    #GHI = GHI.reindex(data.index)
    return mag_factor_smooth 