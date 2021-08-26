import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import ScalarFormatter
import pandas as pd

########################################################
# Pre-processing functions
########################################################
def find_min_max_dict_values (dict, precip_variable):
    # Create bin edges based on data in all of the dataframes, i.e. use the same bin edges for all dataframes
    min_values = []
    max_values = []
    for key, df in dict.items():
        max_values.append(df[precip_variable].max())
        min_values.append(df[precip_variable].min())
    max_value = max(max_values)
    min_value = min(min_values)
    return(min_value, max_value)


def find_min_max_dict_values_array (dict):
    # Create bin edges based on data in all of the dataframes, i.e. use the same bin edges for all dataframes
    min_values = []
    max_values = []
    for key, array in dict.items():
        max_values.append(array.max())
        min_values.append(array.min())
    max_value = max(max_values)
    min_value = min(min_values)
    return(min_value, max_value)


def log_discrete_bins(min_value,max_value,bins_if_log_spaced,discretisation):
    # Calculate the bin width on a log axis, for a given minimum value, maximum value and number of bins
    delta_log_i_l_s=(np.log10(max_value)-np.log10(min_value))/bins_if_log_spaced
    # Start at the minimum value (lowest bin edge)
    bin_edges=[min_value]
    prev_edge=min_value
    lstopped=False
    while(lstopped==False):
        log10prev=np.log10(prev_edge)
        # Stop if reached a number greater than the maximum
        if(log10prev>np.log10(max_value)):
            lstopped=True
        else:
            # Find the width of the bin on a linear scale, based on the log spacings calculated above 
            next_delta=10**(log10prev+delta_log_i_l_s)-10**(log10prev)
            # conservative estimate, round bin size to lower number
            next_edge=prev_edge+max(discretisation,discretisation*int(next_delta/discretisation))
            #next_edge = prev_edge+next_delta
            bin_edges.append(next_edge)
            prev_edge=next_edge
    return bin_edges

########################################################
### Plotting functions
########################################################

def equal_spaced_histogram_low_precips (results_dict, cols_dict, bin_nos, precip_variable, x_axis_scaling = 'linear', y_axis_scaling = 'linear'):
   
    patches= []
    for key, df in results_dict.items():
        print(key)
        col = cols_dict[key]
        patch = mpatches.Patch(color=col, label=key)
        patches.append(patch)
        
        low_precips = df[(df[precip_variable] >0) & (df[precip_variable] <2)]
        
        # Specifying like this because gauge data is only at 0.2 intervals, so below this doesnt make sense
        bin_edges = np.arange(0.01,2.01,0.2)
        
        # Create a histogram and save the bin edges and the values in each bin
        values, bin_edges = np.histogram(low_precips[precip_variable], bins=bin_edges, density=True)
        # Calculate the bin central positions
        bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])
        # Draw the plot
        plt.plot(bin_centres, values,linewidth = 1, color = cols_dict[key])
        #plt.plot(bin_centres, values, color='black', marker='o',markersize =1, linewidth=0.5, markerfacecolor = 'red')
        #plt.hist(wethours['Precipitation (mm/hr)'], bins = bin_no, density = True, color = 'white', edgecolor = 'black', linewidth= 0.5)
        
    plt.legend(handles=patches)
    plt.xlabel(precip_variable)
    plt.ylabel('Probability density')
    plt.title(str(bin_nos) + " bins")
    plt.xscale(x_axis_scaling)
    plt.yscale(y_axis_scaling)
   

