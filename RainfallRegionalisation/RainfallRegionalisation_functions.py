from numba import jit
import pandas as pd
import numpy as np
from pyproj import Proj, transform


# From FindSTats_VlaluesOverpercentile
"""Using numba to extract values above a percentile.
Numba executes loops efficiently (just in time compiling)
Somehow, the exceptions do not work well within numba, so they are passed out as integers"""
@jit
def values_above_percentile(rain_data, percentile_cutoff_data):
    exception=0
    # Find shape of data for use in for loop
    imax=np.shape(rain_data)[1] 
    jmax=np.shape(rain_data)[2]
    if(np.shape(percentile_cutoff_data)[0]>1):
        exception=1
    
    # Define how many numbers over percentile there are for one dimensions
    # This should be the value throughout - which is checked later
    local_raindata=rain_data[:,0,0]
    local_percentile=percentile_cutoff_data[0,0,0]
    data_over_percentile=np.sort(local_raindata[local_raindata>=local_percentile])#[::-1]
    n_over_percentile = len(data_over_percentile)   
    print(n_over_percentile)
    
    # First dimension is for time
    n_highest_array=np.zeros((1,n_over_percentile,imax,jmax))
    for i in range(imax):
        for j in range(jmax):
            #print(i,j)
            # Find the rainfall values at this location
            local_raindata=rain_data[:,i,j]
            # Find the value of the percentile at this location
            local_percentile=percentile_cutoff_data[0,i,j]
            # Extract values above cutoff percentile, sort these data over percentile 
            # in descending order
            data_over_percentile=np.sort(local_raindata[local_raindata>=local_percentile])#[::-1]
            local_n_over_percentile=len(data_over_percentile)
            print(local_n_over_percentile)
            # ensure we have extracted enough values
            if not local_n_over_percentile == n_over_percentile:
                print("Error: incorrect number of values over percentile")
                # Sort in descening order, and remove the smallest value
                data_over_percentile = data_over_percentile[::-1][:n_over_percentile]
                print(len(data_over_percentile))
            # only use the n highest values
            n_highest_array[0,:,i,j]=data_over_percentile
            #print("g")
    return n_highest_array


# From FindStats - work out what difference is
@jit
def values_above_percentile(rain_data,percentile_data,n_highest):
"""Using numba to extract values above a percentile.
Numba executes loops efficiently (just in time compiling)
Somehow, the exceptions do not work well within numba, so they are passed out as integers"""    
    
    exception=0
    # length of lons
    imax=np.shape(rain_data)[1] 
    # length of lats
    jmax=np.shape(rain_data)[2]
    if(np.shape(percentile_data)[0]>1):
        exception=1
    # first dimension is for time
    n_highest_array=np.zeros((1,n_highest,imax,jmax))
    
    local_data_dict ={}
    for i in range(imax):
        for j in range(jmax):
            # Get data at one cell
            local_raindata=rain_data[:,i,j]
            local_data_dict[name] = local_raindata
            name = name +1
            # Find the percentile cutoff value for that cell
            local_percentile=percentile_data[0,i,j]
            # extract values above cutoff percentile, sort these data over percentile in descending order
            # this is the most important line in this piece of code
            data_over_percentile=np.sort(local_raindata[local_raindata>=local_percentile])[::-1]
            local_n_over_percentile=len(data_over_percentile)
            # ensure we have extracted enough values
            if(local_n_over_percentile>=n_highest):
                # only use the n highest values
                n_highest_array[0,:,i,j]=data_over_percentile[:n_highest]
            else:
                exception=2
    return n_highest_array,exception


