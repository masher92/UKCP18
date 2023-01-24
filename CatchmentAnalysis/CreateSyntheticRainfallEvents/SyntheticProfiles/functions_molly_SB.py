import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime
import math

default_peak_shape='refh2-summer'

##### Used in DifferenceBetweenRobertoProfiles_and_SinglePeak
def find_clusters_with_max (difference_df, variable_name, column_name):
    print("Max difference in {} in clusters: ".format(variable_name),difference_df[column_name].nlargest(2).index[0],
          "and ", difference_df[column_name].nlargest(2).index[1])

def find_difference_stats(dictionary_of_data, rainfall_depth_column, rainfall_depth_column_sp, single_peak):
    # Create dataframe to populate with difference stats
    difference_stats = pd.DataFrame(None)
    # Loop through clusters, calculate stats, format as a row and add to the dataframe
    for cluster_number in range(1,16):
        # Get data for this cluster
        cluster = dictionary_of_data[cluster_number]
        # FInd RMSE
        RMSE = math.sqrt(np.square(np.subtract(single_peak[rainfall_depth_column_sp], cluster[rainfall_depth_column])).mean() )
        # Find the maximum rain rate
        max_rain_rate = cluster[rainfall_depth_column].max()
        # Find the difference between the max rain rate in this cluster and for the single-peaked profile
        max_rain_rate_diff = single_peak[rainfall_depth_column_sp].max() - max_rain_rate
        # Find minute in which maximum rain rate occurs
        minute_of_max_rain_rate = cluster[rainfall_depth_column].idxmax()
        # Find the difference between the timing of max rain rate in this cluster and for the single-peaked profile
        minute_of_max_rain_rate_diff = abs(single_peak[rainfall_depth_column_sp].idxmax() - minute_of_max_rain_rate)
        # Format as row, and add to dataframe
        row = pd.DataFrame({'Cluster': cluster_number, 'max_rain_rate': max_rain_rate, 'Max_rain_rate_diff':max_rain_rate_diff,
                          'Max_rain_rate_timing': minute_of_max_rain_rate,  'Max_rain_rate_timing_diff': minute_of_max_rain_rate_diff,
                            'RMSE': RMSE}, index =[cluster_number])
        difference_stats = difference_stats.append(row)

    return difference_stats


def get_one_cluster_one_variable(profiles, cluster_number, duration_bin):
    # Get profiles just for this duration bin
    profiles_this_dur_bin = profiles[profiles['Duration'] ==duration_bin]
    # Get just for one cluster
    one_cluster = profiles_this_dur_bin[profiles_this_dur_bin['Cluster'] ==cluster_number]
    # Put into correct order
    one_cluster = one_cluster.sort_values(by=['Dur_bins'])
    # Remove the initial 0 value
    one_cluster = one_cluster[1:-1]
    # Reset index
    one_cluster.reset_index(inplace=True, drop=True)
    return one_cluster

def find_rainfall_depth_each_min(one_cluster, total_event_rainfall):

    # Find the actual rainfall in each timestep, by multiplying by the total event rainfall for Lin Dyke
    one_cluster['rainfall_this_dur_bin'] = one_cluster['Mean'] * total_event_rainfall

    # Set the value for each of the original timesteps as one 30th of the original value
    one_cluster['rainfall_depth_this_min'] = one_cluster['rainfall_this_dur_bin']/30
    # Then repeat this 30 times (so the value which was originally over 30 minutes, is now split equally 1/30th in each minute)
    one_cluster.reset_index(inplace=True, drop = True)
    one_cluster= one_cluster.loc[one_cluster.index.repeat(30)].reset_index(drop=True)

    # Drop unneeded columns
    one_cluster = one_cluster.drop(["Cluster", "Dur_bins", "Variable", "Duration", "Profile_shape", "Cluster_id", "Mean"], axis =1)

    # Add a starting and ending 0 value
    #new_row = pd.DataFrame(dict(zip(one_cluster.columns.values, [0,0,0])), index = [0])
    #one_cluster = pd.concat([new_row,one_cluster.loc[:],new_row]).reset_index(drop=True)

    # Add a new minutes column
    one_cluster.insert(0, 'minute', range(1,len(one_cluster)+1))

    return one_cluster