# Plot with log spaced bins (Holloway, 2012)
def log_spaced_histogram(results_dict, cols_dict, bin_nos, precip_variable, x_axis_scaling = 'linear', y_axis_scaling = 'linear'):
    
    # Find maximum and minimum values across all dataframes in dictionary
    min_value = find_min_max_dict_values(results_dict, precip_variable)[0]
    max_value = find_min_max_dict_values(results_dict, precip_variable)[1]
    
    patches= []
    for key, df in results_dict.items():
        # Define the colour to use for this entry
        # Create a patch for this colour to be used in creating the legend
        # And add to list of patches for use in legend
        col = cols_dict[key]
        patch = mpatches.Patch(color=col, label=key)
        patches.append(patch)
        
        # Create logarithmically spaced bins
        # Need to go slightly under the number e.g. 0.2 otherwise it excluded values of exactly 0.2
        bins = 10 ** np.linspace(np.log10(0.1), np.log10(30), 50)
        #bins = np.logspace(np.log10(min_value-0.01),np.log10(max_value), bin_nos)  
            
        # Use in built np.histogram density calculator to count numbers in each bin
        density, bin_edges = np.histogram(df[precip_variable], bins= bins, density=True)
        bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])  
        # Draw the plot
        plt.plot(bin_centres, density ,linewidth = 1, color = cols_dict[key])
        
    plt.legend(handles=patches)
    plt.xlabel(precip_variable)
    plt.ylabel('Probability density')
    plt.title(str(bin_nos) + " bins")
    plt.xscale(x_axis_scaling)
    plt.yscale(y_axis_scaling)  
    
def fractional_contribution(results_dict, cols_dict, bin_nos, precip_variable, x_axis_scaling = 'linear', y_axis_scaling = 'linear'):
    
    # Find maximum and minimum values across all dataframes in dictionary
    min_value = find_min_max_dict_values(results_dict, precip_variable)[0]
    max_value = find_min_max_dict_values(results_dict, precip_variable)[1]
    
    patches= []
    for key, df in results_dict.items():
        # Define the colour to use for this entry
        # Create a patch for this colour to be used in creating the legend
        # And add to list of patches for use in legend
        col = cols_dict[key]
        patch = mpatches.Patch(color=col, label=key)
        patches.append(patch)
        
        # Create log spaced bins
        #bins = np.logspace(np.log10(min_value-0.01),np.log10(max_value), bin_nos)  
        bins = np.logspace(np.log10(0.1),np.log10(max_value), bin_nos) 
        # Find the numbers of precipitation measurements in each bin   
        freqs, bin_edges = np.histogram(df[precip_variable], bins= bins, density=False)
        # Find the centre point of each bin for plotting
        bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])  
        # Find the sum of the rain rates for all included values
        R = df[precip_variable].sum()
        
        fcs = []
        for i in range(0,len(freqs)):
            # Find parameters
            r = bin_centres[i]
            n_r = freqs[i]   
            delta_r = bin_edges[i+1]  - bin_edges[i]
            # Implement formula
            fc = (r * n_r)/(R*delta_r)
            # Add values to list
            fcs.append(fc)
        # Draw the plot
        plt.plot(bin_centres, freqs ,linewidth = 1, color = cols_dict[key])
        
    plt.legend(handles=patches)
    plt.xlabel(precip_variable)
    plt.ylabel('Fractional contribution to rainfall')
    plt.title(str(bin_nos) + " bins")
    plt.xscale(x_axis_scaling)
    plt.yscale(y_axis_scaling)
        
        
def log_discrete_histogram(results_dict, cols_dict, bin_nos, precip_variable, x_axis_scaling = 'linear', y_axis_scaling = 'linear'):
    
    # Create bin edges based on data in all of the dataframes, i.e. use the same bin edges for all dataframes
    min_value = find_min_max_dict_values(results_dict, precip_variable)[0]
    max_value = find_min_max_dict_values(results_dict, precip_variable)[1]

    # Maybe min value shoudl be set at 0.05 to make the spacings at the right place
    min_value = 0.05
    discretisation=0.1
    bins_if_log_spaced = bin_nos
    
    # Find edges of bins 
    bin_edges=log_discrete_bins(min_value,max_value,bins_if_log_spaced,discretisation)
    #print ("Based on " + str(bins_if_log_spaced) + " log spaced bins, " + str(len(bin_edges)) + " bins created with " + str(min_value) + str (max_value))
   
    patches= []    
    fig, ax = plt.subplots()
    for key, df in results_dict.items():
        # Define the colour to use for this entry
        # Create a patch for this colour to be used in creating the legend
        # And add to list of patches for use in legend
        col = cols_dict[key]
        patch = mpatches.Patch(color=col, label=key)
        patches.append(patch)
        
        # Find the numbers of precipitation measurements in each bin   
        freqs, bin_edges = np.histogram(df[precip_variable], bins= bin_edges, density=True)
        # Find the centre point of each bin for plotting
        bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])    
        # Draw the plot
        plt.plot(bin_centres, freqs ,linewidth = 1, color = cols_dict[key])

    plt.legend(handles=patches)
    plt.xlabel(precip_variable)
    plt.ylabel('Probability density')
    plt.title(str(len(bin_edges)) + " bins")
    plt.xscale(x_axis_scaling)
    plt.yscale(y_axis_scaling)
    #formatter = FormatStrFormatter('%.3f')
    #ax.yaxis.set_major_formatter(formatter)
        
    # Remove scientific notation from y-axis
    # for axis in [ax.yaxis]:
    #     formatter = ScalarFormatter()
    #     formatter.set_scientific(False)
    #     ax.yaxis.set_major_formatter(formatter)


