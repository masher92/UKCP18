import iris
import glob
import iris.plot as iplt
import iris.quickplot as qplt
import datetime as datetime
import iris.coord_categorisation as cat
import sys
import numpy as np

# Get year from input of running the script 
# year = sys.argv[1]
# print (year)
years = [2009]

for year in years:
    print(year)
    ### Get list of files to convert
    radardir = f'/nfs/a319/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/'
    file_list=glob.glob(radardir +"*.nc")
    sorted_list = sorted(file_list)
    
    for i in range(0,len(sorted_list)):
        print(i)
        ### Load radar data for one day (using IRIS)
        day_cube = iris.load_cube(sorted_list[i])

        ### Add additional time based variables
        # cat.add_year(day_cube, 'time', name='year')
        # cat.add_month(day_cube, 'time', name='month')
        # cat.add_day_of_month(day_cube, 'time', name='day_of_month')
        cat.add_hour(day_cube, 'time', name='hour')
        # cat.add_day(day_cube, 'time', name='day')

        ### Aggregate to half hourly values (means)
        firsthalfof_hour_constraint = iris.Constraint(time=lambda cell: cell.point.minute <30)
        secondhalfof_hour_constraint = iris.Constraint(time=lambda cell: cell.point.minute >=30)

        # Create empty cube list to populate
        my_cube_list = iris.cube.CubeList()

        # Get list of the hours
        hours = set(day_cube.coord('hour').points)
        # Loop through the hours
        for hour in hours:

            # Establish constraint to select only this hour
            hour_constraint = iris.Constraint(time=lambda cell: cell.point.hour == hour)
            # Use constraint to select only this hour
            hour_cube = day_cube.extract(hour_constraint)
            # Check the times
            # times = hour_cube.coord('time').points
            # times = [datetime.datetime.fromtimestamp(x ) for x in times]

            # Get only cubes which fall within the first half of the hour and then the second half of the hour
            first_half_of_hour = hour_cube.extract(firsthalfof_hour_constraint)
            second_half_of_hour = hour_cube.extract(secondhalfof_hour_constraint)

            # If there are at least 4 values
            # Find the mean across first/second halves of hour
            # Add to cube list
            if first_half_of_hour == None:
                print("no values in 1st half hour")
            elif len(first_half_of_hour.shape) ==2:
                print("only 1 value in 1st half hour")        
            else:
                
                if first_half_of_hour.shape[0] >=4:
                    ## Correct negative 1064 values to np.nan
                    if np.nanmin(first_half_of_hour.data)<0:
                        print(f"iter {i}, hour {hour}, first half hour, min value is: {np.nanmin(first_half_of_hour.data)}")
                        first_half_of_hour.data = np.where(first_half_of_hour.data <0, np.nan, first_half_of_hour.data)
                        print(f"min value is: {np.nanmin(first_half_of_hour.data)}")
                        if np.nanmin(first_half_of_hour.data <0):
                            print(first_half_of_hour.data[first_half_of_hour.data<0])
                    # FIND MEAN ACROSS WHOLE FIRST HALF HOUR
                    first_half_hourly_mean = first_half_of_hour.aggregated_by(['hour'],iris.analysis.MEAN)
                    # first_half_hourly_mean.data.astype('float64')
                    my_cube_list.append(first_half_hourly_mean)
                else:
                    print(f"only {first_half_of_hour.shape[0]} vals in 1st half hour")

            ### SECOND HALF HOUR    
            if second_half_of_hour == None:
                print("no values in 2nd half hour")
            elif len(second_half_of_hour.shape) ==2:
                print("only 1 value in 2nd half hour")
            else:
                if second_half_of_hour.shape[0] >=4:    
                    ## Correct negative 1064 values to np.nan
                    if np.nanmin(second_half_of_hour.data)<0:            
                        print(f"iter {i}, hour {hour}, second half hour, min value is: {np.nanmin(second_half_of_hour.data)}")
                        second_half_of_hour.data = np.where(second_half_of_hour.data <0, np.nan, second_half_of_hour.data)
                        print(f"min value is: {np.nanmin(second_half_of_hour.data)}")
                        if np.nanmin(second_half_of_hour.data <0):
                            print(second_half_of_hour.data[second_half_of_hour.data<0])
                    # FIND MEAN ACROSS WHOLE FIRST HALF HOUR
                    second_half_hourly_mean = second_half_of_hour.aggregated_by(['hour'],iris.analysis.MEAN)
                    # second_half_hourly_mean.data.astype('float64')
                    my_cube_list.append(second_half_hourly_mean)
                else:
                    print(f"only {second_half_of_hour.shape[0]} vals in 2nd half hour")


        ### Join back into one cube covering the whole day
        try:
            for halfhour_i in range(0,len(my_cube_list)):
                my_cube_list[halfhour_i].data = my_cube_list[halfhour_i].data.astype('float64')

            thirty_mins_means = my_cube_list.concatenate_cube()

            # Get rid of high values which are fill values
            thirty_mins_means.data = np.where(thirty_mins_means.data >1e+36, np.nan, thirty_mins_means.data)

            # save 
            new_fp = sorted_list[i][:-3]+ '_30mins.nc'
            new_fp = new_fp.replace('5mins', '30mins')
            iris.save(thirty_mins_means, new_fp)
            print(f'Saved cube {year} {i}')
            print(np.nanmin(thirty_mins_means.data))
            print(np.nanmax(thirty_mins_means.data))
            print(np.nanmean(thirty_mins_means.data))

        except:
            pass