def add_cumulative_values(one_cluster):
    # Add a column with the cumulative totals
    one_cluster['cumulative_rainfall_this_dur_bin'] =  one_cluster['rainfall_this_dur_bin'].cumsum()

    # Add a column with the cumulative totals
    one_cluster['cumulative_rainfall_this_min'] =  one_cluster['rainfall_depth_this_min'].cumsum()

    # Keep just minute-ly values
    one_cluster = one_cluster.drop(['rainfall_this_dur_bin', 'cumulative_rainfall_this_dur_bin'],axis=1)

    # Add a rate
    one_cluster['rainfall_rate'] = one_cluster['rainfall_depth_this_min'] * 60

    return one_cluster

def plot_rainfall_depth_each_min(cluster):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize =(15,3))
    ax1.plot(np.array(range(360))+0.5,cluster['rainfall_rate'])
    ax1.set_xlabel('time [mins]')
    ax1.set_ylabel('rainfall rate [mm/hr]')
    ax1.title.set_text("Rainfall rate (mm/hr)")

    ax2.plot(cluster['minute'], cluster['rainfall_depth_this_min'])
    ax2.set_xlabel('time [mins]')
    ax2.set_ylabel("Rainfall depth (mm)")
    ax2.title.set_text("Rainfall depth (mm)")

    ax3.plot(cluster['minute'], cluster['cumulative_rainfall_this_min'])
    ax3.set_ylabel("cumulative rainfall depth (mm)")
    ax3.set_xlabel('time [mins]')
    ax3.title.set_text("Cumulative rainfall depth (mm)")

def make_peak(total_duration_minutes,peak_duration,peak_mm_accum,peak_mid_time,peak_shape,peak_before_frac=0.5):
    a_sum=0.1
    b_sum=0.815
    if(peak_shape=='refh2-summer'):
        peak_accum_curve_mm=np.zeros(total_duration_minutes+1)
        for time in range(total_duration_minutes+1):
            # calculate the actual time of the shifted peak
            peak_after_frac=1-peak_before_frac
            shifted_peak_time=peak_mid_time+(peak_before_frac-0.5)*peak_duration
            duration_before_peak=peak_before_frac*peak_duration
            duration_after_peak=peak_after_frac*peak_duration
            # also calculate normalised fraction
            if(time<shifted_peak_time):
                n_time=(time-shifted_peak_time)/duration_before_peak
            else:
                n_time=(time-shifted_peak_time)/duration_after_peak
            if(n_time<-1.0):
                peak_accum_curve_mm[time]=0.0
            elif(n_time<0.0):
                peak_accum_curve_mm[time]=peak_mm_accum*(peak_before_frac-peak_before_frac*(1-a_sum**((np.abs(n_time))**b_sum))/(1-a_sum))
            elif(n_time<=1.0):
                peak_accum_curve_mm[time]=peak_mm_accum*(peak_before_frac+peak_after_frac*(1-a_sum**((np.abs(n_time))**b_sum))/(1-a_sum))
            elif(n_time>1.0):
                peak_accum_curve_mm[time]=peak_mm_accum
            else:
                raise Exception('Problem getting the peak shape right')
    else:
        raise Exception('Peak shape not defined')
    return peak_accum_curve_mm

# ~ def make_peak(total_duration_minutes,peak_duration,peak_mm_accum,peak_time,peak_shape):
    # ~ a_sum=0.1
    # ~ b_sum=0.815
    # ~ if(peak_shape=='refh2-summer'):
        # ~ peak_accum_curve_mm=np.zeros(total_duration_minutes+1)
        # ~ for time in range(total_duration_minutes+1):
            # ~ # calculate normalised time, -1 being start and 1 end of peak
            # ~ n_time=2.0*(time-peak_time)/peak_duration
            # ~ if(n_time<-1.0):
                # ~ peak_accum_curve_mm[time]=0.0
            # ~ elif(n_time>1.0):
                # ~ peak_accum_curve_mm[time]=peak_mm_accum
            # ~ else:
                # ~ peak_accum_curve_mm[time]=peak_mm_accum*(0.5+np.sign(n_time)*0.5*(1-a_sum**((np.abs(n_time))**b_sum))/(1-a_sum))
    # ~ else:
        # ~ raise Exception('Peak shape not defined')
    # ~ return peak_accum_curve_mm

# This subroutine calculates the
# In principle, accommodate for peaks with different shapes
def make_peaks(total_duration_minutes,peak_durations,peak_mm_accums,peak_times,peak_shapes,peak_before_frac=0.5):
    total_accum=np.zeros(total_duration_minutes+1)
    for i_peak in range(len(peak_durations)):
        peak_duration=peak_durations[i_peak]
        peak_mm_accum=peak_mm_accums[i_peak]
        peak_time=peak_times[i_peak]
        peak_shape=peak_shapes[i_peak]
        total_accum=total_accum+make_peak(total_duration_minutes,peak_duration,peak_mm_accum,peak_time,peak_shape,peak_before_frac)
    return total_accum