def log_discrete_histogram_lesslegend_array(results_dict, cols_dict, bin_nos, precip_variable, patches, del_zeroes,
                                      xlim, x_axis_scaling = 'linear', y_axis_scaling = 'linear'):
    
    # Create bin edges based on data in all of the dataframes, i.e. use the same bin edges for all dataframes
    min_value = find_min_max_dict_values_array(results_dict)[0]
    max_value = find_min_max_dict_values_array(results_dict)[1]

    # Maybe min value shoudl be set at 0.05 to make the spacings at the right place
    min_value = 0.05
    discretisation=0.2
    bins_if_log_spaced = bin_nos
    
    # Find edges of bins 
    bin_edges_planned =log_discrete_bins(min_value,max_value,bins_if_log_spaced,discretisation)
    #print ("Based on " + str(bins_if_log_spaced) + " log spaced bins, " + str(len(bin_edges)) + " bins created with " + str(min_value) + str (max_value))
   
    # dataframe to store numbers in each bin
    numbers_in_each_bin = pd.DataFrame()
    
    fig, ax = plt.subplots()
    for key, array in results_dict.items():
        print(key)
        # Define the colour to use for this entry
        # Create a patch for this colour to be used in creating the legend
        # And add to list of patches for use in legend
        #col = cols_dict[key]
        #patch = mpatches.Patch(color=col, label=key)
        #patches.append(patch)
        
        # Find the density in each biin  
        freqs, bin_edges = np.histogram(array, bins= bin_edges_planned, density=True)
        # Find the numbers of precipitation measurements in each bin  
        freqs_numbers, bin_edges = np.histogram(array, bins= bin_edges_planned, density=False)
        
        n_bins = str(len(bin_edges))
        
        # Find the centre point of each bin for plotting
        bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])    

        if len(numbers_in_each_bin) ==0:
            numbers_in_each_bin['BinCentres'] = bin_centres
        numbers_in_each_bin[key] = freqs_numbers
        
        # Delete those with a value of 0
        if del_zeroes == True:
            indexes = np.where(freqs == 0)[0]
            freqs = np.delete(freqs, indexes)
            bin_centres= np.delete(bin_centres,indexes)        

        # Draw the plot
        plt.plot(bin_centres, freqs ,linewidth = 1, color = cols_dict[key])
        
    plt.legend(handles=patches)
    plt.xlabel(precip_variable)
    plt.ylabel('Probability density')
    if xlim != False:
        plt.xlim(0,xlim)
    plt.title(n_bins + " bins")
    plt.xscale(x_axis_scaling)
    plt.yscale(y_axis_scaling)
    #plt.show()
    #formatter = FormatStrFormatter('%.3f')
    #ax.yaxis.set_major_formatter(formatter)
        
    # Remove scientific notation from y-axis
    # for axis in [ax.yaxis]:
    #     formatter = ScalarFormatter()
    #     formatter.set_scientific(False)
    #     ax.yaxis.set_major_formatter(formatter)
    
    return numbers_in_each_bin

   
