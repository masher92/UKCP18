run_number =19
stat = 'jja_p99'

em_cube_stat = 'EM_mean'
overlapping = ''
region = 'leeds-at-centre-narrow'

def create_leeds_at_centre_narrow_outline (required_proj):
    # #Read in outline of Leeds wards  
    # wards = gpd.read_file("/nfs/a319/gy17m2a/datadir/SpatialData/england_cmwd_2011.shp")
    # # Create column to merge on
    # wards['City'] = 'Leeds'
    # # Merge all wards into one outline
    # leeds = wards.dissolve(by = 'City')

    # # Convert Leeds outline geometry to WGS84
    # leeds.crs = {'init' :'epsg:27700'}
    # leeds_gdf = leeds.to_crs(required_proj)

    # leeds_gdf_square = leeds_gdf.envelope
    # leeds_at_centre_narrow_gdf = gpd.GeoDataFrame(gpd.GeoSeries(leeds_gdf_square), columns = ['geometry'], crs={'init': 'epsg:3857'},)

    # #Define lats and lons to make box around Leeds
    # lons = [54.2, 54.2, 53.2, 53.2]
    # lats = [-1.80,-1.3, -1.3, -1.80] 
    
    # #first two control height above outlnie (bigger number extends it higher)
    # second 2 (smaller number extends it down)
    # #First and last control left hand verticla sdie (smaller number moves it to right)

    #### 1. 
    # lons = [54.2, 54.2, 53.2, 53.2]
    # lats = [-1.50,-1.0, -1.0, -1.50] 

    # ### 2.
    # lons = [54.0, 54.0, 53.6, 53.6]
    # lats = [-1.50,-1.0, -1.0, -1.50] 

    # ### 3.
    # # leeds bouding box
    
    # ###4.
    # lons = [54.0, 54.0, 53.6, 53.6]
    # lats = [-1.50,-0.8, -0.8, -1.50] 

    # ### 5.
    # lons = [54.0, 54.0, 53.6, 53.6]
    # lats = [-2.0,-1.5, -1.5, -2.0] 
    
    # ###6.
    # lons = [54.2, 54.2, 53.75, 53.75]
    # lats = [-1.82,-1.29, -1.29, -1.82] 
    
    # ### 7.
    # lons = [53.85, 53.85, 53.55, 53.55]
    # lats = [-1.82,-1.29, -1.29, -1.82] 
    
    ### 8.
    # lons = [53.94, 53.94, 53.68, 53.68]
    # lats = [-1.50,-0.94, -0.94, -1.50] 
    
    ### 9.
    # lons = [53.94, 53.94, 53.68, 53.68]
    # lats = [-1.82,-0.94, -0.94, -1.82]     
    
    ## 10. leeds box
    # lons = [53.94, 53.94, 53.68, 53.68]
    # lats = [-1.82,-1.28, -1.28, -1.82]    
    
    ### 11. 
    # lons = [53.94, 53.94, 53.68, 53.68]
    # lats = [-1.99,-1.28, -1.28, -1.99]   
    
    ### 12
    # lons = [54.04, 54.04 ,53.68, 53.68]
    # lats = [-1.82,-1.28, -1.28, -1.82]        
     
    ### 13.     
    # lons = [53.94, 53.94, 53.68, 53.68]
    # lats = [-1.82,-1.28, -1.28, -1.82]    
    
    # 14
    # lons = [53.94, 53.94, 53.68, 53.68]
    # lats = [-1.53,-1.0, -1.0, -1.53] 
   
    # 15
    # lons = [53.94, 53.94, 53.68, 53.68]
    # lats = [-2.00,-1.53, -1.53, -2.00] 
 
    # 16
    # lons = [53.94, 53.94, 53.68, 53.68]
    # lats = [-1.82,-1.54, -1.54, -1.82] 

    # 17
    # lons = [53.94, 53.94, 53.68, 53.68]
    # lats = [-1.54,-1.28, -1.28, -1.54] 
    
    # 18. 
    lons = [54.04, 54.04, 53.81, 53.81]
    lats = [-1.82,-1.28, -1.28, -1.82]      
     
    # 19. 
    lons = [53.81, 53.81, 53.57, 53.57]
    lats = [-1.82,-1.28, -1.28, -1.82]       
    
           
    # Convert to polygon
    polygon_geom = Polygon(zip(lats, lons))
    # Convert to geodataframe
    leeds_at_centre_narrow_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
    leeds_at_centre_narrow_gdf = leeds_at_centre_narrow_gdf.to_crs(required_proj) 

    return leeds_at_centre_narrow_gdf

