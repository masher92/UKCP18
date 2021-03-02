import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt


###### LCC SHAPEFILES
shapefile = gpd.read_file("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/LeedsCatchments/LeedsCatchments.shp")
shapefile['PLAN_AREA_km2'] = shapefile['PLAN_AREA']/1000000
print(shapefile)

# Plot
shapefile.plot(facecolor = 'None', edgecolor = 'black')


fig, ax = plt.subplots(1, 1)
shapefile.plot(column='PLAN_AREA_km2', ax=ax, legend=True)
shapefile.plot(column='PLAN_AREA_km2',   cmap='OrRd',
             legend=True,legend_kwds={'label': "Area (km2)",
                                      'orientation': "vertical"})

####################################################################################
# FEH Shapefiles
####################################################################################
# Define rootfp and set as working directory
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/IndividualCatchments/"
os.chdir(root_fp)

catchment_names  = glob.glob("*")
del concat_shps
for catchment_name in catchment_names:
    print(catchment_name)   
    # Shapefiles
    shpfile_name = glob.glob("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/IndividualCatchments/{}/Shapefile/*.shp".format(catchment_name))
    
    if "concat_shps" not in globals():
        concat_shps = gpd.read_file(shpfile_name[0])
    else:
         shp = gpd.read_file(shpfile_name[0])   
         print(shp.name)
         concat_shps = pd.concat([concat_shps,shp])
         
    # Catchment Descriptors     
    filename = glob.glob(root_fp + "{}/CatchmentDescriptors/*.csv".format(catchment_name))[0]
    catchment_descriptors = pd.read_csv(filename)
    catchment_descriptors =catchment_descriptors[2:]     
    catchment_descriptors = catchment_descriptors[catchment_descriptors.columns[0:2]]
    
    if "df" not in globals():
        print("True")
        df = catchment_descriptors

    df[catchment_name]=catchment_descriptors[' "FEH CD-ROM"']    
    # Convert column to numeric
    df[catchment_name] =pd.to_numeric(df[catchment_name])    
    
# Rename columns
df.rename(columns={"VERSION": "Catchment Descriptor"}, inplace = True)

# Reformat
transposed = df.transpose()
transposed.rename(columns=transposed.iloc[0], inplace = True)
transposed = transposed[1:]
transposed = transposed.reset_index()
concat_shps = concat_shps.reset_index()
transposed['name'] = concat_shps['name']

cols = transposed.columns[1:38]
transposed[cols] = transposed[cols].apply(pd.to_numeric, errors='coerce', axis=1)


concat_shps = concat_shps.merge(transposed, on='name')
   
# Plot
concat_shps.plot()

fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])
ax.axis('off')
concat_shps.plot(ax=ax, column='ALTBAR',   cmap='OrRd', edgecolor = 'black',
             legend=True,legend_kwds={'label': "Metres above sea level",
                                      'orientation': "vertical"})
# Save and show plot
plt.savefig("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/Catchments_matching_FEH_ALTBAR_spatialplot.PNG",
            bbox_inches='tight')
plt.show()


fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])
ax.axis('off')
concat_shps.plot(ax=ax, column='URBEXT2000',   cmap='OrRd', edgecolor = 'black',
             legend=True,legend_kwds={'label': "Urban Extent",
                                      'orientation': "vertical"})
# Save and show plot
plt.savefig("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/Catchments_matching_FEH_URBEXT_spatialplot.PNG",
            bbox_inches='tight')
plt.show()


fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])
ax.axis('off')
concat_shps.plot(ax=ax, column='BFIHOST',   cmap='OrRd', edgecolor = 'black',
             legend=True,legend_kwds={'label': "BFIHOST",
                                      'orientation': "vertical"})
# Save and show plot
plt.savefig("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/Catchments_matching_FEH_BFIHOST_spatialplot.PNG",
            bbox_inches='tight')
plt.show()

fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])
ax.axis('off')
concat_shps.plot(ax=ax, column='SAAR',   cmap='OrRd', edgecolor = 'black',
             legend=True,legend_kwds={'label': "SAAR (mm)",
                                      'orientation': "vertical"})
# Save and show plot
plt.savefig("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/Catchments_matching_FEH_SAAR_spatialplot.PNG",
            bbox_inches='tight')
plt.show()