def log_discrete_histogram_lesslegend(results_dict, cols_dict, bin_nos, precip_variable, patches, del_zeroes,
                                      xlim, x_axis_scaling = 'linear', y_axis_scaling = 'log'):
    
    # Create bin edges based on data in all of the dataframes, i.e. use the same bin edges for all dataframes
    min_value = find_min_max_dict_values(results_dict, precip_variable)[0]
    max_value = find_min_max_dict_values(results_dict, precip_variable)[1]
    
    # Maybe min value shoudl be set at 0.05 to make the spacings at the right place
    min_value = 0.05
    discretisation=0.2
    bins_if_log_spaced = bin_nos
    
    # Find edges of bins 
    bin_edges_planned =log_discrete_bins(min_value,max_value,bins_if_log_spaced,discretisation)
    #print ("Based on " + str(bins_if_log_spaced) + " log spaced bins, " + str(len(bin_edges)) + " bins created with " + str(min_value) + str (max_value))
   
    # dataframe to store numbers in each bin
    numbers_in_each_bin = pd.DataFrame()
    
    fig, ax = plt.subplots()
    for key, df in results_dict.items():
        print(key)
        # Define the colour to use for this entry
        # Create a patch for this colour to be used in creating the legend
        # And add to list of patches for use in legend
        
        # Find the density in each biin  
        freqs, bin_edges = np.histogram(df[precip_variable], bins= bin_edges_planned, density=True)
        # Find the numbers of precipitation measurements in each bin  
        freqs_numbers, bin_edges = np.histogram(df[precip_variable], bins= bin_edges_planned, density=False)
        
        n_bins = str(len(bin_edges))
        
        # Find the centre point of each bin for plotting
        bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])    

        if len(numbers_in_each_bin) ==0:
            numbers_in_each_bin['BinCentres'] = bin_centres
        numbers_in_each_bin[key] = freqs_numbers
        
        # Delete those with a value of 0
        if del_zeroes == True:
            indexes = np.where(freqs == 0)[0]
            #freqs = np.delete(freqs, indexes)
            #bin_centres= np.delete(bin_centres,indexes) 
            for i in range(0, len(freqs)):
                if i in indexes:
                    freqs[i] = np.nan

        # Draw the plot
        plt.scatter(bin_centres, freqs ,linewidth = 1,s=3, color = cols_dict[key])
        plt.plot(bin_centres, freqs ,linewidth = 1, color = cols_dict[key])

    plt.legend(handles=patches)
    plt.xlabel(precip_variable)
    plt.ylabel('Probability density')
    if xlim != False:
        plt.xlim(0,xlim)
    #plt.title(n_bins + " bins")
    plt.xscale(x_axis_scaling)
    plt.yscale(y_axis_scaling)
    #plt.show()
    #formatter = FormatStrFormatter('%.3f')
    #ax.yaxis.set_major_formatter(formatter)
        
    # Remove scientific notation from y-axis
    # for axis in [ax.yaxis]:
    #     formatter = ScalarFormatter()
    #     formatter.set_scientific(False)
    #     ax.yaxis.set_major_formatter(formatter)
    
    return numbers_in_each_bin