def find_biggest_percentage_share (dictionary):
    '''
    Description
    ----------
        Takes a dictionary containing, for a particular number of clusters, the cluster
        number values associated with each cell for each ensemble member
        Calculates for each cell the proportion of ensemble members in which it is found
            within the cluster in which it appears most often.
        
    Parameters
    ----------
        dictionary: Dictionary
            A dictionary where the keys are ensemble member numbers, and the values are  
            series (1D array) are cluster number values for all lat/long locations in an area
            defined by the bounding box of the northern region (north East, north West and Yorkshire
            and the Humber)
    Returns
    -------
        lats_2d : array
            A 2d array of the latitudes
        lons_2d : array
            A 2d array of the longitudes
        percent_2d: array
            A 2d array of the proportion of ensemble members in which each cell is found
            within the cluster in which it appears most often.
    '''
    
    
    # Converts the dictionary into a dataframe
    # Each row in the dataframe is a locaton, nad each column contains the regional
    # cluster code for each ensemble member
    codes_df = pd.DataFrame(dictionary)    
    
    # Create a dictionary to store for each cluster the % of ensemble members where
    # the location is in that cluster
    percents_dict = {}
    # For each cluster in the number of clusters
    # Find the proportion of ensemble members in which the cell is in that cluster
    for n in range(num_clusters): 
        # Find the percentage of ensemble members in that cluster and add to the dictionary
        percent_n = (codes_df.apply(lambda s: (s == (n+1)).sum(), axis=1))/12 * 100
        percents_dict['Percent_' + str(n+1)] = percent_n
    
    # Create this as a dataframe
    percents_df = pd.DataFrame(percents_dict)        
    # Add to dataframe containing codes
    codes_df = codes_df.assign(**percents_df)
    # Find the maximum percentage in any one cluster
    codes_df['Percent'] = codes_df.iloc[:,12:len(codes_df.columns)].max(axis=1)           
     # Add lats and lons and remove unneeded columns                                           
    codes_df['lat'], codes_df['lon'] = region_codes['lat'], region_codes['lon']
    
    # Kep only last 3 cols
    codes_df = codes_df[codes_df.columns[-3:]]
    
    ##############################################################################
    # Mask out locations not within specified region
    ##############################################################################
    # Join to mask dataframe (this defines whether each lat/long in an area
    # defined by the bounding box of the northern region (north East, north West and Yorkshire
    # and the Humber region
    # is within the region in the name of the mask - those that are have a 1 value)
    mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))
    # Make the lat, lons from the region cluster codes dataframe the same length as the mask (for joining)
    region_codes = region_codes.round({'lat': 8, 'lon': 8})
    mask = mask.round({'lat': 8, 'lon': 8})

    # Join the mask with the region codes
    codes_df = mask.merge(codes_df,  on=['lat', 'lon'], how="left")   
    
    ##############################################################################
    # Convert into format for plotting
    ##############################################################################
    # Convert 1D array back to 2D array
    lats_2d = codes_df['lat'].to_numpy().reshape(lat_length, lon_length)
    lons_2d = codes_df['lon'].to_numpy().reshape(lat_length, lon_length)
    percent_2d = codes_df['Percent'].to_numpy().reshape(lat_length, lon_length)

    # Create mask where cells outwith region are masked
    percent_2d[percent_2d == 0] = 'nan' 
    mx = np.ma.masked_invalid(percent_2d)
    
    # Apply this to the region_codes and lats and lons
    # Not sure if this is best method...
    mask_cols = ~np.all(mx.mask, axis=0)
    percent_2d = percent_2d[:, mask_cols]
    lats_2d = lats_2d[:, mask_cols]
    lons_2d = lons_2d[:, mask_cols]
    
    mask_rows = np.all(np.isnan(percent_2d) | np.equal(percent_2d, 0), axis=1)
    percent_2d = percent_2d[~mask_rows]
    lats_2d = lats_2d[~mask_rows]
    lons_2d = lons_2d[~mask_rows]
    
    # Convert the projections
    lons_2d, lats_2d = transform(Proj(init='epsg:4326'), Proj(init='epsg:27700'),lons_2d, lats_2d)
    
    return lats_2d, lons_2d, percent_2d

@jit
def wet_hour_stats(rain_data, statistic_name):
    '''
    Description
    ----------
        Takes the data from a cube and loops through each cell in the array of data
        and extracts just the wet hours (>0.1mm/hr). Using these wet hours it calculates
        a single value related to the specified 'statistic_name' parameter. This value is the
        saved at that location. A 2d array of data values is returned containing one value
        for each cell corresponding to the input statistic_name.
    Parameters
    ----------
        rain_data: array
            3D array containing the data from an iris cube, with multiple timelices for each location
        statistic_name: String
            A string specifying the statistic to be calculated
    Returns
    -------
        stats_array: array
            A 2D array containing for each location the value corresponing to the statistic
            given as an input to the function      
    '''
    
    # Define length of lons
    imax=np.shape(rain_data)[1] 
    # Define length of lats
    jmax=np.shape(rain_data)[2]
    
    # Create empty array to populate with stats value
    stats_array =np.zeros((imax,jmax))

    # Loop through each of the cells, and find the value of the specified statistic
    # in that cell. Save this value to the correct position in the array
    print("Entering loop")
    for i in range(imax):
        for j in range(jmax):
            # Get data at one cell
            local_raindata=rain_data[:,i,j]
            # Keep only values above 0.1 (wet hours)
            wet_hours = local_raindata[local_raindata>0.1]         
            
            # Calculate statistics on just the wet hours
            # If the statistic name is a percentile then need to first extract the 
            # percentile number from the string 'statistic_name'
            if statistic_name == 'jja_mean_wh':
               statistic_value  = np.mean(wet_hours)
            elif statistic_name == 'jja_max_wh':
              statistic_value  = np.max(wet_hours)
            elif statistic_name == 'wet_prop':
               statistic_value  = (len(wet_hours)/len(local_raindata)) *100
            else:
              percentile_str =re.findall(r'\d+', statistic_name)
              if len(percentile_str) == 1:
                  percentile_no = float(percentile_str[0])
              elif len(percentile_str) ==2:
                 percentile_no = float(percentile_str[0] + '.' + percentile_str[1])
              statistic_value =  np.percentile(wet_hours, percentile_no)
            
            # Store at correct location in array
            stats_array[i,j] = statistic_value

    return  stats_array
    
