import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import ScalarFormatter

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

def equal_spaced_histogram (results_dict, cols_dict, bin_nos, precip_variable, x_axis_scaling = 'linear', y_axis_scaling = 'linear'):
   
    patches= []
    for key, df in results_dict.items():
        print(key)
        col = cols_dict[key]
        patch = mpatches.Patch(color=col, label=key)
        patches.append(patch)
        
        # Create a histogram and save the bin edges and the values in each bin
        values, bin_edges = np.histogram(df[precip_variable], bins=bin_nos, density=True)
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