def calc_rainfall_curves(method,total_mm_accum,total_duration_minutes,N_subpeaks,subpeak_duration_minutes,peak_before_frac=0.5):
    subpeak_mm_accum=total_mm_accum/N_subpeaks
    if(subpeak_duration_minutes*N_subpeaks>total_duration_minutes and method=='divide-time'):
        print(f"Total length of subpeaks longer than total_duration, divide-time method not sensible")
        return
    if(method=='single-peak'):
        # accumulation curve following REFH2 methodology.
        peak_durations=[total_duration_minutes]
        peak_mm_accums=[total_mm_accum]
        peak_times=[total_duration_minutes/2.] #central times
        peak_shapes=[default_peak_shape]
    elif(method=='divide-time'):
        # accumulation: first peak starts at start, last peak ends at end
        peak_durations=[subpeak_duration_minutes]*N_subpeaks
        peak_mm_accums=[subpeak_mm_accum]*N_subpeaks
        peak_times=(total_duration_minutes/(2.*N_subpeaks))*(1+2.0*np.array(range(N_subpeaks)))
        peak_shapes=[default_peak_shape]*N_subpeaks
    elif(method=='max-spread'):
        # accumulation: peaks equally spaced over period
        peak_durations=[subpeak_duration_minutes]*N_subpeaks
        peak_mm_accums=[subpeak_mm_accum]*N_subpeaks
        peak_times=subpeak_duration_minutes/2.0+((total_duration_minutes-subpeak_duration_minutes)/(N_subpeaks-1))*(np.array(range(N_subpeaks)))
        peak_shapes=[default_peak_shape]*N_subpeaks
    elif(method=='subpeak-timing'):
        # accumulation: peak timing calculated so that Nth part of rainfall
        # falls on average at the same time as in the single peak
        # consider each minute as a block with constant rainfall rate for simplicity
        peak_durations=[subpeak_duration_minutes]*N_subpeaks
        peak_mm_accums=[subpeak_mm_accum]*N_subpeaks
        peak_shapes=[default_peak_shape]*N_subpeaks
        # calculate the single peak, as a reference
        ref_accum=make_peak(total_duration_minutes,total_duration_minutes,total_mm_accum,total_duration_minutes/2.,default_peak_shape,peak_before_frac)
        # calculate peak times for each peak individually
        peak_times=np.zeros(N_subpeaks)
        for i_peak in range(len(peak_durations)):
            accum_start_peak=i_peak*subpeak_mm_accum
            accum_end_peak=(i_peak+1)*subpeak_mm_accum
            prec_time_total=0.
            for time in range(total_duration_minutes):
                time_left=time
                time_right=time+1
                ref_accum_left=ref_accum[time_left]
                ref_accum_right=ref_accum[time_right]
                # fully outside time
                if(ref_accum_left>=accum_end_peak or ref_accum_right<=accum_start_peak):
                    pass
                elif(ref_accum_left>=accum_start_peak and ref_accum_right<=accum_end_peak):
                    # minute fully within peak
                    prec_time_total=prec_time_total+(ref_accum_right-ref_accum_left)*0.5*(time_left+time_right)
                elif(ref_accum_left<=accum_start_peak and ref_accum_right>=accum_start_peak):
                    # this is at the start of peak
                    time_frac=(ref_accum_right-accum_start_peak)/(ref_accum_right-ref_accum_left)
                    time_start_peak=time_right-time_frac
                    prec_time_total=prec_time_total+(ref_accum_right-accum_start_peak)*0.5*(time_start_peak+time_right)
                elif(ref_accum_left<=accum_end_peak and ref_accum_right>=accum_end_peak):
                    # end of peak
                    time_frac=(accum_end_peak-ref_accum_left)/(ref_accum_right-ref_accum_left)
                    time_end_peak=time+time_frac
                    prec_time_total=prec_time_total+(accum_end_peak-ref_accum_left)*0.5*(time_left+time_end_peak)
                else:
                    raise Exception('Unexpected condition in subpeak-timing routine')
            # calculate average time of rainfall arrival
            peak_times[i_peak]=prec_time_total/(accum_end_peak-accum_start_peak)
    accum=make_peaks(total_duration_minutes,peak_durations,peak_mm_accums,peak_times,peak_shapes,peak_before_frac)
    rate=(accum[1:]-accum[:-1])*60. # convert to mm/hr
    return accum,rate