def log_discrete_with_inset_array(results_dict, cols_dict, bin_nos, precip_variable, patches, del_zeroes,xlim):
    
    # Create bin edges based on data in all of the dataframes, i.e. use the same bin edges for all dataframes
    min_value = find_min_max_dict_values_array(results_dict)[0]
    max_value = find_min_max_dict_values_array(results_dict)[1]

    # Maybe min value shoudl be set at 0.05 to make the spacings at the right place
    min_value = 0.05
    discretisation=0.2
    bins_if_log_spaced = bin_nos
    
    # Find edges of bins 
    bin_edges_planned =log_discrete_bins(min_value,max_value,bins_if_log_spaced,discretisation)
    #print ("Based on " + str(bins_if_log_spaced) + " log spaced bins, " + str(len(bin_edges)) + " bins created with " + str(min_value) + str (max_value))
   
    # dataframe to store numbers in each bin
    numbers_in_each_bin = pd.DataFrame()
    
    
    fig, ax1 = plt.subplots()
    left, bottom, width, height = [0.57, 0.56, 0.3, 0.3]
    ax2=fig.add_axes([left, bottom, width, height])
    
    for key, array in results_dict.items():
        print(key)
       
        # Find the density in each biin  
        freqs, bin_edges = np.histogram(array, bins= bin_edges_planned, density=True)
        # Find the numbers of precipitation measurements in each bin  
        freqs_numbers, bin_edges = np.histogram(array, bins= bin_edges_planned, density=False)
        # Find n_bins
        n_bins = str(len(bin_edges))
        # Find the centre point of each bin for plotting
        bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])    

        if len(numbers_in_each_bin) ==0:
            numbers_in_each_bin['BinCentres'] = bin_centres
        numbers_in_each_bin[key] = freqs_numbers
        
        # Delete those with a value of 0
        if del_zeroes == True:
            indexes = np.where(freqs == 0)[0]
            freqs = np.delete(freqs, indexes)
            bin_centres= np.delete(bin_centres,indexes)        

        # Draw the plot
        ax1.plot(bin_centres, freqs ,linewidth = 1, color = cols_dict[key])
                
        ax1.legend(handles=patches, loc = 'lower left', bbox_to_anchor = (0.15,0.73))
        ax1.set_xlabel(precip_variable)
        ax1.set_ylabel('Probability density')
        if xlim != False:
            ax1.xlim(0,xlim)
        #ax1.set_title(n_bins + " bins")
        ax1.set_xscale('linear')
        ax1.set_yscale('log')
        
    # Inset axis
    #ax2.plot(range(6), color = 'green')                   
    #patches= []
    for key, array in results_dict.items():
        print(key)
        col = cols_dict[key]
        #patch = mpatches.Patch(color=col, label=key)
        #patches.append(patch)
        
        low_precips = array[(array >0) & (array <2)]
        
        # Specifying like this because gauge data is only at 0.2 intervals, so below this doesnt make sense
        bin_edges = np.arange(0.01,2.01,0.2)
        
        # Create a histogram and save the bin edges and the values in each bin
        values, bin_edges = np.histogram(low_precips, bins=bin_edges, density=True)
        # Calculate the bin central positions
        bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])
        # Draw the plot
        ax2.plot(bin_centres, values,linewidth = 1, color = cols_dict[key])
        #plt.plot(bin_centres, values, color='black', marker='o',markersize =1, linewidth=0.5, markerfacecolor = 'red')
        #plt.hist(wethours['Precipitation (mm/hr)'], bins = bin_no, density = True, color = 'white', edgecolor = 'black', linewidth= 0.5)
       
    #plt.legend(handles=patches)
    #ax2.set_xlabel(precip_variable)
    #ax2.set_ylabel('Probability density')
    #ax2.set_title(str(bin_nos) + " bins")
    ax2.set_xscale('linear')
    ax2.set_yscale('linear')
   
    return numbers_in_each_bin
    

