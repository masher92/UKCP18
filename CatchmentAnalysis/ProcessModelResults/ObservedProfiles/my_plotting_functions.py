import itertools
import pandas as pd
import numpy as np

def create_colours_df (short_ids):
    lst = ['darkblue', 'paleturquoise', 'grey', 'indianred', 'darkred']
    colours =['black'] + list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x in lst))
    colours_df = pd.DataFrame({ 'short_id': short_ids, "colour": colours})
    colours_df = colours_df.reindex(colours_df['short_id'].map(dict(zip(short_ids, range(len(short_ids))))).sort_values().index)
    return colours_df

def scatter_plot_with_trend_line(ax, short_ids, x,y,xlabel,ylabel):
    ax.scatter(x, y)
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    ax.plot(x,p(x),"r--")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for i, txt in enumerate(short_ids):
        ax.annotate(txt, (x[i], y[i]))

def make_props_plot (ax, proportions_df, variable, variable_unit, labels):
    
    # reformat the dataframe for stacked plotting
    reformatted_df  =proportions_df.T[1:]
    reformatted_df.columns = labels

    # Plot
    reformatted_df.plot(ax=ax, kind='bar', edgecolor='white', linewidth=3, stacked = True, width =0.8, rot =45,
                         xlabel = 'Flood {} ({})'.format(variable, variable_unit),
                            ylabel = 'Proportion of flooded cells', fontsize = 12)
    plt.rcParams.update({'font.size': 14})
    ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left')


def bar_plot_props (ax, props_df, variable_name, short_ids_order, colours_df):
    
    labels = props_df['index']
    x = np.arange(len(props_df['index']))
    width = 0.3
        
    props_df = props_df[short_ids_order].copy()
    
    colours_df =colours_df.reindex(colours_df['short_id'].map(dict(zip(short_ids_order, range(len(short_ids_order))))).sort_values().index)
    colours_df.reset_index(inplace=True, drop=True)
    
    # counts_df plotting
    width, DistBetweenBars, Num = 0.05, 0.01, 16 # width of each bar, distance between bars, number of bars in a group
    # calculate the width of the grouped bars (including the distance between the individual bars)
    WithGroupedBars = Num*width + (Num-1)*DistBetweenBars        
        
    # Proportions_df plotting
    for i in range(Num):
        ax.bar(np.arange(len(props_df))-WithGroupedBars/2 + (width+DistBetweenBars)*i, props_df.iloc[:,i], width, 
                color = colours_df['colour'][i])
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=30, fontsize = 12)
    ax.set_xlabel('Flood {}'.format(variable_name), fontsize = 15)
    ax.set_ylabel('Proportion of cells', fontsize = 15)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

def plot_totals(cluster_results, short_ids, title):
    
    cluster_results = cluster_results.reindex(totals_df['short_id'].map(dict(zip(short_ids, range(len(short_ids))))).sort_values().index)
    cluster_results.reset_index(inplace=True, drop=True)
    
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize = (28,7))
    y_pos = np.arange(len(totals_df['short_id']))

    ##############################
    # Plot number of flooded cells
    ##############################
    axs[0].bar(y_pos, cluster_results['TotalFloodedArea'].values.tolist(), width = 0.9, color = cluster_results['colour'])
    # Create names on the x-axis
    axs[0].set_xticks(y_pos)
    axs[0].set_xticklabels(short_ids, fontsize =20, rotation = 75)
    axs[0].set_ylabel('Number of flooded cells', fontsize =20)
    axs[0].tick_params(axis='both', which='major', labelsize=15)

    xlocs, xlabs = plt.xticks(y_pos)
    xlocs=[i+1 for i in range(0,19)]
    xlabs=[i/2 for i in range(0,19)]
    
    for i, v in enumerate(cluster_results['TotalFloodedArea'].values.tolist()):
        axs[0].text(xlocs[i] - 1.2, v * 1.025, str(cluster_results["%Diff_FloodedArea_fromSP_formatted"][i]), fontsize = 19, rotation =90)

    ##############################
    # Plot percent difference from single peak
    ##############################
    axs[1].bar(np.arange(len(cluster_results['%Diff_FloodedArea_fromSP'][1:])), cluster_results['%Diff_FloodedArea_fromSP'][1:], width = 0.9, color = cluster_results['colour'][1:])
    # Create names on the x-axis
    axs[1].set_xticks(y_pos[:-1])
    axs[1].set_xticklabels(short_ids[1:], fontsize =20, rotation = 75)
    axs[1].set_ylabel('Number of flooded cells', fontsize =20)
    axs[1].tick_params(axis='both', which='major', labelsize=15)    

    ##############################
    # Plot percent diffference (absoloute)
    ##############################
    axs[2].bar(np.arange(len(cluster_results['Abs%Diff_FloodedArea_fromSP'][1:])), cluster_results['Abs%Diff_FloodedArea_fromSP'][1:], width = 0.9, color = cluster_results['colour'][1:])
    # Create names on the x-axis
    axs[2].set_xticks(y_pos[:-1])
    axs[2].set_xticklabels(short_ids[1:], fontsize =20, rotation = 75)
    axs[2].set_ylabel('% difference from single peak', fontsize =20)
    axs[2].tick_params(axis='both', which='major', labelsize=15)
    
    # Make legend
    colors = ['black','darkblue', 'paleturquoise', 'grey', 'indianred', 'darkred']
    texts = ['FEH','F2','F1','C', 'B1', 'B2'] 
    patches = [ mpatches.Patch(color=colors[i], label="{:s}".format(texts[i]) ) for i in range(len(texts)) ]
    plt.legend(handles=patches, bbox_to_anchor=(1.1, 0.5), loc='center', ncol=1, prop={'size': 15} )
    
    fig.suptitle(title, fontsize = 25)   
    
