# Plot rainfall rates (mm/hr) and cumulative rainfall
# for a multi-peak simulation
# Use 1-minute time steps

## NOTE: CURVES ARE CURRENTLY NOT WRITTEN TO TEXT


########################################################
########################################################
#### Create dataframe for one method containing the accumulation
#### and rate at each minute of time
########################################################
######################################################## 
## DIFFERENT METHODS EXPLORED IN SCRIPT
methods=['single-peak','divide-time','max-spread','subpeak-timing']
durations = ['1h', '3h', '6h']

# For each method produce a dataframe containing precipitation values for each minute
# and save these to file
for duration in ['6h']:
    for method in methods:
        print(method, duration)
        
        ## PARAMETER SETTINGS
        N_subpeaks= 3
        total_duration_minutes= int(duration[0]) * 60
        subpeak_duration_minutes=total_duration_minutes/6
        if duration == '1h':
            total_mm_accum= 38.7
        elif duration == '3h':
            total_mm_accum= 51.3
        elif duration == '6h':
              total_mm_accum= 59.98
        default_peak_shape='refh2-summer'
        
        # Create datetimes to go with values
        start = datetime(2022,4,5,0,0,0)
        end = start + relativedelta(hours=int(duration[0]))
        seconds = (end - start).total_seconds() + 60
        step = timedelta(minutes=1)
        datetimes = []
        for i in range(0, int(seconds), int(step.total_seconds())):
            datetimes.append(start + timedelta(seconds=i))       
        
        # Find accumulation and rate
        accum,rate=calc_rainfall_curves(method,total_mm_accum,total_duration_minutes,N_subpeaks,subpeak_duration_minutes)
        # Make rate same length as accumulation 
        rate = np.insert(rate, 0, 0, axis=0)
        # Create as dataframe
        accum_df = pd.DataFrame({'Dates': datetimes,  'Accumulation': accum, 
                                 'Rate (mm/hr)': rate, 'Rate (mm/min)': rate/60})
        # Keep only columns needed for feeding to ReFH2
        accum_df = accum_df[['Dates','Rate (mm/min)']]
        
        # Write to csv
        #accum_df.to_csv("CatchmentAnalysis/CreateSyntheticRainfalLEvents/LinDyke_DataAndFigs/SyntheticEvents_preLossRemoval/{}/{}_{}.csv".format(duration,duration, method),
         #               header = False, index = False)
        
        # Plot
        #pdf_plotter_all_rates()
        
        print(accum_df['Rate (mm/min)'].max())
        
## Antecedent conditions
dates = []
for i in[3,2,1]:
    print(i)
    dates.append(accum_df['Dates'][0] - timedelta(days=i))

antecedent_rainfall = pd.DataFrame({'Date': dates, "rainfall":0.51})
# antecedent_rainfall.to_csv("LinDyke_DataAndFigs/lindyke_daily_antecedent_conditions.csv", index = False)   

#############################################################################
#############################################################################
# Plot
#############################################################################
#############################################################################
# Plot for each method
for method in methods:
    pdf_plotter_rate(method)

# Plot
pdf_plotter_all_rates()

    
# Plot
pdf_plotter()





