# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 14:41:21 2024

@author: frede
"""
import pandas as pd
data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True)

# Plots for sunny and cloudy days
sun_cloud_days = ['2023-05-12 00:00:00', '2023-05-17 00:00:00']



import pandas as pd
data=pd.read_csv('resources/clean_data.csv',
                 index_col=0)

data.index = pd.to_datetime(data.index, utc=True) 

#def daily_plots():
def daily_plots(Title, y_label, value1, value2, value3, value4, value5, start_date, end_date, model_to_run, y_lim, model_explain = False):   
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec 
    import numpy as np
    
    filtered1 = value1.replace([np.nan, np.inf, -np.inf], np.nan)
    filtered2 = value2.replace([np.nan, np.inf, -np.inf], np.nan)
    y_max1 = np.nanmax(filtered1)
    y_max2 = np.nanmax(filtered2)
    #y_lim = max(y_max1,y_max2) + 5


    tz='UTC' 
    time_index_day = pd.date_range(start=start_date, 
                                     end=end_date, 
                                     freq='D',  
                                     tz=tz)

    
    for day in time_index_day:
        time_index = pd.date_range(start=day, 
                               periods=24*12*1, 
                               freq='5min',
                               tz=tz)
        
        #power generation inverter
        plt.figure(figsize=(8, 6))
        gs1 = gridspec.GridSpec(1, 1)
        ax0 = plt.subplot(gs1[0,0])
        ax0.plot(value1[time_index], 
                  color='dodgerblue',
                  label=value1.name)
        ax0.plot(value2[time_index], 
                  color='firebrick',
                  label=value2.name)
        ax0.plot(value3[time_index], 
                  color='blue',
                  label=value3.name)
        ax0.plot(value4[time_index], 
                  color='green',
                  label=value4.name)
        ax0.plot(value5[time_index], 
                  color='purple',
                  label=value5.name)
        ax0.set_ylim([0,y_lim])
        ax0.set_ylabel(y_label)
        plt.title(Title)
        plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
        ax0.grid('--')
        ax0.legend()
        
        #Adds explination on the model that has been run
        model_explain_function(model_explain, model_to_run)
        
        plt.savefig('Figures/daily_profiles/{}_{}_{}_{}.jpg'.format(Title, day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                    dpi=100, bbox_inches='tight')
        """
        #power generation per string
        plt.figure(figsize=(8, 6))
        gs1 = gridspec.GridSpec(1, 1)
        ax0 = plt.subplot(gs1[0,0])
        for i in ['1', '2', '3', '4']:
            ax0.plot(0.001*data['VBF PV{} input voltage (V)'.format(i)][time_index]*data['VBF PV{} input current (A)'.format(i)][time_index], 
                 label='VBF PV{} power (kW)'.format(i))
        
        ax0.set_ylim([0,10])
        ax0.set_xlim(time_index[0], time_index[-1])
        ax0.set_ylabel('DC Power (kW)')
        plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
        ax0.grid('--')
        ax0.legend()
        plt.savefig('Figures/daily_profiles/strings_vertical_{}_{}_{}.jpg'.format(day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                    dpi=100, bbox_inches='tight')
        """
    #return time_index_day, y_max1
#example use

"""
time_day, y_max1 = daily_plots('Power generation test', 
            'DC Power (kW)',
            data['INV-1-TBF Total input power (kW)'], 
            data['INV-2-VBF Total input power (kW)'], 
            '2023-05-05 00:00:00', 
            '2023-05-10 00:00:00')
"""

#def daily_plots():
def day_plot(Title, y_label, days, path=False, save_plots=False, model_to_run = False,poa_direct=False, poa_sky_diffuse=False, poa_ground_diffuse=False, poa_global=False, model_explain = False, value1=1, value2=1, value3=1, value4=1, value5=1, y_lim = 'default', custom_label = False, zoom = False, solar_position = False, y_lines = False, custom_yline = False):   
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec 
    import numpy as np
    import statistics
    import math

    tz='UTC' 
    
    #Font sizes
    label_size = 20
    text_size = 16
    title_size = 24
    text_size = 16
    tick_size = 16
    legend_size = 16
    pad = 20 # Distance between plot and title
    font_type = 'Arial'
    
    #sunny_day = '2023-05-05 00:00:00'
    #cloudy_day = '2023-05-10 00:00:00'
    #days = [sunny_day, cloudy_day]
    time_index_day = pd.to_datetime(days)
    
    
    color1 = 'dodgerblue'
    color2 = 'firebrick'
    color3 = 'green'
    color4 = 'purple'
    color5 = 'red'

   
    
#calculates appropiate y_lim if no input given
    if y_lim == 'default':
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
        # The ylim is based on the highest values and rounded to the next 5    
        filt_1 = value1[time_index_test2]
        filt_2 = value2[time_index_test2]
        filtered1 = filt_1.replace([np.nan, np.inf, -np.inf], 0)
        filtered2 = filt_2.replace([np.nan, np.inf, -np.inf], 0)
        sorted_series1 = sorted(filtered1, reverse=True)
        sorted_series2 = sorted(filtered2, reverse=True)
        y_10_max1 = sorted_series1[:3]
        y_10_max2 = sorted_series2[:3]
        y_max1 = statistics.median(y_10_max1)
        y_max2 = statistics.median(y_10_max2)
        y_max = max(y_max1,y_max2)
        if y_max<50:
            y_lim = math.ceil( y_max/ 5.0)
            # Multiply the result by 5
            y_lim *= 5
        elif 50<= y_max <= 400:
            y_lim = math.ceil( y_max/ 50)
            # Multiply the result by 5
            y_lim *= 50
        elif y_max>400:
            y_lim = math.ceil( y_max/ 100)
            # Multiply the result by 5
            y_lim *= 100
        


    if custom_label ==False:
        if isinstance(value1, int):
            value1_label = 'int'
        else: 
            value1_label = value1.name
            
        if isinstance(value2, int):
            value2_label = 'int'
        else: 
            value2_label = value2.name
        
        if isinstance(value3, int):
            value3_label = 'int'
        else: 
            value3_label = value3.name
            
        if isinstance(value4, int):
            value4_label = 'int'
        else: 
            value4_label = value4.name
            
        if isinstance(value5, int):
            value5_label = 'int'
        else: 
            value5_label = value5.name
            
    elif isinstance(custom_label, list):
        value1_label = custom_label[0]
        value2_label = custom_label[1]
        value3_label = custom_label[2]
        value4_label = custom_label[3]
        value5_label = custom_label[4]
        
    
    for day in time_index_day:
        time_index = pd.date_range(start=day, 
                               periods=24*12*1, 
                               freq='5min',
                               tz=tz)
        
        #power generation inverter
        plt.figure(figsize=(10, 6))
        gs1 = gridspec.GridSpec(1, 1)
        ax0 = plt.subplot(gs1[0,0])
        ax0.set_ylim([0,y_lim])
        if isinstance(value1, pd.Series) and not isinstance(value2, pd.Series) and not isinstance(value3, pd.Series) and not isinstance(value4, pd.Series) :
            ax0.plot(value1[time_index], 
                      color=color1,
                      label= value1_label)
            
        if isinstance(value1, pd.Series) and  isinstance(value2, pd.Series) and not isinstance(value3, pd.Series) and not isinstance(value4, pd.Series):
            ax0.plot(value1[time_index], 
                      color=color1,
                      label=value1_label)
            ax0.plot(value2[time_index], 
                      color=color2,
                      label=value2_label)
            
        if isinstance(value1, pd.Series) and  isinstance(value2, pd.Series) and isinstance(value3 , pd.Series) and not isinstance(value4, pd.Series):
            ax0.plot(value1[time_index], 
                      color=color1,
                      label=value1_label)
            ax0.plot(value2[time_index], 
                      color=color2,
                      label=value2_label) 
            ax0.plot(value3[time_index], 
                      color=color3,
                      label=value3_label) 
        if isinstance(value1, pd.Series) and  isinstance(value2, pd.Series) and isinstance(value3 , pd.Series) and isinstance(value4, pd.Series) and not isinstance(value5, pd.Series):
            ax0.plot(value1[time_index], 
                      color=color1,
                      label=value1_label)
            ax0.plot(value2[time_index], 
                      color=color2,
                      label=value2_label) 
            ax0.plot(value3[time_index], 
                      color=color3,
                      label=value3_label) 
            ax0.plot(value4[time_index], 
                      color=color4,
                      label=value4_label) 
            
            
            
        if isinstance(value1, pd.Series) and  isinstance(value2, pd.Series) and isinstance(value3 , pd.Series) and isinstance(value4, pd.Series) and isinstance(value5, pd.Series):
            ax0.plot(value1[time_index], 
                      color=color1,
                      label=value1_label)
            ax0.plot(value2[time_index], 
                      color=color2,
                      label=value2_label) 
            ax0.plot(value3[time_index], 
                      color=color3,
                      label=value3_label) 
            ax0.plot(value4[time_index], 
                      color=color4,
                      label=value4_label)
            ax0.plot(value5[time_index], 
                      color=color5,
                      label=value5_label)
            
        # Colors the background with components of the irradiance     
        if isinstance(poa_direct, pd.Series) and  isinstance(poa_sky_diffuse, pd.Series) and isinstance(poa_ground_diffuse, pd.Series) and  isinstance(poa_global, pd.Series):
            import seaborn as sns
            colors = sns.color_palette('muted')
            
            
            direct_percent = (poa_direct[time_index]/poa_global[time_index])*100
            sky_diffuse_percent = (poa_sky_diffuse[time_index]/poa_global[time_index])*100
            ground_diffuse_percent = (poa_ground_diffuse[time_index]/poa_global[time_index])*100
            
            #Added together
            sky_direct = direct_percent + sky_diffuse_percent
            sky_direct_ground = direct_percent + sky_diffuse_percent + ground_diffuse_percent
             
            ax2 = ax0.twinx()

            
            ax2.plot(direct_percent, label='direct')
            ax2.fill_between(time_index, 0, direct_percent, color=colors[0], alpha=0.4)  # Fill color below the line
            ax2.plot(sky_direct, label='sky_diffuse')
            ax2.fill_between(time_index, direct_percent, sky_direct, color=colors[1], alpha=0.4)
            ax2.plot(sky_direct_ground, label = 'ground_diffuse')
            ax2.fill_between(time_index, sky_direct, sky_direct_ground, color=colors[2], alpha=0.4)
            ax2.legend()
            ax2.set_ylim([0,100])
            ax2.set_ylabel('Percentage')
            plt.tight_layout()
            
        
        # Adds a x-axis in the top of the plot with the solar azimuth
        if isinstance(solar_position, pd.Series):
            if y_lines == True and solar_position.name == 'azimuth': # Plots vertical lines when the sun reaces east, south and west
                #time_index_start = pd.date_range(day, 
                 #                    periods=1, 
                  #                   freq='5min',
                   #                  tz=tz)
              
                #time_index_end = time_index_start + pd.DateOffset(days=1)
                #ax3 = ax0.twiny()
             
                #ax3.set_xlim(solar_position[time_index_start], solar_position[time_index_end])
                #ax3.plot(solar_position[time_index],solar_position[time_index], alpha=1 )
                #if y_lines == True and solar_position.name == 'azimuth':
                 #   ax3.axvline(x=90, color='black', linestyle = '--')
                  #  ax3.axvline(x=180, color='black', linestyle = '--')
                   # ax3.axvline(x=270, color='black', linestyle = '--')
                    #ax3.set_xlabel('Solar azimuth')
                    
                    noon = solar_position[time_index]
                    noon_90 = noon[solar_position>90]
                    noon_180 = noon[solar_position>180]
                    noon_270 = noon[solar_position>270]
                    ax0.axvline(noon_270.index[0], color='black', linestyle = '--')
                    ax0.axvline(noon_180.index[0], color='black', linestyle = '--')
                    ax0.axvline(noon_90.index[0], color='black', linestyle = '--')
                    ax0.text(noon_270.index[0], 0.05*y_lim, 'W', fontsize=8, ha='center', va='center', family='sans-serif', 
                             bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
                    ax0.text(noon_180.index[0], 0.05*y_lim, 'S', fontsize=8, ha='center', va='center', family='sans-serif', 
                             bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
                    ax0.text(noon_90.index[0], 0.05*y_lim, 'E', fontsize=8, ha='center', va='center', family='sans-serif', 
                             bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
            # Draws vertical lines when the solar elevation goes above and below 10deg
            if y_lines == True and solar_position.name == 'elevation':              
                #ax4 = ax0.twinx()
                elev = solar_position[time_index]
                elev10 = elev[elev>10]
                #ax4.plot(solar_position[elev10.index], color='red', alpha=1)
                ax0.axvline(elev10.index[0], color='black', linestyle = '--')
                ax0.axvline(elev10.index[-1], color='black', linestyle = '--')
                ax0.text(elev10.index[0], 0.8, 'Solar \nelevation \n10°', fontsize=12, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
                ax0.text(elev10.index[-1], 0.8, 'Solar \nelevation \n10°', fontsize=12, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
            # Draws ann vertical line at a customset offset
            if isinstance(custom_yline, pd.DateOffset) and solar_position.name == 'azimuth':
                time_index_start = pd.date_range(day, 
                                     periods=1, 
                                     freq='5min',
                                     tz=tz)
                time_index_end = time_index_start + custom_yline
                ax0.axvline(time_index_end, color='red', linestyle = '--')
            
            # Draws an vertical line when the value is at its maximum value    
            if custom_yline =='value1' and solar_position.name == 'azimuth':
                index_of_highest_value = value1[time_index].idxmax()
                ax0.axvline(index_of_highest_value, color='red', linestyle = '--')
            if custom_yline =='value2' and solar_position.name == 'azimuth':
                index_of_highest_value = value2[time_index].idxmax()
                ax0.axvline(index_of_highest_value, color='red', linestyle = '--')
            if custom_yline =='value3' and solar_position.name == 'azimuth':
                index_of_highest_value = value3[time_index].idxmax()
                ax0.axvline(index_of_highest_value, color='red', linestyle = '--')
            if custom_yline =='value4' and solar_position.name == 'azimuth':
                index_of_highest_value = value4[time_index].idxmax()
                ax0.axvline(index_of_highest_value, color='red', linestyle = '--')
         
            
            
                
                 
            #if y_lines == True and solar_position.name == 'elevation': 
             #   ax3.axvline(x=10, color='black', linestyle = '--')
              #  ax3.set_xlabel('Solar elevation')

                    
            
            """   
           ax3.text(180, y_lim - 100, 'S', fontsize=12, ha='center', va='center', family='sans-serif', 
    bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle,pad=0.5'))
           ax3.text(90, y_lim-100, 'E', fontsize=12, ha='center', va='center', family='sans-serif', 
    bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle,pad=0.5'))
           ax3.text(270, y_lim-100, 'W', fontsize=12, ha='center', va='center', family='sans-serif', 
    bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle,pad=0.5'))
           """       
                
                



                

       
        ax0.set_ylabel(y_label, fontsize=label_size)
        plt.title(Title, fontsize=title_size)
        plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
        ax0.grid('--')
        ax0.legend(fontsize=legend_size)
    
        ax0.set_xlabel('Date', fontsize=label_size)
        ax0.tick_params(axis='both', which='major', labelsize=tick_size)
        #Zoom on the specified interval
        if zoom == False:
            ax0.set_xlim(pd.Timestamp(day), pd.Timestamp(day + pd.Timedelta(days=1)))
        else:
            ax0.set_xlim(pd.Timestamp(day) + pd.Timedelta(hours=zoom[0]), pd.Timestamp(day + pd.Timedelta(hours=zoom[1])))
        
        #Adds explination on the model that has been run
        model_explain_function(model_explain, model_to_run)
        
        if save_plots == True:
            plt.savefig(path+'/{}_{}_{}_{}.png'.format(Title, day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                        dpi=100, bbox_inches='tight',format = 'png')
        
        plt.savefig('Figures/day_profiles/{}_{}_{}_{}.jpg'.format(Title, day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                    dpi=100, bbox_inches='tight')
        


#def daily_plots():
def scatter_plot_old(Title, y_label, x_label, modelled_value, measured_value,start_date=False, end_date = False, time_index = False, solar_position = False, model_to_run = False, model_explain = False,interval = 'false', color_value='blue', y_lim = 'default', regression_line = True, color_interval = 'total', elevation_min = False, lower_limit = False):   
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec 
    import numpy as np
    import statistics
    import math
    
    #Font sizes
    label_size = 16
    text_size = 16
    title_size = 20
    text_size = 12
    tick_size = 14
    pad = 20 # Distance between plot and title
    font_type = 'Arial'


    
    tz='UTC' 
    
    

    
                  
    
    if y_lim == 'default':

        # The ylim is based on the highest values and rounded to the next 5    
        filt_1 = modelled_value[time_index]
        filt_2 = measured_value[time_index]
        filtered1 = filt_1.replace([np.nan, np.inf, -np.inf], 0)
        filtered2 = filt_2.replace([np.nan, np.inf, -np.inf], 0)
        sorted_series1 = sorted(filtered1, reverse=True)
        sorted_series2 = sorted(filtered2, reverse=True)
        y_10_max1 = sorted_series1[:3]
        y_10_max2 = sorted_series2[:3]
        y_max1 = statistics.median(y_10_max1)
        y_max2 = statistics.median(y_10_max2)
        y_max = max(y_max1,y_max2)
        if y_max<50:
            y_lim = math.ceil( y_max/ 5.0)
            # Multiply the result by 5
            y_lim *= 5
        elif 50<= y_max <= 400:
            y_lim = math.ceil( y_max/ 50)
            # Multiply the result by 5
            y_lim *= 50
        elif y_max>400:
            y_lim = math.ceil( y_max/ 100)
            # Multiply the result by 5
            y_lim *= 100
    
    
    """
    #power generation inverter
    plt.figure(figsize=(8, 8))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    ax0.plot([0,1000],[0, 1000], linewidth=3, color='black')
    ax0.scatter(modelled_value[time_index], measured_value[time_index], 
              color='blue')
    plt.title(Title)
    ax0.set_xlim([0,y_lim])
    ax0.set_ylim([0,y_lim])
    ax0.set_ylabel(y_label)
    ax0.set_xlabel(x_label)
    """
    
    ####
    if isinstance(solar_position, pd.DataFrame):
        solar_position = solar_position.loc[time_index]
        
        if interval == 'morning':
            #Time index excluding the periode where the genration is dominated 
            #by the east side
            if isinstance(elevation_min, float):
                scat_index = solar_position[(solar_position['azimuth']<=180) & (solar_position['elevation']>elevation_min)].index
            elif elevation_min ==False:
                scat_index = solar_position[(solar_position['azimuth']<=180)]
        elif interval == 'noon':
            scat_index = solar_position[(solar_position['azimuth']>=135) & (solar_position['azimuth']<=225)].index
        elif interval == 'afternoon':
            if isinstance(elevation_min, float):
                scat_index = solar_position[(solar_position['azimuth']>180) & (solar_position['elevation']>elevation_min)].index
            elif elevation_min ==False:
                scat_index = solar_position[(solar_position['azimuth']>180)].index
        elif interval == 'false':
            if elevation_min != False:
                scat_index =  solar_position[(solar_position['elevation']>elevation_min)].index
            #if elevation_min == False:
            else:
                scat_index = time_index
    else:
        scat_index = time_index
     
        
     

    #The afternoon azimuth angles are chosen to be roughly midway between the
    #peak and vally of the DC generation on 12th May 2023. 
    
    #The morning interval can also include data point for the same 
    #day around midnight since the solar morning azimuth=0 can be withing
    #that day. It doesn't matter since there will be no generation at midnight. 
    
    ########
        
    
    #power generation inverter
    plt.figure(figsize=(8, 8))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    ax0.plot([0,y_lim],[0, y_lim], linewidth=3, color='black', label = 'identity line')
        
    
    if isinstance(color_value, pd.Series):
        if color_value.name == 'azimuth':
            if interval == 'morning' and color_interval =='specific':
                vmin = 0
                vmax = 180
            elif interval == 'noon' and color_interval =='specific':
                vmin = 130
                vmax = 215
            elif interval == 'afternoon' and color_interval =='specific':
                vmin = 180
                vmax = 360
            elif color_interval =='total':
                vmin = 0
                vmax = 360
                # Plots scatter with color limits from azimuth
            sc = ax0.scatter(modelled_value[scat_index], measured_value[scat_index],c = color_value[scat_index], cmap = 'jet',alpha=0.5, vmin=vmin, vmax=vmax)

        else: 
            sc = ax0.scatter(modelled_value[scat_index], measured_value[scat_index],c = color_value[scat_index], cmap = 'jet',alpha=0.5)
        
        # Adding a color bar
        cbar = plt.colorbar(sc)
        cbar.set_label(str(color_value.name), fontsize=label_size)
        # Adjust the font size of the colorbar's tick labels
        cbar.ax.tick_params(labelsize=tick_size)  # Set the font size here
        
    if isinstance(color_value, str):
        ax0.scatter(modelled_value[scat_index], measured_value[scat_index], 
                  color=color_value,alpha=0.5)
        
    #RMSE = math.sqrt(np.square(np.subtract(modelled_value[scat_index],measured_value[scat_index])).mean())
    #nRMSE = RMSE/modelled_value[scat_index].mean()
    
    
    nRMSE = calculate_nrmse(modelled_value[scat_index],measured_value[scat_index])
    
    
    # Calculate the residuals
    residuals = measured_value[scat_index] - modelled_value[scat_index]
    
    # Calculate the total sum of squares
    total_sum_of_squares = np.sum((measured_value[scat_index] - np.mean(measured_value[scat_index]))**2)
    
    # Calculate the residual sum of squares
    residual_sum_of_squares = np.sum(residuals**2)
    
    # Calculate R^2
    r_sq = 1 - (residual_sum_of_squares / total_sum_of_squares)
    
    

    
    if start_date == False:
        start_date = time_index[0]
        end_date = time_index[-1]
        start_string = start_date.strftime('%Y-%m-%d')
        end_string = end_date.strftime('%Y-%m-%d')
    else:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            start_string = start_date.strftime('%Y-%m-%d')
            end_string = end_date.strftime('%Y-%m-%d')

    ax0.text(0.05, 0.95, 'nRMSE = ' + str(round(nRMSE*100,1))+'%', 
         transform=ax0.transAxes, fontsize=text_size)
    ax0.text(0.05, 0.90, '# data points = ' + str(len(scat_index)), 
         transform=ax0.transAxes, fontsize=text_size)
    ax0.text(0.05, 0.85, 'interval = ' + str(interval), 
         transform=ax0.transAxes, fontsize=text_size)
    ax0.text(0.05, 0.80, 'Period = ' + str(start_string) + ' to ' + str(end_string), 
         transform=ax0.transAxes, fontsize=text_size)
    ax0.text(0.05, 0.75, 'r_sq = ' + str(round(r_sq,3)), 
         transform=ax0.transAxes, fontsize=text_size)
    plt.title(Title, fontsize=title_size, pad=pad, fontname=font_type)
    ax0.set_xlim([0,y_lim])
    ax0.set_ylim([0,y_lim])
    ax0.set_ylabel(y_label, fontsize=label_size)
    ax0.set_xlabel(x_label, fontsize=label_size)
    # Set the font size of tick labels on both axes
    ax0.tick_params(axis='both', which='major', labelsize=tick_size)
    
    
    #Adds explination on the model that has been run
    model_explain_function(model_explain, model_to_run)
    if regression_line == True:
        R_sqared, m, b = reg_line(modelled_value, measured_value, scat_index, regression_line)
        ax0.text(0.05, 0.70, 'R^2 = ' + str(round(R_sqared,3)), 
             transform=ax0.transAxes, fontsize=text_size)
        
        
    fit_dict = {'nRMSE':nRMSE*100,
                '# data points':len(scat_index),
                'R^2':round(R_sqared,3),
                'slope':m,
                'offset':b}    
    return scat_index, fit_dict
    




#def daily_plots():
def scatter_plot(Title, y_label, x_label, modelled_value, measured_value,start_date=False, end_date = False, time_index = False, solar_position = False, model_to_run = False, model_explain = False,interval = 'false', color_value='blue', y_lim = 'default', regression_line = True, color_interval = 'total', elevation_min = False, lower_limit = False):   
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec 
    import numpy as np
    import statistics
    import math
    
    #Font sizes
    label_size = 16
    text_size = 16
    title_size = 20
    text_size = 12
    tick_size = 14
    pad = 20 # Distance between plot and title
    font_type = 'Arial'


    
    tz='UTC' 
    
    

    
                  
    
    if y_lim == 'default':

        # The ylim is based on the highest values and rounded to the next 5    
        filt_1 = modelled_value[time_index]
        filt_2 = measured_value[time_index]
        filtered1 = filt_1.replace([np.nan, np.inf, -np.inf], 0)
        filtered2 = filt_2.replace([np.nan, np.inf, -np.inf], 0)
        sorted_series1 = sorted(filtered1, reverse=True)
        sorted_series2 = sorted(filtered2, reverse=True)
        y_10_max1 = sorted_series1[:3]
        y_10_max2 = sorted_series2[:3]
        y_max1 = statistics.median(y_10_max1)
        y_max2 = statistics.median(y_10_max2)
        y_max = max(y_max1,y_max2)
        if y_max<50:
            y_lim = math.ceil( y_max/ 5.0)
            # Multiply the result by 5
            y_lim *= 5
        elif 50<= y_max <= 400:
            y_lim = math.ceil( y_max/ 50)
            # Multiply the result by 5
            y_lim *= 50
        elif y_max>400:
            y_lim = math.ceil( y_max/ 100)
            # Multiply the result by 5
            y_lim *= 100
    
    
    """
    #power generation inverter
    plt.figure(figsize=(8, 8))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    ax0.plot([0,1000],[0, 1000], linewidth=3, color='black')
    ax0.scatter(modelled_value[time_index], measured_value[time_index], 
              color='blue')
    plt.title(Title)
    ax0.set_xlim([0,y_lim])
    ax0.set_ylim([0,y_lim])
    ax0.set_ylabel(y_label)
    ax0.set_xlabel(x_label)
    """
    
    ####
    if isinstance(solar_position, pd.DataFrame):
        solar_position = solar_position.loc[time_index]
        
        if interval == 'morning':
            #Time index excluding the periode where the genration is dominated 
            #by the east side
            if isinstance(elevation_min, float):
                scat_index = solar_position[(solar_position['azimuth']<=180) & (solar_position['elevation']>elevation_min)].index
            elif elevation_min ==False:
                scat_index = solar_position[(solar_position['azimuth']<=180)]
        elif interval == 'noon':
            scat_index = solar_position[(solar_position['azimuth']>=135) & (solar_position['azimuth']<=225)].index
        elif interval == 'afternoon':
            if isinstance(elevation_min, float):
                scat_index = solar_position[(solar_position['azimuth']>180) & (solar_position['elevation']>elevation_min)].index
            elif elevation_min ==False:
                scat_index = solar_position[(solar_position['azimuth']>180)].index
        elif interval == 'noon_exclude':
            if isinstance(elevation_min, float):
                long_index =  solar_position[(solar_position['elevation']>elevation_min)].index
                short_index = solar_position[(solar_position['azimuth']>=135) & (solar_position['azimuth']<=230)].index
                scat_index = long_index.difference(short_index)
            elif elevation_min ==False:
                long_index = time_index
                scat_index = solar_position[(solar_position['azimuth']>=135) & (solar_position['azimuth']<=230)].index
                scat_index = long_index.difference(short_index)
        elif interval == 'false':
            if elevation_min != False:
                scat_index =  solar_position[(solar_position['elevation']>elevation_min)].index
            #if elevation_min == False:
            else:
                scat_index = time_index
    else:
        scat_index = time_index
     
    modelled_value = modelled_value[scat_index]
    measured_value = measured_value[scat_index]
    
    #Filters out times where either modelled of measured or both are nan
    no_nan_indices = modelled_value.notna() & measured_value.notna()  # Find indices where both are not NaN
    modelled_value = modelled_value[no_nan_indices]
    measured_value = measured_value[no_nan_indices]

  
    scat_index = modelled_value.index
    #The afternoon azimuth angles are chosen to be roughly midway between the
    #peak and vally of the DC generation on 12th May 2023. 
    
    #The morning interval can also include data point for the same 
    #day around midnight since the solar morning azimuth=0 can be withing
    #that day. It doesn't matter since there will be no generation at midnight. 
    
    ########
        
    
    #power generation inverter
    plt.figure(figsize=(8, 8))
    gs1 = gridspec.GridSpec(1, 1)
    ax0 = plt.subplot(gs1[0,0])
    ax0.plot([0,y_lim],[0, y_lim], linewidth=3, color='black', label = 'identity line')
        
    
    if isinstance(color_value, pd.Series):
        if color_value.name == 'azimuth':
            if interval == 'morning' and color_interval =='specific':
                vmin = 0
                vmax = 180
            elif interval == 'noon' and color_interval =='specific':
                vmin = 130
                vmax = 215
            elif interval == 'afternoon' and color_interval =='specific':
                vmin = 180
                vmax = 360
            elif color_interval =='total':
                vmin = 0
                vmax = 360
                # Plots scatter with color limits from azimuth
            sc = ax0.scatter(modelled_value[scat_index], measured_value[scat_index],c = color_value[scat_index], cmap = 'jet',alpha=0.5, vmin=vmin, vmax=vmax)

        else: 
            sc = ax0.scatter(modelled_value[scat_index], measured_value[scat_index],c = color_value[scat_index], cmap = 'jet',alpha=0.5)
        
        # Adding a color bar
        cbar = plt.colorbar(sc)
        cbar.set_label(str(color_value.name), fontsize=label_size)
        # Adjust the font size of the colorbar's tick labels
        cbar.ax.tick_params(labelsize=tick_size)  # Set the font size here
        
    if isinstance(color_value, str):
        ax0.scatter(modelled_value[scat_index], measured_value[scat_index], 
                  color=color_value,alpha=0.5)
        
    #RMSE = math.sqrt(np.square(np.subtract(modelled_value[scat_index],measured_value[scat_index])).mean())
    #nRMSE = RMSE/modelled_value[scat_index].mean()
    
    
    nRMSE = calculate_nrmse(modelled_value[scat_index],measured_value[scat_index])
    
    
    # Calculate the residuals
    residuals = measured_value[scat_index] - modelled_value[scat_index]
    
    # Calculate the total sum of squares
    total_sum_of_squares = np.sum((measured_value[scat_index] - np.mean(measured_value[scat_index]))**2)
    
    # Calculate the residual sum of squares
    residual_sum_of_squares = np.sum(residuals**2)
    
    # Calculate R^2
    r_sq = 1 - (residual_sum_of_squares / total_sum_of_squares)
    
    

    
    if start_date == False:
        start_date = time_index[0]
        end_date = time_index[-1]
        start_string = start_date.strftime('%Y-%m-%d')
        end_string = end_date.strftime('%Y-%m-%d')
    else:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            start_string = start_date.strftime('%Y-%m-%d')
            end_string = end_date.strftime('%Y-%m-%d')

    ax0.text(0.05, 0.95, 'nRMSE = ' + str(round(nRMSE*100,1))+'%', 
         transform=ax0.transAxes, fontsize=text_size)
    ax0.text(0.05, 0.90, '# data points = ' + str(len(scat_index)), 
         transform=ax0.transAxes, fontsize=text_size)
    ax0.text(0.05, 0.85, 'interval = ' + str(interval), 
         transform=ax0.transAxes, fontsize=text_size)
    ax0.text(0.05, 0.80, 'Period = ' + str(start_string) + ' to ' + str(end_string), 
         transform=ax0.transAxes, fontsize=text_size)
    ax0.text(0.05, 0.75, 'r_sq = ' + str(round(r_sq,3)), 
         transform=ax0.transAxes, fontsize=text_size)
    plt.title(Title, fontsize=title_size, pad=pad, fontname=font_type)
    ax0.set_xlim([0,y_lim])
    ax0.set_ylim([0,y_lim])
    ax0.set_ylabel(y_label, fontsize=label_size)
    ax0.set_xlabel(x_label, fontsize=label_size)
    # Set the font size of tick labels on both axes
    ax0.tick_params(axis='both', which='major', labelsize=tick_size)
    
    
    #Adds explination on the model that has been run
    model_explain_function(model_explain, model_to_run)
    if regression_line == True:
        R_sqared, m, b = reg_line(modelled_value, measured_value, scat_index, regression_line)
        ax0.text(0.05, 0.70, 'R^2 = ' + str(round(R_sqared,3)), 
             transform=ax0.transAxes, fontsize=text_size)
        
        
    fit_dict = {'nRMSE':nRMSE*100,
                '# data points':len(scat_index),
                'R^2':round(R_sqared,3),
                'slope':m,
                'offset':b}    
    return scat_index, fit_dict
    


def solar_pos_scat(Title, y_label, x_label, value1, value2,start_date, end_date, solar_position, y_lim, x_lim, model_to_run, model_explain = False,color_value='blue',  interval = 'false'):   
        import pandas as pd
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec 
        import numpy as np
        import statistics
        import math

        
        tz='UTC' 
        time_index = pd.date_range(start=start_date, 
                                         end=end_date, 
                                         freq='5min',  
                                             tz=tz)
        
        ####
        
        solar_position = solar_position.loc[time_index]
        
        if interval == 'morning':
            #Time index excluding the periode where the genration is dominated 
            #by the east side
            scat_index = solar_position[solar_position['azimuth']<180].index
        elif interval == 'noon':
            scat_index = solar_position[(solar_position['azimuth']>=130) & (solar_position['azimuth']<=215)].index
        elif interval == 'afternoon':
            scat_index = solar_position[solar_position['azimuth']>180].index
        elif interval == 'false':
            scat_index = time_index
            
        #The afternoon azimuth angles are chosen to be roughly midway between the
        #peak and vally of the DC generation on 12th May 2023. 
        
        #The morning interval can also include data point for the same 
        #day around midnight since the solar morning azimuth=0 can be withing
        #that day. It doesn't matter since there will be no generation at midnight. 
        
        ########
        
        #power generation inverter
        plt.figure(figsize=(8, 8))
        gs1 = gridspec.GridSpec(1, 1)
        ax0 = plt.subplot(gs1[0,0])
        if isinstance(color_value, pd.Series):
            ax0.scatter(value1[scat_index], value2[scat_index],c = color_value[scat_index], cmap = 'jet',alpha=0.5)
        if isinstance(color_value, str):
            ax0.scatter(value1[scat_index], value2[scat_index], 
                      color=color_value,alpha=0.5)
            
        plt.title(Title)
        ax0.set_xlim(x_lim)
        ax0.set_ylim(y_lim)
        ax0.set_ylabel(y_label)
        ax0.set_xlabel(x_label)
        
        #Adds explination on the model that has been run
        model_explain_function(model_explain, model_to_run)



def bar_plots(poa_model, poa_data, model_to_run,days, model_explain = False):
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec 
    import seaborn as sns
    
    # Converted to kWh/m2
    poa_daily_sum = (poa_data.resample('D').sum()*5)/(60*1000)
    
    tz='UTC' 
    time_index_day = pd.to_datetime(days)
    
    colors = sns.color_palette('muted')
    
    for day in time_index_day:

        if poa_model == 'infinite_sheds':
            categories = ['East', 'West']
            Direct = [poa_daily_sum['poa_front_direct'][day],poa_daily_sum['poa_back_direct'][day]]
            Sky_diffuse = [poa_daily_sum['poa_front_sky_diffuse'][day],poa_daily_sum['poa_back_sky_diffuse'][day]]
            Ground_diffuse = [poa_daily_sum['poa_front_ground_diffuse'][day],poa_daily_sum['poa_back_ground_diffuse'][day]]
        elif poa_model == 'simple':
            categories = ['East', 'West']
            Direct = [poa_daily_sum['east_poa_direct'][day],poa_daily_sum['west_poa_direct'][day]]
            Sky_diffuse = [poa_daily_sum['east_poa_sky_diffuse'][day],poa_daily_sum['west_poa_sky_diffuse'][day]]
            Ground_diffuse = [poa_daily_sum['east_poa_ground_diffuse'][day],poa_daily_sum['west_poa_ground_diffuse'][day]]
            
        
        #power generation inverter
        plt.figure(figsize=(8, 8))
        gs1 = gridspec.GridSpec(1, 1)
        ax0 = plt.subplot(gs1[0,0])
        
        totals = [sum(x) for x in zip(Direct, Sky_diffuse, Ground_diffuse)]

        # Plotting the first sub-category
        bar1 = ax0.bar(categories, Direct, color=colors[0], label='Direct')
        
        # Plotting the second sub-category, stacked on top of the first
        bar2 = ax0.bar(categories, Sky_diffuse, bottom=Direct, color=colors[1], label='Sky diffuse')
               
        # Plotting the third sub-category, stacked on top of the first two
        bar3 = ax0.bar(categories, Ground_diffuse, bottom=[i+j for i, j in zip(Direct, Sky_diffuse)], color=colors[2], label='Ground diffuse')
                 
        # Function to add labels within the bars
        def add_labels(bars, data, bottom_data=None):
            for bar, datum, total, bottom_datum in zip(bars, data, totals, bottom_data if bottom_data else [0]*len(data)):
                height = bar.get_height()
                if height > 0:  # To avoid division by zero and negative values
                    plt.text(bar.get_x() + bar.get_width() / 2., bottom_datum + height / 2.,
                             f'{(datum / total * 100):.1f}%', ha='center', va='center', color='black', fontsize = 12, fontweight = 'bold')
        
        # Adding labels to each sub-category
        add_labels(bar1, Direct)
        add_labels(bar2, Sky_diffuse, Direct)
        add_labels(bar3, Ground_diffuse, [i+j for i, j in zip(Direct, Sky_diffuse)])

       
        #ax0.bar(categories, Ground_diffuse, bottom=Sky_diffuse, color='green', label='Ground diffuse')
        
        # Adding labels and title
        ax0.set_xlabel('Orientation')
        date_string = day.strftime('%Y-%m-%d')
        ax0.set_ylabel('Daily irradiance [kWh/m2]')
        plt.title(f'POA components for {date_string}' + ' ' + poa_model)
        plt.legend()
        
        #Adds explination on the model that has been run
        model_explain_function(model_explain, model_to_run)
        
        """
        if model_explain == True:
            # Prepare the dictionary content for display in three columns
            dict_items = list(model_to_run.items())
            n = len(dict_items)
            # Recalculate for two columns
            cols = 2
            rows = n // cols + (n % cols > 0)        
            # Create an adjusted explanatory box for two columns
            plt.figtext(0.1, 0, '\n'.join(['\t'.join([f'{dict_items[row + col * rows][0]}: {dict_items[row + col * rows][1]}' for col in range(cols) if row + col * rows < n]) for row in range(rows)]), ha='left', fontsize=10, bbox=dict(boxstyle="round,pad=0.5", edgecolor="black", facecolor="lightgrey"))
          """ 







def model_explain_function(model_explain, model_to_run):
        import matplotlib.pyplot as plt
        if model_explain == True:
            # Prepare the dictionary content for display in three columns
            dict_items = list(model_to_run.items())
            n = len(dict_items)
            # Recalculate for two columns
            cols = 2
            rows = n // cols + (n % cols > 0)        
            # Create an adjusted explanatory box for two columns
            plt.figtext(0.1, -0.2, '\n'.join(['\t'.join([f'{dict_items[row + col * rows][0]}: {dict_items[row + col * rows][1]}' for col in range(cols) if row + col * rows < n]) for row in range(rows)]), ha='left', fontsize=10, bbox=dict(boxstyle="round,pad=0.5", edgecolor="black", facecolor="lightgrey"))
            
    
      
        


#def daily_plots():
def day_histo_plot(Title, y_label, days, model_to_run, poa_direct, poa_sky_diffuse, poa_ground_diffuse, poa_global, solar_position = False, model_explain = False, zoom = False, y_lines = True):   
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec 
    import numpy as np
    import statistics
    import math
    import seaborn as sns

    tz='UTC' 
    
    colors = sns.color_palette('muted')
    #sunny_day = '2023-05-05 00:00:00'
    #cloudy_day = '2023-05-10 00:00:00'
    #days = [sunny_day, cloudy_day]
    time_index_day = pd.to_datetime(days)
    
    #Font sizes
    label_size = 12
    text_size = 16
    title_size = 20
    text_size = 12
    tick_size = 12
    pad = 20 # Distance between plot and title
    font_type = 'Arial'
    
    color1 = 'dodgerblue'
    color2 = 'firebrick'
    color3 = 'green'
    color4 = 'purple'

    for day in time_index_day:
        time_index = pd.date_range(start=day, 
                               periods=24*12*1, 
                               freq='5min',
                               tz=tz)
        
        
        direct_percent = (poa_direct[time_index]/poa_global[time_index])*100
        sky_diffuse_percent = (poa_sky_diffuse[time_index]/poa_global[time_index])*100
        ground_diffuse_percent = (poa_ground_diffuse[time_index]/poa_global[time_index])*100
        
        #Added together
        sky_direct = direct_percent + sky_diffuse_percent
        sky_direct_ground = direct_percent + sky_diffuse_percent + ground_diffuse_percent
        
        #power generation inverter
        plt.figure(figsize=(10, 6))
        gs1 = gridspec.GridSpec(1, 1)
        ax0 = plt.subplot(gs1[0,0])
        
        #ax0.bar(time_index, direct_percent, label='direct', color=colors[0])
        #ax0.bar(time_index, sky_diffuse_percent, bottom=direct_percent, label='sky_diffuse', color=colors[1])
        #ax0.bar(time_index, ground_diffuse_percent, bottom=direct_percent+sky_diffuse_percent, label='ground_diffuse', color=colors[2])
        
        
        ax0.plot(direct_percent, label='direct')
        ax0.fill_between(time_index, 0, direct_percent, color=colors[0], alpha=0.4)  # Fill color below the line
        ax0.plot(sky_direct, label='sky_diffuse')
        ax0.fill_between(time_index, direct_percent, sky_direct, color=colors[1], alpha=0.4)
        ax0.plot(sky_direct_ground, label = 'ground_diffuse')
        ax0.fill_between(time_index, sky_direct, sky_direct_ground, color=colors[2], alpha=0.4)
        
        
        """
        # Adds a x-axis in the top of the plot with the solar azimuth  
        if isinstance(solar_position, pd.DataFrame):
            ax3 = ax0.twiny()
            ax3.plot(solar_position['azimuth'][time_index],solar_position['azimuth'][time_index], alpha=0 )
            if azimuth_line == True:
                ax3.axvline(x=90, color='black', linestyle = '--')
                ax3.axvline(x=180, color='black', linestyle = '--')
                ax3.axvline(x=270, color='black', linestyle = '--')
                """
        
        if isinstance(solar_position, pd.Series):
            if y_lines == True and solar_position.name == 'azimuth': # Plots vertical lines when the sun reaces east, south and west
                #time_index_start = pd.date_range(day, 
                 #                    periods=1, 
                  #                   freq='5min',
                   #                  tz=tz)
              
                #time_index_end = time_index_start + pd.DateOffset(days=1)
                #ax3 = ax0.twiny()
             
                #ax3.set_xlim(solar_position[time_index_start], solar_position[time_index_end])
                #ax3.plot(solar_position[time_index],solar_position[time_index], alpha=1 )
                #if y_lines == True and solar_position.name == 'azimuth':
                 #   ax3.axvline(x=90, color='black', linestyle = '--')
                  #  ax3.axvline(x=180, color='black', linestyle = '--')
                   # ax3.axvline(x=270, color='black', linestyle = '--')
                    #ax3.set_xlabel('Solar azimuth')
                    
                    noon = solar_position[time_index]
                    noon_90 = noon[solar_position>90]
                    noon_180 = noon[solar_position>180]
                    noon_270 = noon[solar_position>270]
                    ax0.axvline(noon_270.index[0], color='black', linestyle = '--')
                    ax0.axvline(noon_180.index[0], color='black', linestyle = '--')
                    ax0.axvline(noon_90.index[0], color='black', linestyle = '--')
                    ax0.text(noon_270.index[0], 10, 'W', fontsize=8, ha='center', va='center', family='sans-serif', 
                             bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
                    ax0.text(noon_180.index[0], 10, 'S', fontsize=8, ha='center', va='center', family='sans-serif', 
                             bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
                    ax0.text(noon_90.index[0], 10, 'E', fontsize=8, ha='center', va='center', family='sans-serif', 
                             bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
        
        
        ax0.set_ylim([0,100])
        ax0.set_ylabel(y_label,fontsize=14)
        plt.title(Title, fontsize=title_size)
        plt.setp(ax0.get_xticklabels(), ha="right", rotation=45,fontsize=tick_size)
        ax0.grid('--')
        ax0.tick_params(axis='y', labelsize=16) 
        ax0.legend(fontsize=label_size)
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        #Zoom on the specified interval
        if zoom == False:
            ax0.set_xlim(pd.Timestamp(day), pd.Timestamp(day + pd.Timedelta(days=1)))
        else:
            ax0.set_xlim(pd.Timestamp(day) + pd.Timedelta(hours=zoom[0]), pd.Timestamp(day + pd.Timedelta(hours=zoom[1])))
        
        #Adds explination on the model that has been run
        model_explain_function(model_explain, model_to_run)
        
        #plt.savefig('Figures/day_histo_profiles/{}_{}_{}_{}.jpg'.format(Title, day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
         #           dpi=100, bbox_inches='tight')
        
    #return direct_percent, sky_diffuse_percent, ground_diffuse_percent, sky_direct, sky_direct_ground


    """
def reg_line(modelled_value, measured_value, index, regression_line = True):
        import numpy as np
        import matplotlib.pyplot as plt
        x = modelled_value[index].fillna(0)
        y = measured_value[index].fillna(0)
        m, b = np.polyfit(x, y, 1)
        # Calculating the regression line's y values based on m and b
        y_pred = m * x + b
        plt.plot(x,y_pred, color='red', label='Regression line')
        # Calculate the residuals
        residuals = y - y_pred
        
        # Calculate the total sum of squares
        total_sum_of_squares = np.sum((y - np.mean(y))**2)
        
        # Calculate the residual sum of squares
        residual_sum_of_squares = np.sum(residuals**2)
        
        # Calculate R^2
        r_squared = 1 - (residual_sum_of_squares / total_sum_of_squares)
        return r_squared
    
    
    """
        
def reg_line(modelled_value, measured_value, index, regression_line=True):
    import numpy as np
    import matplotlib.pyplot as plt
    
    # Extract the specific indexed data and fill NA with 0 
    # Should maybe just exclude those points?
    #x = modelled_value[index].fillna(0)
    #y = measured_value[index].fillna(0)
    
    x = modelled_value
    y = measured_value
    
    """
    modelled_value = modelled_value[index]
    measured_value = measured_value[index]
    
    #Filters out times where either modelled of measured or both are nan
    no_nan_indices = modelled_value.notna() & measured_value.notna()  # Find indices where both are not NaN
    modelled_value_clean = modelled_value[no_nan_indices]
    measured_value_clean = measured_value[no_nan_indices]

    x = modelled_value_clean
    y = measured_value_clean
    """
    
    try:
        # Attempt to fit a linear regression model
        m, b = np.polyfit(x, y, 1)
        
        # Calculating the regression line's y values based on m and b
        y_pred = m * x + b
        
        # Optionally plot the regression line
        if regression_line:
            plt.plot(x, y_pred, color='red', label='Regression line')
            plt.legend(loc = 'lower right')
        
        # Calculate the residuals
        residuals = y - y_pred
        
        # Calculate the total sum of squares
        total_sum_of_squares = np.sum((y - np.mean(y))**2)
        
        # Calculate the residual sum of squares
        residual_sum_of_squares = np.sum(residuals**2)
        
        # Calculate R^2
        r_squared = 1 - (residual_sum_of_squares / total_sum_of_squares)
        
    except np.linalg.LinAlgError:
        # If SVD did not converge, return 100 as specified
        r_squared = 100
        m = np.nan
        b = np.nan
    
    return r_squared, m, b

    
    

def calculate_nrmse(modelled_value, measured_value):    #Is this correct?
    import numpy as np
    """
    Calculate the normalized Root Mean Squared Error (nRMSE).

    Parameters:
    - modelled_value: np.array or a list, predicted values by the model.
    - measured_value: np.array or a list, actual measured values.

    Returns:
    - nRMSE as a float.
    """
    mse = np.mean((modelled_value - measured_value) ** 2)
    rmse = np.sqrt(mse)
    nrmse = rmse / (measured_value.max() - measured_value.min())
    nrmse_mean = rmse / np.mean(measured_value)

    return nrmse_mean






#def daily_plots():
def day_plot_6(Title, y_label, days, path=False, save_plots=False, model_to_run = False,poa_direct=False, poa_sky_diffuse=False, poa_ground_diffuse=False, poa_global=False, model_explain = False, value1=1, value2=1, value3=1, value4=1, value5=1,value6=1, y_lim = 'default', custom_label = False, zoom = False, solar_position = False, y_lines = False, custom_yline = False):   
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec 
    import numpy as np
    import statistics
    import math

    tz='UTC' 
    
    #Font sizes
    label_size = 20
    text_size = 16
    title_size = 24
    text_size = 16
    tick_size = 16
    legend_size = 16
    pad = 20 # Distance between plot and title
    font_type = 'Arial'
    
    #sunny_day = '2023-05-05 00:00:00'
    #cloudy_day = '2023-05-10 00:00:00'
    #days = [sunny_day, cloudy_day]
    time_index_day = pd.to_datetime(days)
    
    
    color1 = 'dodgerblue'
    color2 = 'firebrick'
    color3 = 'green'
    color4 = 'purple'
    color5 = 'red'    
    color6 = 'orange'

   


    if custom_label ==False:
        if isinstance(value1, int):
            value1_label = 'int'
        else: 
            value1_label = value1.name
            
        if isinstance(value2, int):
            value2_label = 'int'
        else: 
            value2_label = value2.name
        
        if isinstance(value3, int):
            value3_label = 'int'
        else: 
            value3_label = value3.name
            
        if isinstance(value4, int):
            value4_label = 'int'
        else: 
            value4_label = value4.name
            
        if isinstance(value5, int):
            value5_label = 'int'
        else: 
            value5_label = value5.name
            
        if isinstance(value6, int):
            value6_label = 'int'
        else: 
            value6_label = value6.name
            
    elif isinstance(custom_label, list):
        value1_label = custom_label[0]
        value2_label = custom_label[1]
        value3_label = custom_label[2]
        value4_label = custom_label[3]
        value5_label = custom_label[4]
        value6_label = custom_label[5]
        
    
    for day in time_index_day:
        time_index = pd.date_range(start=day, 
                               periods=24*12*1, 
                               freq='5min',
                               tz=tz)
        
        #power generation inverter
        plt.figure(figsize=(10, 6))
        gs1 = gridspec.GridSpec(1, 1)
        ax0 = plt.subplot(gs1[0,0])
        ax0.set_ylim([0,y_lim])
        if isinstance(value1, pd.Series) and not isinstance(value2, pd.Series) and not isinstance(value3, pd.Series) and not isinstance(value4, pd.Series) and not isinstance(value5, pd.Series) and not isinstance(value6, pd.Series):
            ax0.plot(value1[time_index], 
                      color=color1,
                      label= value1_label)
            
        if isinstance(value1, pd.Series) and  isinstance(value2, pd.Series) and not isinstance(value3, pd.Series) and not isinstance(value4, pd.Series)and not isinstance(value5, pd.Series) and not isinstance(value6, pd.Series):
            ax0.plot(value1[time_index], 
                      color=color1,
                      label=value1_label)
            ax0.plot(value2[time_index], 
                      color=color2,
                      label=value2_label)
            
        if isinstance(value1, pd.Series) and  isinstance(value2, pd.Series) and isinstance(value3 , pd.Series) and not isinstance(value4, pd.Series)and not isinstance(value5, pd.Series) and not isinstance(value6, pd.Series):
            ax0.plot(value1[time_index], 
                      color=color1,
                      label=value1_label)
            ax0.plot(value2[time_index], 
                      color=color2,
                      label=value2_label) 
            ax0.plot(value3[time_index], 
                      color=color3,
                      label=value3_label) 
        if isinstance(value1, pd.Series) and  isinstance(value2, pd.Series) and isinstance(value3 , pd.Series) and isinstance(value4, pd.Series) and not isinstance(value5, pd.Series) and not isinstance(value6, pd.Series):
            ax0.plot(value1[time_index], 
                      color=color1,
                      label=value1_label)
            ax0.plot(value2[time_index], 
                      color=color2,
                      label=value2_label) 
            ax0.plot(value3[time_index], 
                      color=color3,
                      label=value3_label) 
            ax0.plot(value4[time_index], 
                      color=color4,
                      label=value4_label) 
            
            
            
        if isinstance(value1, pd.Series) and  isinstance(value2, pd.Series) and isinstance(value3 , pd.Series) and isinstance(value4, pd.Series) and isinstance(value5, pd.Series) and not isinstance(value6, pd.Series):
            ax0.plot(value1[time_index], 
                      color=color1,
                      label=value1_label)
            ax0.plot(value2[time_index], 
                      color=color2,
                      label=value2_label) 
            ax0.plot(value3[time_index], 
                      color=color3,
                      label=value3_label) 
            ax0.plot(value4[time_index], 
                      color=color4,
                      label=value4_label)
            ax0.plot(value5[time_index], 
                      color=color5,
                      label=value5_label)
            
            if isinstance(value1, pd.Series) and  isinstance(value2, pd.Series) and isinstance(value3 , pd.Series) and isinstance(value4, pd.Series) and isinstance(value5, pd.Series) and isinstance(value6, pd.Series):
                ax0.plot(value1[time_index], 
                          color=color1,
                          label=value1_label)
                ax0.plot(value2[time_index], 
                          color=color2,
                          label=value2_label) 
                ax0.plot(value3[time_index], 
                          color=color3,
                          label=value3_label) 
                ax0.plot(value4[time_index], 
                          color=color4,
                          label=value4_label)
                ax0.plot(value5[time_index], 
                          color=color5,
                          label=value5_label)
                ax0.plot(value6[time_index], 
                          color=color6,
                          label=value6_label)
           
        # Adds a x-axis in the top of the plot with the solar azimuth
        if isinstance(solar_position, pd.Series):
            if y_lines == True and solar_position.name == 'azimuth': # Plots vertical lines when the sun reaces east, south and west
                #time_index_start = pd.date_range(day, 
                 #                    periods=1, 
                  #                   freq='5min',
                   #                  tz=tz)
              
                #time_index_end = time_index_start + pd.DateOffset(days=1)
                #ax3 = ax0.twiny()
             
                #ax3.set_xlim(solar_position[time_index_start], solar_position[time_index_end])
                #ax3.plot(solar_position[time_index],solar_position[time_index], alpha=1 )
                #if y_lines == True and solar_position.name == 'azimuth':
                 #   ax3.axvline(x=90, color='black', linestyle = '--')
                  #  ax3.axvline(x=180, color='black', linestyle = '--')
                   # ax3.axvline(x=270, color='black', linestyle = '--')
                    #ax3.set_xlabel('Solar azimuth')
                    
                    noon = solar_position[time_index]
                    noon_90 = noon[solar_position>90]
                    noon_180 = noon[solar_position>180]
                    noon_270 = noon[solar_position>270]
                    ax0.axvline(noon_270.index[0], color='black', linestyle = '--')
                    ax0.axvline(noon_180.index[0], color='black', linestyle = '--')
                    ax0.axvline(noon_90.index[0], color='black', linestyle = '--')
                    ax0.text(noon_270.index[0], 0.05*y_lim, 'W', fontsize=8, ha='center', va='center', family='sans-serif', 
                             bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
                    ax0.text(noon_180.index[0], 0.05*y_lim, 'S', fontsize=8, ha='center', va='center', family='sans-serif', 
                             bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
                    ax0.text(noon_90.index[0], 0.05*y_lim, 'E', fontsize=8, ha='center', va='center', family='sans-serif', 
                             bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
            # Draws vertical lines when the solar elevation goes above and below 10deg
            if y_lines == True and solar_position.name == 'elevation':              
                #ax4 = ax0.twinx()
                elev = solar_position[time_index]
                elev10 = elev[elev>10]
                #ax4.plot(solar_position[elev10.index], color='red', alpha=1)
                ax0.axvline(elev10.index[0], color='black', linestyle = '--')
                ax0.axvline(elev10.index[-1], color='black', linestyle = '--')
                ax0.text(elev10.index[0], 0.8, 'Solar \nelevation \n10°', fontsize=12, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
                ax0.text(elev10.index[-1], 0.8, 'Solar \nelevation \n10°', fontsize=12, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
            # Draws ann vertical line at a customset offset
            if isinstance(custom_yline, pd.DateOffset) and solar_position.name == 'azimuth':
                time_index_start = pd.date_range(day, 
                                     periods=1, 
                                     freq='5min',
                                     tz=tz)
                time_index_end = time_index_start + custom_yline
                ax0.axvline(time_index_end, color='red', linestyle = '--')
        
        ax0.set_ylabel(y_label, fontsize=label_size)
        plt.title(Title, fontsize=title_size)
        plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
        ax0.grid('--')
        ax0.legend(fontsize=legend_size)
    
        ax0.set_xlabel('Date', fontsize=label_size)
        ax0.tick_params(axis='both', which='major', labelsize=tick_size)
        #Zoom on the specified interval
        if zoom == False:
            ax0.set_xlim(pd.Timestamp(day), pd.Timestamp(day + pd.Timedelta(days=1)))
        else:
            ax0.set_xlim(pd.Timestamp(day) + pd.Timedelta(hours=zoom[0]), pd.Timestamp(day + pd.Timedelta(hours=zoom[1])))
        
        #Adds explination on the model that has been run
        model_explain_function(model_explain, model_to_run)
        
        if save_plots == True:
            plt.savefig(path+'/{}_{}_{}_{}.png'.format(Title, day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                        dpi=100, bbox_inches='tight',format = 'png')
        
        plt.savefig('Figures/day_profiles/{}_{}_{}_{}.jpg'.format(Title, day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                    dpi=100, bbox_inches='tight')
        
        
        
def day_plot_6_1(Title, y_label, days, path=False, save_plots=False, model_to_run=False, poa_direct=False, poa_sky_diffuse=False, poa_ground_diffuse=False, poa_global=False, model_explain=False, value1=1, value2=1, value3=1, value4=1, value5=1, value6=1, y_lim='default', custom_label=False, zoom=False, solar_position=False, y_lines=False, custom_yline=False):   
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec 
    import numpy as np
    import statistics
    import math

    tz='UTC' 
    
    # Font sizes
    label_size = 20
    text_size = 16
    title_size = 24
    tick_size = 16
    legend_size = 16
    pad = 20 # Distance between plot and title
    font_type = 'Arial'
    
    time_index_day = pd.to_datetime(days)
    
    color1 = '#1E90FF'  # Dodger Blue
    color2 = '#B22222'  # Firebrick
    color3 = '#228B22'  # Forest Green
    color4 = '#FF8C00'  # Dark Orange
    color5 = '#9370DB'  # Medium Purple
    color6 = '#00CED1'  # Cyan

    if custom_label == False:
        if isinstance(value1, int):
            value1_label = 'int'
        else: 
            value1_label = value1.name
            
        if isinstance(value2, int):
            value2_label = 'int'
        else: 
            value2_label = value2.name
        
        if isinstance(value3, int):
            value3_label = 'int'
        else: 
            value3_label = value3.name
            
        if isinstance(value4, int):
            value4_label = 'int'
        else: 
            value4_label = value4.name
            
        if isinstance(value5, int):
            value5_label = 'int'
        else: 
            value5_label = value5.name
            
        if isinstance(value6, int):
            value6_label = 'int'
        else: 
            value6_label = value6.name
            
    elif isinstance(custom_label, list):
        value1_label = custom_label[0]
        value2_label = custom_label[1]
        value3_label = custom_label[2]
        value4_label = custom_label[3]
        value5_label = custom_label[4]
        value6_label = custom_label[5]
        
    for day in time_index_day:
        time_index = pd.date_range(start=day, 
                               periods=24*12*1, 
                               freq='5min',
                               tz=tz)
        
        # Power generation inverter
        plt.figure(figsize=(10, 10))
        gs1 = gridspec.GridSpec(1, 1)
        ax0 = plt.subplot(gs1[0, 0])
        ax0.set_ylim([0, y_lim])
        if isinstance(value1, pd.Series):
            ax0.plot(value1[time_index], color=color1, label=value1_label)
        if isinstance(value2, pd.Series):
            ax0.plot(value2[time_index], color=color2, label=value2_label)
        if isinstance(value3, pd.Series):
            ax0.plot(value3[time_index], color=color3, label=value3_label)
        if isinstance(value4, pd.Series):
            ax0.plot(value4[time_index], color=color4, label=value4_label)
        if isinstance(value5, pd.Series):
            ax0.plot(value5[time_index], color=color5, label=value5_label)
        if isinstance(value6, pd.Series):
            ax0.plot(value6[time_index], color=color6, label=value6_label)
           
        # Adds a x-axis in the top of the plot with the solar azimuth
        if isinstance(solar_position, pd.Series):
            if y_lines == True and solar_position.name == 'azimuth': # Plots vertical lines when the sun reaches east, south, and west
                noon = solar_position[time_index]
                noon_90 = noon[solar_position > 90]
                noon_180 = noon[solar_position > 180]
                noon_270 = noon[solar_position > 270]
                ax0.axvline(noon_270.index[0], color='black', linestyle='--')
                ax0.axvline(noon_180.index[0], color='black', linestyle='--')
                ax0.axvline(noon_90.index[0], color='black', linestyle='--')
                ax0.text(noon_270.index[0], 0.05*y_lim, 'W', fontsize=8, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
                ax0.text(noon_180.index[0], 0.05*y_lim, 'S', fontsize=8, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
                ax0.text(noon_90.index[0], 0.05*y_lim, 'E', fontsize=8, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
            # Draws vertical lines when the solar elevation goes above and below 10°
            if y_lines == True and solar_position.name == 'elevation':              
                elev = solar_position[time_index]
                elev10 = elev[elev > 10]
                ax0.axvline(elev10.index[0], color='black', linestyle='--')
                ax0.axvline(elev10.index[-1], color='black', linestyle='--')
                ax0.text(elev10.index[0], 0.8, 'Solar \nelevation \n10°', fontsize=12, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
                ax0.text(elev10.index[-1], 0.8, 'Solar \nelevation \n10°', fontsize=12, ha='center', va='center', family='sans-serif', 
                         bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=0.5'))
            # Draws a vertical line at a custom set offset
            if isinstance(custom_yline, pd.DateOffset) and solar_position.name == 'azimuth':
                time_index_start = pd.date_range(day, periods=1, freq='5min', tz=tz)
                time_index_end = time_index_start + custom_yline
                ax0.axvline(time_index_end, color='red', linestyle='--')
        
        ax0.set_ylabel(y_label, fontsize=label_size)
        plt.title(Title, fontsize=title_size)
        plt.setp(ax0.get_xticklabels(), ha="right", rotation=45)
        ax0.grid('--')
        ax0.legend(fontsize=legend_size, loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=3)
    
        ax0.set_xlabel('Date', fontsize=label_size)
        ax0.tick_params(axis='both', which='major', labelsize=tick_size)
        #Zoom on the specified interval
        if zoom == False:
            ax0.set_xlim(pd.Timestamp(day), pd.Timestamp(day + pd.Timedelta(days=1)))
        else:
            ax0.set_xlim(pd.Timestamp(day) + pd.Timedelta(hours=zoom[0]), pd.Timestamp(day + pd.Timedelta(hours=zoom[1])))
        
        #Adds explanation on the model that has been run
        model_explain_function(model_explain, model_to_run)
        
        if save_plots == True:
            plt.savefig(path + '/{}_{}_{}_{}.png'.format(Title, day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                        dpi=100, bbox_inches='tight', format='png')
        
        plt.savefig('Figures/day_profiles/{}_{}_{}_{}.jpg'.format(Title, day.year, str(day.month).zfill(2), str(day.day).zfill(2)), 
                    dpi=100, bbox_inches='tight')