def plot_difference_levels (fp_for_classified_diff_raster, labels, norm = None):

    # Create discrete cmap
    colors_list = [mpl.cm.viridis(0.1), mpl.cm.viridis(0.5), mpl.cm.viridis(0.7), mpl.cm.viridis(0.9)]
    cmap = mpl.colors.ListedColormap(colors_list)
    cmap.set_over('red')
    cmap.set_under('green')

    # Create labels
    if 'depth' in fp_for_classified_diff_raster:
        labels= ['<-0.1m', '-0.1-0.1m', '0.1-0.3m', '0.3m+']
    else:
        labels = ['<-0.1m/s', '-0.1-0.1m/s', '0.1-0.3m/s', '0.3m/s+']
   
   # Create patches for legend
    patches_list = []
    for i, color in  enumerate(colors_list):
        patch =  mpatches.Patch(color=color, label=labels[i])
        patches_list.append(patch)  

    # plot the new clipped raster      
    clipped = rasterio.open(fp_for_classified_diff_raster)

    # Set up plot instance
    fig, ax = plt.subplots(figsize=(20, 15))
    catchment_gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)
    cx.add_basemap(ax, crs = catchment_gdf.crs.to_string(), url = cx.providers.OpenStreetMap.Mapnik)
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap, norm = norm)
       
    # Close file (otherwise can't delete it, as ref to it is open)
    clipped.close()
    plt.axis('off')
    plt.legend(handles=patches_list, handleheight=3, handlelength=3, fontsize =20)
    
    # Create file path for saving figure to
    method_name = re.search('{}(.*)/'.format(model_directory), fp_for_classified_diff_raster).group(1)
    figs_dir = 'Figs/{}/'.format(method_name)
    plot_fp = figs_dir + re.search('6h_.*/(.*).tif', fp_for_classified_diff_raster).group(1) + ".png"
                                 
    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    plt.close()   
    
def plot_classified_raster(fp_for_classified_raster, labels, colors_list, norm = None):
    
    # Create patches for legend
    patches_list = []
    for i, color in  enumerate(colors_list):
        patch =  mpatches.Patch(color=color, label=labels[i])
        patches_list.append(patch)  
    
    # Create cmap
    cmap = mpl.colors.ListedColormap(colors_list)
    
    # plot the new clipped raster      
    clipped = rasterio.open(fp_for_classified_raster)

    fig, ax = plt.subplots(figsize=(20, 15))
    catchment_gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)
    cx.add_basemap(ax, crs = catchment_gdf.crs.to_string(), url = cx.providers.OpenStreetMap.Mapnik)
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap, norm = norm)

    # Close file (otherwise can't delete it, as ref to it is open)
    clipped.close()

    plt.axis('off')

    plt.legend(handles=patches_list, handleheight=3, handlelength=3, fontsize =20)
    
    # Create file path for saving figure to
    method_name = re.search('{}(.*)/'.format(model_directory), fp_for_classified_raster).group(1)
    figs_dir = 'Figs/{}/'.format(method_name)
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    plot_fp = figs_dir + re.search('6h_.*/(.*).tif', fp_for_classified_raster).group(1) + ".png"

    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    plt.close()  
      
        
