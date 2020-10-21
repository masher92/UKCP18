def find_biggest_percentage_share (dictionary):
    # Create a dataframe containing the region codes for each ensemble member in the columns        
    codes_df = pd.DataFrame(dictionary)    
    
    # Create a dictionary to store for each cluster the % of ensemble members wher
    # the location is in that cluster
    percents_dict = {}
    # For each cluster in the number of clusters
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
    
    # Read in the mask
    mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))
     # Make the lat, lons from the mask the same length
    codes_df = codes_df.round({'lat': 8, 'lon': 8})
    mask = mask.round({'lat': 8, 'lon': 8})
    # Join the mask with the region codes
    codes_df = mask.merge(codes_df,  on=['lat', 'lon'], how="left")   
    
     # Convert to 2D
    lats_2d = codes_df['lat'].to_numpy().reshape(lat_length, lon_length)
    lons_2d = codes_df['lon'].to_numpy().reshape(lat_length, lon_length)
    percent_2d = codes_df['Percent'].to_numpy().reshape(lat_length, lon_length)
    
    ##### TRIM
    percent_2d[percent_2d == 0] = 'nan' 
    mx = np.ma.masked_invalid(percent_2d)
    
    mask_cols = ~np.all(mx.mask, axis=0)
    percent_2d = percent_2d[:, mask_cols]
    lats_2d = lats_2d[:, mask_cols]
    lons_2d = lons_2d[:, mask_cols]
    
    mask_rows = np.all(np.isnan(percent_2d) | np.equal(percent_2d, 0), axis=1)
    percent_2d = percent_2d[~mask_rows]
    lats_2d = lats_2d[~mask_rows]
    lons_2d = lons_2d[~mask_rows]
    
    # Convert the projections
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:27700')
    lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)
    
    return lats_2d, lons_2d, percent_2d

    ### Plot
    # fig, ax = plt.subplots(figsize=(20,20))
    # my_plot = ax.pcolormesh(lons_2d, lats_2d, percent_2d,
    #                   linewidths=3, alpha = 1)
    # leeds_gdf.plot(ax= ax, edgecolor='black', color='none', linewidth=5)
    # #fig.colorbar(mypltp, ax=ax, fraction=0.036, pad=0.02)
    # cbar = plt.colorbar(my_plot,fraction=0.036, pad=0.02)
    # cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
    # plt.title(('% of cells in same cluster: '+ stat + '_' + str(num_clusters) + ' clusters'), fontsize=50)