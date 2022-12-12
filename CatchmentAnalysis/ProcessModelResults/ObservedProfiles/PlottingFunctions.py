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


def bar_plot_props (ax, props_df, variable_name, short_ids_order, colours):
    
    labels = props_df['index']
    x = np.arange(len(props_df['index']))
    width = 0.3
        
    props_df = props_df[short_ids_order].copy()
    colours_formatted_ls = colours[short_ids_order].copy()         
    colours_formatted_ls = colours_formatted_ls.loc['colour'].tolist()
    # counts_df plotting
    width, DistBetweenBars, Num = 0.05, 0.01, 16 # width of each bar, distance between bars, number of bars in a group
    # calculate the width of the grouped bars (including the distance between the individual bars)
    WithGroupedBars = Num*width + (Num-1)*DistBetweenBars        
        
    # Proportions_df plotting
    for i in range(Num):
        ax.bar(np.arange(len(props_df))-WithGroupedBars/2 + (width+DistBetweenBars)*i, props_df.iloc[:,i], width, 
                color = colours_formatted_ls[i])
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=30, fontsize = 12)
    ax.set_xlabel('Flood {}'.format(variable_name), fontsize = 15)
    ax.set_ylabel('Proportion of cells', fontsize = 15)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    
def plot_totals(totals_df, percent_diffs_df, short_ids_order, plot_title, colours):
    
    patches_list = []
    labels= ['FEH','F2', 'F1', 'C', 'B1', 'B2']
    colors = ['black', 'darkblue', 'lightblue', 'grey', 'indianred', 'darkred']
    for i, color in  enumerate(colors):
        patch =  mpatches.Patch(color=color, label=labels[i])
        patches_list.append(patch)  
    patches_list
    
    percent_diffs_df = percent_diffs_df[short_ids_order].copy()
    totals_df = totals_df[short_ids_order].copy()
    colours_formatted = colours[short_ids_order].copy() 
    colours_formatted_ls = colours_formatted.loc['colour'].tolist()
    
    fig, axs = plt.subplots(nrows=1, ncols=3, constrained_layout=True, figsize = (30,16))
    y_pos = np.arange(len(totals_df.columns))

    ##############################
    # Plot number of flooded cells
    ##############################
    plt.subplot(231)
    plt.bar(y_pos, totals_df.iloc[[0]].values.tolist()[0], width = 0.9, color = colours_formatted_ls, label = labels)
    # Create names on the x-axis
    plt.xticks(y_pos, short_ids_order, fontsize =20, rotation = 75)
    # plt.xlabel('Method')
    plt.ylabel('Number of flooded cells', fontsize =20)

    xlocs, xlabs = plt.xticks(y_pos)
    xlocs=[i+1 for i in range(0,19)]
    xlabs=[i/2 for i in range(0,19)]

    for i, v in enumerate(totals_df.iloc[[0]].values.tolist()[0]):
        plt.text(xlocs[i] - 1.2, v * 1.025, str(percent_diffs_df.T['percent_diffs_formatted'][i]), fontsize = 19, rotation =90)

    ##############################
    # Plot flooded extent in m2
    # ##############################
    percent_diffs_df_no_sp = percent_diffs_df.T
    # Remove the single peak from the order
    percent_diffs_df_no_sp= percent_diffs_df_no_sp.drop('6h_sp')
    short_ids_order = [x for x in short_ids_order if x != '6h_sp']

    plt.subplot(232)
    plt.bar(np.arange(len(percent_diffs_df_no_sp['percent_diffs'])), percent_diffs_df_no_sp['percent_diffs'], 
            width = 0.9, color = colours_formatted_ls[1:], label = labels)
    # Create names on the x-axis
    plt.xticks(np.arange(len(percent_diffs_df_no_sp['percent_diffs'])), short_ids_order, fontsize =20, rotation = 75)
    # plt.xlabel('Method')
    plt.ylabel('Percentage difference from single peak', fontsize =20)
    fig.suptitle(plot_title, fontsize = 30);
    
    #
    plt.subplot(233)
    plt.bar(np.arange(len(percent_diffs_df_no_sp['percent_diffs_abs'])), percent_diffs_df_no_sp['percent_diffs_abs'], 
            width = 0.9, color = colours_formatted_ls[1:], label = labels)
    # Create names on the x-axis
    plt.xticks(np.arange(len(percent_diffs_df_no_sp['percent_diffs_abs'])), short_ids_order, fontsize =20, rotation = 75)
    # plt.xlabel('Method')
    plt.ylabel('Percentage difference from single peak', fontsize =20)
    plt.legend()
    #fig.suptitle("a big long suptitle that runs into the title\n"*2, y=1.05);
    fig.suptitle(plot_title, fontsize = 30);
    plt.legend(handles=patches_list, handleheight=3, handlelength=3, fontsize =15, 
                bbox_to_anchor=(1.2,0.8), ncol=1)  
    
    
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
             