def log_discrete_with_inset(results_dict, cols_dict, bin_nos, precip_variable, patches, del_zeroes, xlim):
    
    # Create bin edges based on data in all of the dataframes, i.e. use the same bin edges for all dataframes
    min_value = find_min_max_dict_values(results_dict, precip_variable)[0]
    max_value = find_min_max_dict_values(results_dict, precip_variable)[1]

    # Maybe min value shoudl be set at 0.05 to make the spacings at the right place
    min_value = 0.05
    discretisation=0.2
    bins_if_log_spaced = bin_nos
    
    # Find edges of bins 
    bin_edges_planned =log_discrete_bins(min_value,max_value,bins_if_log_spaced,discretisation)
    #print ("Based on " + str(bins_if_log_spaced) + " log spaced bins, " + str(len(bin_edges)) + " bins created with " + str(min_value) + str (max_value))
   
    # dataframe to store numbers in each bin
    numbers_in_each_bin = pd.DataFrame()
    
    fig, ax1 = plt.subplots()
    left, bottom, width, height = [0.57, 0.56, 0.3, 0.3]
    ax2=fig.add_axes([left, bottom, width, height])
    
    for key, df in results_dict.items():
        print(key)
        # Define the colour to use for this entry
        # Create a patch for this colour to be used in creating the legend
        # And add to list of patches for use in legend
        #col = cols_dict[key]
        #patch = mpatches.Patch(color=col, label=key)
        #patches.append(patch)
        
        # Find the density in each biin  
        freqs, bin_edges = np.histogram(df[precip_variable], bins= bin_edges_planned, density=True)
        # Find the numbers of precipitation measurements in each bin  
        freqs_numbers, bin_edges = np.histogram(df[precip_variable], bins= bin_edges_planned, density=False)
        
        n_bins = str(len(bin_edges))
        
        # Find the centre point of each bin for plotting
        bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])    

        if len(numbers_in_each_bin) ==0:
            numbers_in_each_bin['BinCentres'] = bin_centres
        numbers_in_each_bin[key] = freqs_numbers
        
        # Delete those with a value of 0
        if del_zeroes == True:
            indexes = np.where(freqs == 0)[0]
            freqs = np.delete(freqs, indexes)
            bin_centres= np.delete(bin_centres,indexes)        

        # Draw the plot
        ax1.plot(bin_centres, freqs ,linewidth = 1, color = cols_dict[key])

        ax1.legend(handles=patches, loc = 'lower left', bbox_to_anchor = (0.18,0.7), prop = {"size":8})                
        #ax1.legend(handles=patches, loc = 'lower left', bbox_to_anchor = (0.15,0.73))
        ax1.set_xlabel(precip_variable)
        ax1.set_ylabel('Probability density')
        if xlim != False:
            ax1.xlim(0,xlim)
        #ax1.set_title(n_bins + " bins")
        ax1.set_xscale('linear')
        ax1.set_yscale('linear')
        
    # Inset axis
    #ax2.plot(range(6), color = 'green')                   
    #patches= []
    fig,ax = plt.subplots()
    for key, df in results_dict.items():
        print(key)
        if key in ['Observations Regridded_12km','Model 12km', 'Model 2.2km_regridded_12km']:
            col = cols_dict[key]
            #patch = mpatches.Patch(color=col, label=key)
            #patches.append(patch)
            low_precips = df[(df["Precipitation (mm/hr)"] >=0) & (df["Precipitation (mm/hr)"] <10)]
            if key =='Observations Regridded_12km':
                low_precips["Precipitation (mm/hr)"] = round(low_precips["Precipitation (mm/hr)"],1)
            low_precips_12km = results_dict['Model 12km'][(results_dict['Model 12km']["Precipitation (mm/hr)"] >=0) & (results_dict['Model 12km']["Precipitation (mm/hr)"] <10)]
            low_precips_2_2km = results_dict['Model 2.2km_regridded_12km'][(results_dict['Model 2.2km_regridded_12km']["Precipitation (mm/hr)"] >=0) & (results_dict['Model 2.2km_regridded_12km']["Precipitation (mm/hr)"] <10)]
            
            # Specifying like this because gauge data is only at 0.2 intervals, so below this doesnt make sense
            bin_edges = np.arange(0.1,2.01,0.11)
            
            # Create a histogram and save the bin edges and the values in each bin
            values, bin_edges = np.histogram(low_precips["Precipitation (mm/hr)"], bins=bin_edges, density=True)
            
            # Calculate the bin central positions
            bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])
            # Draw the plot
            plt.plot(bin_centres, values,linewidth = 1, color = cols_dict[key])
            #plt.plot(bin_centres, values, color='black', marker='o',markersize =1, linewidth=0.5, markerfacecolor = 'red')
            #plt.hist(wethours['Precipitation (mm/hr)'], bins = bin_no, density = True, color = 'white', edgecolor = 'black', linewidth= 0.5)
            plt.legend(handles=patches)
            ax.set_yscale('linear')
    #plt.legend(handles=patches)
    #ax2.set_xlabel(precip_variable)
    #ax2.set_ylabel('Probability density')
    #ax2.set_title(str(bin_nos) + " bins")
    ax2.set_xscale('linear')
    ax2.set_yscale('linear')
   
    return numbers_in_each_bin


