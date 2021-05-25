import os
import sys
import warnings
import pandas as pd
from matplotlib.ticker import ScalarFormatter
warnings.simplefilter(action='ignore', category=FutureWarning)

################################################################
# Define variables and set up environment
################################################################
root_dir = '/nfs/a319/gy17m2a/'
os.chdir(root_dir)

# Create path to files containing functions
sys.path.insert(0, root_dir + 'Scripts/UKCP18/GlobalFunctions')
from PDF_plotting_functions import *

# Define station names
station_names = ['headingley_logger', 'eccup_logger', 'bramham_logger', 'farnley_hall_logger', 'knostrop_logger',
               'otley_s.wks_logger']


ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

#############################################
# Read in data
#############################################
for overlapping_time_period in ['Overlapping', 'NotOverlapping']:
    for combined_em in ['Combined', 'NotCombined']:
        for jja_value in ['jja', 'all']:
                
            # 'Not_Overlapping
            overlapping_time_periods= overlapping_time_period
            # 'Combined', 'NotCombined'
            combined_ems = combined_em
            # 'jja', 'all'
            just_jja = jja_value
            
            # Create a dictionary to store the timeseries for all of the stations
            precip_ts = {}
            
            # Loop through the stations, read in gauge and corresponding CEH-GEAR grid cell 
            # data, cut to include only the dates for which they overlap and plot PDFs
            for station_name in station_names:
                print(station_name)  
                # Create a dictionary to store the timeseries for just this station
                gauge_ts ={}
                
                #### Read in CEH-GEAR data from grid cell within which the gauge is found
                filename_cehgear= root_dir + 'Outputs/TimeSeries/CEH-GEAR/Gauge_GridCells/TimeSeries_csv/{}.csv'.format(station_name)
                df_cehgear = pd.read_csv(filename_cehgear, index_col=None, header=0)
                # Create a formatted date column
                df_cehgear['Datetime'] = pd.to_datetime(df_cehgear['Date_formatted'], dayfirst = True)
                
                #### Read in the gauge data
                filename_gauge= root_dir + 'datadir/GaugeData/Newcastle/leeds-at-centre_csvs/{}.csv'.format(station_name)
                df_gauge = pd.read_csv(filename_gauge, index_col=None, header=0)
                # Create a formatted date column
                df_gauge['Datetime'] = pd.to_datetime(df_gauge['Datetime'])
                   
                #### Read in UKCP18 data]
                em_csvs = {}
                for em in ems:
                    filename_ukcp18= root_dir + 'Outputs/TimeSeries/UKCP18/Gauge_GridCells/TimeSeries_csv/{}_{}.csv'.format(station_name, em)
                    df_ukcp18 = pd.read_csv(filename_ukcp18, index_col=None, header=0)
                    # Create a formatted date column
                    em_csvs[em] = df_ukcp18
                
                #### Cut gauge and CEH-GEAR to only include the overlapping time period
                # Find earliest and latest datetime for which there is data in either gauge or CEH-GEAR
                earliesttime = df_gauge['Datetime'].min() if df_gauge['Datetime'].min() > df_cehgear['Datetime'].min() else df_cehgear['Datetime'].min()
                latesttime = df_gauge['Datetime'].max() if df_gauge['Datetime'].max() < df_cehgear['Datetime'].max() else df_cehgear['Datetime'].max()
                # Override with latestime from UKCP18       
                latesttime = pd.to_datetime(df_ukcp18['Date_formatted'].max(), dayfirst = False)
                
                # Filter to only be between these times
                if overlapping_time_period == 'Overlapping':
                    df_cehgear = df_cehgear[(df_cehgear['Datetime'] > earliesttime)& (df_cehgear['Datetime']< latesttime)]
                    df_gauge = df_gauge[(df_gauge['Datetime'] > earliesttime)& (df_gauge['Datetime']< latesttime)]
                    
                # Go through each ensemble member and filter
                # And add to dictionary    
                for em in ems:
                    df_ukcp18 = em_csvs[em]
                    if overlapping_time_period == 'Overlapping':
                        df_ukcp18 = df_ukcp18[78480:] # manually calculated as index of dates bigger than earliest date
                        em_csvs[em] = df_ukcp18
                
                # Cut to JJA
                if just_jja == 'jja':
                    df_gauge = df_gauge[df_gauge['Datetime'].dt.month.isin([6,7,8])]
                    df_cehgear= df_cehgear[df_cehgear['Datetime'].dt.month.isin([6,7,8])]
                    for em in ems:
                        df_ukcp18 = em_csvs[em]
                        to_drop = ['-06-', '-07-', '-08-']
                        df_ukcp18 = df_ukcp18[~df_ukcp18['Date_formatted'].str.contains('|'.join(to_drop))]
                        em_csvs[em] = df_ukcp18
                
                
                # Check if gauge and CEH-GEAR data set are the same length
                if len(df_gauge) == len(df_cehgear):
                    print("Same length")
                # UKCP18 will not be same length as it uses 12 months * 30 days = 360 days total
                
                #### Remove -999 values and na values
                print('NA values in Gauge: ' + str(len(df_gauge[df_gauge['Precipitation (mm/hr)'] == -999])))
                print('NA values in CEH-GEAR: ' + str(df_cehgear['Precipitation (mm/hr)'].isna().sum()))
                
                df_gauge = df_gauge[df_gauge['Precipitation (mm/hr)'] != -999]
                df_cehgear.dropna(inplace = True)
                    
                # Join all ems together
                for em in ems:
                    df_ukcp18 = em_csvs[em]
                    if combined_ems == 'Combined':
                        joined_ems = pd.concat(em_csvs.values(),ignore_index = True)
                        gauge_ts[station_name + '_UKCP18Data'] = joined_ems
                    elif combined_ems == 'NotCombined':
                        precip_ts[station_name + '_UKCP18Data' + em] = df_ukcp18
                        gauge_ts[station_name + '_UKCP18Data' + em] = df_ukcp18
                
                # Add to dictionary for all stations
                precip_ts[station_name + '_GaugeData'] = df_gauge
                precip_ts[station_name + '_GridData'] = df_cehgear
                
                # Add to dictionary for this station
                gauge_ts[station_name + '_GaugeData'] = df_gauge
                gauge_ts[station_name + '_GridData'] = df_cehgear
                
                #########################################################################
                # Plotting
                #########################################################################
                # Define a dictionary of colours
                cols_dict = {station_name + '_GaugeData' : 'firebrick',
                             station_name + '_GridData'  : 'green'}
                if combined_ems == 'Combined':
                    cols_dict[station_name + '_UKCP18Data'] = 'grey'
                else:
                    for em in ems:
                       cols_dict[station_name + '_UKCP18Data{}'.format(em)] = 'grey'
                             
                # Set plotting parameters
                x_axis = 'linear'
                y_axis = 'log'
                bin_nos = 25 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
                xlim = False # False lets plot define aprpopriate xlims
                bins_if_log_spaced= bin_nos
                
                # Create patches, used for labelling
                patches= []
                patch = mpatches.Patch(color='firebrick', label='Gauge Data')
                patches.append(patch)
                patch = mpatches.Patch(color='green', label='CEH-GEAR Data')
                patches.append(patch)
                patch = mpatches.Patch(color='grey', label='UKCP18 Data')
                patches.append(patch)
                
                # Plot
                log_discrete_histogram_lesslegend(gauge_ts, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                                  patches, True, xlim, x_axis, y_axis) 
                
                # Save
                plt.savefig("Scripts/UKCP18/RainGaugeAnalysis/Validating_CEH-GEAR/Figs/PDF_GaugevsGridCell/{}_{}_{}_{}.png".format(station_name, just_jja, overlapping_time_period, combined_ems))
                
                
        
    


    #########################################################################
    # Further analysis
    #########################################################################
    # Reset indexes
    df_gauge.reset_index(drop = True, inplace = True)
    
    #### Find top 20 values in Gauge data
    top20_gauge = df_gauge.nlargest(20, 'Precipitation (mm/hr)')
    # Join on date, so as to find the equivalent vlaues in the CEH-GEAR data at these times
    top20_gauge_cehgear = pd.merge(top20_gauge, df_cehgear, on = 'Datetime')
    # Remove extra date column
    top20_gauge_cehgear = top20_gauge_cehgear.drop(['Date_formatted'], axis =1)  
    # Rename columns
    top20_gauge_cehgear = top20_gauge_cehgear.rename(columns =
                         {'Precipitation (mm/hr)_x': 'Gauge',
                           'Precipitation (mm/hr)_y': 'CEH-GEAR'})
    
    #### For the highest values in the gauge data find the values on either side
    #### of this for both the gauge and CEH-GEAR (to check whether its just that
    #### peaks are not being found in exactly the same moment)
    ## Find timestamp of one of the highest values
    datetime_of_highvalue = top20_gauge.iloc[3][0]
    # Find index of row with that value in original dataframe
    idx = df_gauge.index[df_gauge['Datetime'] == datetime_of_highvalue][0]
    # Extract rows from dataframe with that index, and two above and two below
    surrounding_datetimes = df_gauge.iloc[[idx-2,idx-1, idx, idx+1, idx +2]]
    # Merge to get CEH-GEAR values at those datetimes
    surrounding_datetimes = pd.merge(surrounding_datetimes, df_cehgear, on = 'Datetime')
    surrounding_datetimes = surrounding_datetimes.drop(['Date_formatted'], axis =1)
    surrounding_datetimes = surrounding_datetimes.rename(columns = {'Precipitation (mm/hr)_x': 'Gauge',
                           'Precipitation (mm/hr)_y': 'CEH-GEAR'})
    


###############################################################################
# Plots using all stations
###############################################################################
cols_dict = {'headingley_logger_GaugeData' : 'firebrick',
             'headingley_logger_GridData' : 'green',
             'eccup_logger_GaugeData' : 'firebrick',
             'eccup_logger_GridData' : 'green',
             'bramham_logger_GaugeData' : 'firebrick',
             'bramham_logger_GridData' : 'green',
             'farnley_hall_logger_GaugeData' : 'firebrick',
             'farnley_hall_logger_GridData' : 'green',
             'knostrop_logger_GaugeData' : 'firebrick',
             'knostrop_logger_GridData' : 'green'}

x_axis = 'linear'
y_axis = 'log'
bin_nos = 10 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
xlim = False
bins_if_log_spaced= bin_nos

