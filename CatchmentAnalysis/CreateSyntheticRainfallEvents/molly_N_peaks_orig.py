# Plot rainfall rates (mm/hr) and cumulative rainfall
# for a multi-peak simulation
# Use 1-minute time steps

## NOTE: CURVES ARE CURRENTLY NOT WRITTEN TO TEXT

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

## DIFFERENT METHODS EXPLORED IN SCRIPT
methods=['single-peak','divide-time','max-spread','subpeak-timing']

## PARAMETER SETTINGS
total_duration_minutes=360 # needs to be an integer
N_subpeaks=3
subpeak_duration_minutes=60.
total_mm_accum=40.
default_peak_shape='refh2-summer'

def make_peak(total_duration_minutes,peak_duration,peak_mm_accum,peak_time,peak_shape):
    a_sum=0.1
    b_sum=0.815
    if(peak_shape=='refh2-summer'):
        peak_accum_curve_mm=np.zeros(total_duration_minutes+1)
        for time in range(total_duration_minutes+1):
            # calculate normalised time, -1 being start and 1 end of peak
            n_time=2.0*(time-peak_time)/peak_duration
            if(n_time<-1.0):
                peak_accum_curve_mm[time]=0.0
            elif(n_time>1.0):
                peak_accum_curve_mm[time]=peak_mm_accum
            else:
                peak_accum_curve_mm[time]=peak_mm_accum*(0.5+np.sign(n_time)*0.5*(1-a_sum**((np.abs(n_time))**b_sum))/(1-a_sum))
    else:
        raise Exception('Peak shape not defined')
    return peak_accum_curve_mm

# This subroutine calculates the
# In principle, accommodate for peaks with different shapes
def make_peaks(total_duration_minutes,peak_durations,peak_mm_accums,peak_times,peak_shapes):
    total_accum=np.zeros(total_duration_minutes+1)
    for i_peak in range(len(peak_durations)):
        peak_duration=peak_durations[i_peak]
        peak_mm_accum=peak_mm_accums[i_peak]
        peak_time=peak_times[i_peak]
        peak_shape=peak_shapes[i_peak]
        total_accum=total_accum+make_peak(total_duration_minutes,peak_duration,peak_mm_accum,peak_time,peak_shape)
    return total_accum

def calc_rainfall_curves(method,total_mm_accum,total_duration_minutes,N_subpeaks,subpeak_duration_minutes):
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
        ref_accum=make_peak(total_duration_minutes,total_duration_minutes,total_mm_accum,total_duration_minutes/2.,default_peak_shape)
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
    accum=make_peaks(total_duration_minutes,peak_durations,peak_mm_accums,peak_times,peak_shapes)
    rate=(accum[1:]-accum[:-1])*60. # convert to mm/hr
    return accum,rate

def pdf_plotter():
    fig, axs = plt.subplots(2,1)
    for method in methods:
        accum,rate=calc_rainfall_curves(method,total_mm_accum,total_duration_minutes,N_subpeaks,subpeak_duration_minutes)
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

pdf_plotter()