########################################################
########################################################
#### Function to create a plot with 2 subplots:
#### One containing the accumulation over time, for all 4 methods
#### The other containing the rate over time, for all 4 methods
########################################################
########################################################
def pdf_plotter():
    fig, axs = plt.subplots(2,1)
    for method in methods:
        accum,rate=calc_rainfall_curves(method,total_mm_accum,total_duration_minutes,N_subpeaks,subpeak_duration_minutes,peak_before_frac=0.5)
        # WRITING TO TEXT COULD BE DONE HERE
        # NOTE ACCUM ARRAY IS 1 LONGER THAN RATE ARRAY
        axs[0].plot(np.array(range(total_duration_minutes+1)),accum)
        axs[1].plot(np.array(range(total_duration_minutes))+0.5,rate)
    axs[0].set_title('Experiment with '+str(N_subpeaks)+' peaks of '+str(subpeak_duration_minutes)+' minutes each in '+str(total_duration_minutes)+' minutes')
    axs[0].legend(methods,loc='lower right')
    axs[0].set_ylabel('rainfall accumulation [mm]')
    axs[1].set_ylabel('rainfall rate [mm/hr]')
    axs[1].set_xlabel('time [mins]')
    plt.tight_layout()
    plt.show()

########################################################
########################################################
#### Function to plot the rate plot individually for each
#### of the methods
########################################################
########################################################
def pdf_plotter_rate(method, total_mm_accum):
    fig, ax = plt.subplots()
    accum,rate=calc_rainfall_curves(method,total_mm_accum,total_duration_minutes,N_subpeaks,subpeak_duration_minutes)
    # WRITING TO TEXT COULD BE DONE HERE
    # NOTE ACCUM ARRAY IS 1 LONGER THAN RATE ARRAY
    ax.plot(np.array(range(total_duration_minutes))+0.5,rate)
    #axs[0].set_title('Experiment with '+str(N_subpeaks)+' peaks of '+str(subpeak_duration_minutes)+' minutes each in '+str(total_duration_minutes)+' minutes')
    ax.set_ylabel('rainfall rate [mm/hr]')
    ax.set_xlabel('time [mins]')
    plt.tight_layout()
    plt.show()

########################################################
########################################################
#### Create one plot with 4 stacked subplots
#### with each subplot containing the rate plot for each method
########################################################
########################################################
def pdf_plotter_all_rates():
    fig, axs = plt.subplots(4,1, figsize = (5,6), sharey= True, sharex=True)
    for i in range(0,len(methods)):
        print(i)
        accum,rate=calc_rainfall_curves(methods[i],total_mm_accum,total_duration_minutes,N_subpeaks,subpeak_duration_minutes)
        # WRITING TO TEXT COULD BE DONE HERE
        # NOTE ACCUM ARRAY IS 1 LONGER THAN RATE ARRAY
        axs[i].plot(np.array(range(total_duration_minutes))+0.5,rate)
    #axs[3].set_title('Experiment with '+str(N_subpeaks)+' peaks of '+str(subpeak_duration_minutes)+' minutes each in '+str(total_duration_minutes)+' minutes')
    #axs[0].legend(methods,loc='lower right')
        #axs[i].set_ylabel('rainfall rate [mm/hr]')
    #axs[3].set_xlabel('time [mins]')
    fig.text(0.5, 0.0, 'Time [mins]', ha='center', fontsize = 12)
    fig.text(0.0, 0.5, 'Rainfall rate [mm/hr]', va='center', rotation='vertical', fontsize = 12)
    plt.tight_layout()
    #plt.savefig("CatchmentAnalysis/CreateSyntheticRainfallEvents/LinDyke_DataAndFigs/SyntheticEvents_preLossRemoval/{}/{}_allmethods.jpg".format(duration,duration))
    plt.show()

def show_simple_example():
    fig, axs = plt.subplots(2,1)
    accum,rate=calc_rainfall_curves('single-peak',58.,360,1,360,peak_before_frac=0.9)
    # WRITING TO TEXT COULD BE DONE HERE
    # NOTE ACCUM ARRAY IS 1 LONGER THAN RATE ARRAY
    axs[0].plot(np.array(range(360+1)),accum)
    axs[1].plot(np.array(range(360))+0.5,rate)
    axs[0].set_ylabel('rainfall accumulation [mm]')
    axs[1].set_ylabel('rainfall rate [mm/hr]')
    axs[1].set_xlabel('time [mins]')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    show_simple_example()