leeds_at_centre_narrow_gdf = create_leeds_at_centre_narrow_outline({'init' :'epsg:3857'})

# Load in the cube for the correct statistic and ensemble summary metric 
stats_cube = iris.load("Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Summaries/{}_{}{}.nc".format(stat, em_cube_stat, overlapping))[0]
  
# Trim to smaller area
if region == 'Northern':
        stats_cube = trim_to_bbox_of_region(stats_cube, wider_northern_gdf)
elif region == 'leeds-at-centre':
        stats_cube = trim_to_bbox_of_region(stats_cube, leeds_at_centre_gdf)
elif region == 'leeds':
        stats_cube = trim_to_bbox_of_region(stats_cube, leeds_gdf)    
elif region == 'leeds-at-centre-narrow':
        stats_cube = trim_to_bbox_of_region(stats_cube, leeds_at_centre_narrow_gdf)                       
        
# Mask the data so as to cover any cells not within the specified region 
if region == 'Northern':
        stats_cube.data = ma.masked_where(wider_northern_mask == 0, stats_cube.data)
        # Trim to the BBOX of Northern England
        # This ensures the plot shows only the bbox around northern england
        # but that all land values are plotted
        stats_cube = trim_to_bbox_of_region(stats_cube, northern_gdf)
elif region == 'UK':
        stats_cube.data = ma.masked_where(uk_mask == 0, stats_cube.data)  
  
# Find the minimum and maximum values to define the spread of the pot
local_min = stats_cube.data.min()
local_max = stats_cube.data.max()
#local_min = 2.17
#local_max = 2.70
contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)

#############################################################################
# Set up environment for plotting
#############################################################################
# Set up plotting colours
precip_colormap = create_precip_cmap()   
# Set up a plotting figurge with Web Mercator projection
proj = ccrs.Mercator.GOOGLE
fig = plt.figure(figsize=(20,20), dpi=200)
ax = fig.add_subplot(122, projection = proj)
   
# Define number of decimal places to use in the rounding of the colour bar
# This ensures smaller numbers have decimal places, but not bigger ones.  
if stats_cube.data.max() >10:
    n_decimal_places = 0
elif stats_cube.data.max() < 0.1:
    n_decimal_places  =3
else:
    n_decimal_places =2
    
#############################################################################
# Plot
#############################################################################
mesh = iplt.pcolormesh(stats_cube, cmap = precip_colormap, vmin = local_min, vmax = local_max)
     
# Add regional outlines, depending on which region is being plotted
if region == 'Northern':
       leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
       northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
       cb1 = plt.colorbar(mesh, ax=ax, fraction=0.053, pad=0.03, boundaries = contour_levels)
elif region == 'leeds-at-centre' or region == 'leeds' or region == 'leeds-at-centre-narrow':
       leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2.3)
       cb1 = plt.colorbar(mesh, ax=ax, fraction=0.041, pad=0.03, 
                         boundaries = contour_levels)
elif region == 'UK':
       plt.gca().coastlines(linewidth =0.5)
       cb1 = plt.colorbar(mesh, ax=ax, fraction=0.049, pad=0.03, 
                         boundaries = contour_levels)
cb1.ax.tick_params(labelsize=25)
if stat != 'whprop':
    cb1.set_label('mm/hr', size = 25)
elif stat == 'whprop':
    cb1.set_label('%', size = 25)
cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])   

percent_diff = round((local_max-local_min)/((local_max+local_min)/2)*100,2)
print(percent_diff)

num_cells = stats_cube.shape[0] * stats_cube.shape[1] 
print(num_cells)

# Save files
filename = "Scripts/UKCP18/RegionalRainfallStats/Model/Figs/Testing_{}_{}_{}%_{}cells.png".format(stat, run_number, percent_diff, num_cells)
fig.savefig(filename, bbox_inches = 'tight')
  


