import numpy as np
import matplotlib.pyplot as plt

def plot_normalised_intensity(normalised_intensity, category):
    len_intensity = len(normalised_intensity)
    # Time points: start of event, end of event, midpoint of the intervals
    plot_time = np.hstack(
        (
            np.array([0.0]),
            (np.arange(len_intensity) + 0.5) / len_intensity,
            np.array([1.0]),
        )
    )
    # The way Roberto plots the curve, going to 0 at start/end
    extended_intensity = np.hstack(
        (np.array([0.0]), normalised_intensity, np.array([0.0]))
    )
    # Alternative plotting method, which keeps intensity constant at start/end
    # Advantage is that this gives the correct integral under the curve
    # Though it still has some issues (probably every plotting method has issues)
    # extended_intensity_v2 = np.hstack(
    #    (
    #        np.array(normalised_intensity[0]),
    #        normalised_intensity,
    #        np.array(normalised_intensity[-1]),
    #    )
    # )
    plt.plot(plot_time, extended_intensity)
    # plt.plot(plot_time, extended_intensity_v2)
    plt.scatter(plot_time, extended_intensity)
    plt.xlim(0, 1)
    plt.ylim(bottom=0.0)
    plt.xlabel("normalised time")
    plt.ylabel("normalised intensity")
    # plt.legend(("RVH et al.", "alternative"))
    plt.title("event curve, category = " + str(category))
    plt.show()

 ################# Steef functions
def get_normalised_intensity(array_in, len_out):
    len_in = len(array_in)
    # Calculates the total accumulated value at each original point
    # Adds a zero at the start of the array
    csum = np.cumsum(np.hstack((np.array([0.0]), array_in)))
    # Normalise accumulation to 0 to 1
    csum = csum / csum[-1]
    # Array going from 0 up to 1: normalised time
    # corresponding to these points
    normalised_time_in = np.arange(len_in + 1) / (1.0 * len_in)
    # Array of the "time points" corresponding to
    # Boundaries of output intervals
    normalised_time_out = np.arange(len_out + 1) / (1.0 * len_out)
    # Interpolate total accumulated value to desired output points
    csum_out = np.interp(normalised_time_out, normalised_time_in, csum)
    # Interpolate back to accumulations over the desired number of intervals
    # Scale with the number of points to normalise
    normalised_intensity = (csum_out[1:] - csum_out[:-1]) * len_out
    return normalised_intensity

def analyse_event(array_in):
    # Remove leading/trailing zeros from array
    # can we always do this?
    trimmed_array = np.trim_zeros(array_in)
    # Go from raw data directly to 12 and 5 points
    event_curve_12 = get_normalised_intensity(trimmed_array, 12)
    event_curve_12 = np.append([0], event_curve_12)
    event_curve_12 = np.append(event_curve_12, [0])    
    
    event_curve_5 = get_normalised_intensity(trimmed_array, 5)
    # Get the category as a number from 1 to 5
    # add 1 as python indexing starts at 0
    category = np.argmax(event_curve_5) + 1
    return category, event_curve_12