# Only difference is in how keys is specified to the colors dict
def log_discrete_histogram_BaselinevsFuture(results_dict, cols_dict, bin_nos, precip_variable, patches, del_zeroes,
                                      xlim, x_axis_scaling = 'linear', y_axis_scaling = 'linear'):

    # Create bin edges based on data in all of the dataframes, i.e. use the same bin edges for all dataframes
    min_value = find_min_max_dict_values(results_dict, precip_variable)[0]
    max_value = find_min_max_dict_values(results_dict, precip_variable)[1]

    # Maybe min value shoudl be set at 0.05 to make the spacings at the right place
    min_value = 0.05
    discretisation=0.2
    bins_if_log_spaced = bin_nos
    
    # Find edges of bins 
    bin_edges_planned =log_discrete_bins(min_value,max_value,bins_if_log_spaced,discretisation)
    #print ("Based on " + str(bins_if_log_spaced) + " log spaced bins, " + str(len(bin_edges)) + " bins created with " + str(min_value) + str (max_value))
   
    # dataframe to store numbers in each bin
    numbers_in_each_bin = pd.DataFrame()
    
    fig, ax = plt.subplots()
    for key, df in results_dict.items():
        print(key)
        print(df['Precipitation (mm/hr)'].max())
        print(df['Precipitation (mm/hr)'].min())        
        # Define the colour to use for this entry
        # Create a patch for this colour to be used in creating the legend
        # And add to list of patches for use in legend
        #col = cols_dict[key]
        #patch = mpatches.Patch(color=col, label=key)
        #patches.append(patch)
        
        # Find the density in each biin  
        freqs, bin_edges = np.histogram(df[precip_variable], bins= bin_edges_planned, density=True)
        # Find the numbers of precipitation measurements in each bin  
        freqs_numbers, bin_edges = np.histogram(df[precip_variable], bins= bin_edges_planned, density=False)
        
        n_bins = str(len(bin_edges))
        
        # Find the centre point of each bin for plotting
        bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])    

        if len(numbers_in_each_bin) ==0:
            numbers_in_each_bin['BinCentres'] = bin_centres
        numbers_in_each_bin[key] = freqs_numbers
        
        # Delete those with a value of 0
        if del_zeroes == True:
            indexes = np.where(freqs == 0)[0]
            freqs = np.delete(freqs, indexes)
            bin_centres= np.delete(bin_centres,indexes)        

        # Draw the plot     
        plt.plot(bin_centres, freqs ,linewidth = 1, color = cols_dict[key[5:]])
        
    plt.legend(handles=patches)
    plt.xlabel(precip_variable)
    plt.ylabel('Probability density')
    if xlim != False:
        plt.xlim(0,xlim)
    plt.title(n_bins + " bins")
    plt.xscale(x_axis_scaling)
    plt.yscale(y_axis_scaling)

    return numbers_in_each_bin