def plot_difference_levels_pos_neg (fp_for_posneg_diff_raster, norm = None):

    # Create discrete cmap
    colors_list = ["red", "grey", "green"]
    cmap = mpl.colors.ListedColormap(colors_list)

    # Create patches for legend
    patches_list = []
    labels= ['{} < single peak'.format(fp_for_posneg_diff_raster.split('/')[1]),
             '{} = single peak'.format(fp_for_posneg_diff_raster.split('/')[1]),
             '{} > single peak'.format(fp_for_posneg_diff_raster.split('/')[1])]
    for i, color in  enumerate(colors_list):
        patch =  mpatches.Patch(color=color, label=labels[i])
        patches_list.append(patch)  

    # plot the new clipped raster      
    clipped = rasterio.open(fp_for_posneg_diff_raster)

    # Set up plot instance
    fig, ax = plt.subplots(figsize=(20, 15))
    catchment_gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)
    cx.add_basemap(ax, crs = catchment_gdf.crs.to_string(), url = cx.providers.OpenStreetMap.Mapnik)
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap, norm = norm)

    # Close file (otherwise can't delete it, as ref to it is open)
    clipped.close()

    plt.axis('off')
    plt.legend(handles=patches_list, handleheight=3, handlelength=3, fontsize =15)
    
    # Create file path for saving figure to
    method_name = re.search('{}(.*)/'.format(model_directory), fp_for_posneg_diff_raster).group(1)
    figs_dir = 'Figs/{}/'.format(method_name)
    plot_fp = figs_dir + re.search('6h_.*/(.*).tif', fp_for_posneg_diff_raster).group(1) + ".png"                                 
    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    plt.close()  
    
def plot_worst_case_bars (ax, worst_case_method_df):
    # Remove the np.nan values
    worst_case_method_df = worst_case_method_df.iloc[:5,1]
    # Set scenario names as index
    worst_case_method_df.index = ["singlepeak", "dividetime", "subpeaktiming", "maxspread", "no maximum"]
    # Plot
    worst_case_method_df.plot(ax= ax, kind ='bar',width=  0.9, rot =45, ylabel = 'Number of cells')  
    
def make_totals_bar_plot (ax, totals_df, y_name, ls, colors):
    y_pos = np.arange(len(totals_df.columns))
    ax.bar( y_pos, totals_df.iloc[[0]].values.tolist()[0], color=colors,
            width = 0.9)
    # Create names on the x-axis
    ax.set_xticks(y_pos, totals_df_area.columns, fontsize =10, rotation = 45)
    ax.tick_params(axis= 'both', which = 'major', labelsize =10)

    xlocs, xlabs = plt.xticks()
    xlocs=[i+1 for i in range(0,10)]
    xlabs=[i/2 for i in range(0,10)]

    for i, v in enumerate(totals_df.iloc[[0]].values.tolist()[0]):
        ax.text(xlocs[i] - 1.12, v * 1.015, str(ls[i]), fontsize = 10)
    
def make_bar_plot_by_category (ax, df_to_plot, variable, variable_unit, ylabel, colors):
           
    # Setting up plotting
    width, DistBetweenBars, Num = 0.2, 0.01, 4 # width of each bar, distance between bars, number of bars in a group
    # calculate the width of the grouped bars (including the distance between the individual bars)
    WithGroupedBars = Num* width + (Num-1)*DistBetweenBars

    for i in range(Num):
        ax.bar(np.arange(len(df_to_plot))-WithGroupedBars/2 + (width+DistBetweenBars)*i, df_to_plot.iloc[:,i+1], width, 
                color = colors[i])
    ax.set_xticks(np.arange(len(df_to_plot['index'])), df_to_plot['index'], rotation=30, fontsize = 12)
    ax.set_xlabel('Flood {} ({})'.format(variable,variable_unit), fontsize = 15)
    ax.set_ylabel(ylabel, fontsize = 15)
    
    # Put legend on top left plot
    if ax == axs[0,0]:
        plt.legend(df_to_plot.columns[1:], fontsize=15, frameon = True)    
    
    
def make_props_plot (ax, proportions_df, variable, variable_unit, labels):
    
    # reformat the dataframe for stacked plotting
    reformatted_df  =proportions_df.T[1:]
    
    if variable  == 'Velocity':
        reformatted_df.columns = labels_velocity
    else:
        reformatted_df.columns = labels_depth

    # Plot
    reformatted_df.plot(ax=ax, kind='bar', edgecolor='white', linewidth=3, stacked = True, width =0.8, rot =45,
                         xlabel = 'Flood {} ({})'.format(variable, variable_unit),
                            ylabel = 'Proportion of flooded cells', fontsize = 12)
    plt.rcParams.update({'font.size': 14})
    ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
       
       
    
def make_spatial_plot(ax, fp):
    img = Image.open(fp)
    ax.imshow(img)
    ax.axis('off')   
             