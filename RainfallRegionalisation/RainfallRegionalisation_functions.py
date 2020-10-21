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