# Testing plotting with bands for lowest and highest ensemble member values
def with_spread_bands(results_dict, cols_dict, bin_nos, precip_variable, patches, del_zeroes,
                                      xlim, x_axis_scaling = 'linear', y_axis_scaling = 'linear'):

    # Create bin edges based on data in all of the dataframes, i.e. use the same bin edges for all dataframes
    min_value = find_min_max_dict_values(results_dict, precip_variable)[0]
    max_value = find_min_max_dict_values(results_dict, precip_variable)[1]

    # Maybe min value shoudl be set at 0.05 to make the spacings at the right place
    min_value = 0.05
    discretisation=0.2
    bins_if_log_spaced = bin_nos
    
    # Find edges of bins 
    bin_edges_planned =log_discrete_bins(min_value,max_value,bins_if_log_spaced,discretisation)
    #print ("Based on " + str(bins_if_log_spaced) + " log spaced bins, " + str(len(bin_edges)) + " bins created with " + str(min_value) + str (max_value))
   
    # dataframe to store numbers in each bin
    numbers_in_each_bin = pd.DataFrame()
    
    # Create a dataframe to store the frequency values for each bin for each EM
    freqs_df = pd.DataFrame()
    # Find the frequency for each ensemble member    
    for key, df in results_dict.items():
        # Find the density in each biin  
        freqs, bin_edges = np.histogram(df[precip_variable], bins= bin_edges_planned, density=True)
        # Find the numbers of precipitation measurements in each bin  
        freqs_numbers, bin_edges = np.histogram(df[precip_variable], bins= bin_edges_planned, density=False)
        # Add to dataframe
        freqs_df[key]=freqs
    # Find max and min values across the ensemble members   
    maxs = freqs_df.max(axis=1)  
    mins = freqs_df.min(axis=1)  
    
    ## Create a new dictionary containing just combined
    joined_ems = pd.concat(em_csvs.values(),ignore_index = True)
    keys_to_remove =('otley_s.wks_logger_UKCP18Data01', 'otley_s.wks_logger_UKCP18Data04', 'otley_s.wks_logger_UKCP18Data05', 'otley_s.wks_logger_UKCP18Data06', 'otley_s.wks_logger_UKCP18Data07', 'otley_s.wks_logger_UKCP18Data08', 'otley_s.wks_logger_UKCP18Data09', 'otley_s.wks_logger_UKCP18Data10', 'otley_s.wks_logger_UKCP18Data11', 'otley_s.wks_logger_UKCP18Data12', 'otley_s.wks_logger_UKCP18Data13', 'otley_s.wks_logger_UKCP18Data15')
    for key in keys_to_remove:
        if key in results_dict:
            del results_dict[key]
    results_dict[station_name + '_UKCP18Data'] = joined_ems
    
    # ##### Between min and max
    # fig, ax = plt.subplots()
    # ax.plot(bin_centres, mins, bin_centres, maxs)
    # ax.fill_between(bin_centres, mins, maxs, facecolor = 'lightblue')
    # plt.xscale(x_axis_scaling)
    # plt.yscale(y_axis_scaling)
    
    
    fig, ax = plt.subplots()
    for key, df in results_dict.items():
        # Find the density in each biin  
        freqs, bin_edges = np.histogram(df[precip_variable], bins= bin_edges_planned, density=True)
        # Find the numbers of precipitation measurements in each bin  
        freqs_numbers, bin_edges = np.histogram(df[precip_variable], bins= bin_edges_planned, density=False)
        # Add to dataframe
        freqs_df[key]=freqs
        
        print(key)
        n_bins = str(len(bin_edges))
        
        # Find the centre point of each bin for plotting
        bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])    

        if len(numbers_in_each_bin) ==0:
            numbers_in_each_bin['BinCentres'] = bin_centres
        numbers_in_each_bin[key] = freqs_numbers
        
        # Delete those with a value of 0
        if del_zeroes == True:
            indexes = np.where(freqs == 0)[0]
            freqs = np.delete(freqs, indexes)
            bin_centres= np.delete(bin_centres,indexes)        

        # Draw the plot     
        plt.plot(bin_centres, freqs ,linewidth = 1)#, color = cols_dict[key])
      
    ax.plot(bin_centres, mins,'g--' ,bin_centres, maxs,'g--')
    ax.fill_between(bin_centres, mins, maxs, facecolor = 'lightgreen')
    plt.xscale(x_axis_scaling)
    plt.yscale(y_axis_scaling) 
      
        
    plt.legend(handles=patches)
    plt.xlabel(precip_variable)
    plt.ylabel('Probability density')
    if xlim != False:
        plt.xlim(0,xlim)
    plt.title(n_bins + " bins")
    plt.xscale(x_axis_scaling)
    plt.yscale(y_axis_scaling)

    return numbers_in_each_bin


x_axis_scaling = 'linear'
y_axis_scaling = 'log'




     
## Holloway method manually applied
# # Find the numbers of precipitation measurements in each bin   
# freqs, bin_edges = np.histogram(df['Precipitation (mm/hr)'], bins= bins, density=False)
# # Find the centre point of each bin for plotting
# bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])    
   
# # Find the density of each bin as the number of measurements in the bin divided 
# # by the sum of the the total number of measurememnts in the dataset and the 
# # bin width in mm/hr
# densities = []
# for i in range(0,len(freqs)):
#     bin_width = bin_edges[i+1]  - bin_edges[i]
#     density = freqs[i] /(bin_width*df['Precipitation (mm/hr)'].count())
#     densities.append(density)