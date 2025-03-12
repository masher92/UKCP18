#!/bin/bash
echo "helloe"
# Output CSV file
output_file="/nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/missing_files_summary.csv"

# Define the expected number of days in each month
declare -A days_in_month=( 
    ["01"]=31 ["02"]=29 ["03"]=31 ["04"]=30 
    ["05"]=31 ["06"]=30 ["07"]=31 ["08"]=31 
    ["09"]=30 ["10"]=31 ["11"]=30 ["12"]=31 
)

# Function to check if a year is a leap year
is_leap_year() {
    local year=$1
    if (( year % 4 == 0 && year % 100 != 0 )) || (( year % 400 == 0 )); then
        return 0
    else
        return 1
    fi
}

# Write CSV header
echo "Year,Month,Expected Files,Actual Files,Missing Files" > "$output_file"

# Loop through years 2006 to 2019
for year in {2006..2019}; do
    echo "Processing Year: $year"

    # Adjust February for leap years
    if is_leap_year "$year"; then
        days_in_month["02"]=29
    else
        days_in_month["02"]=28
    fi

    # Change to the appropriate directory
    target_directory="/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/"
    if ! cd "$target_directory"; then
        echo "Warning: Failed to change directory to $target_directory"
        continue
    fi

    # Iterate over each month
    for month in "${!days_in_month[@]}"; do
        pattern="metoffice-c-band-rain-radar_uk_${year}${month}*.nc"
        expected_count=${days_in_month[$month]}

        # Count actual files
        actual_count=$(ls $pattern 2>/dev/null | wc -l)
        missing_count=$((expected_count - actual_count))

        # Append results to CSV
        echo "$year,$month,$expected_count,$actual_count,$missing_count" >> "$output_file"

        # Print status
        echo "Year: $year, Month: $month, Expected: $expected_count, Actual: $actual_count, Missing: $missing_count"
    done

    echo "--------------------------------------"
done

echo "Summary saved to $output_file"



# year=$1
# echo "Year: $year"

# # Change to the specified directory
# target_directory="/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/"
# echo "Changing directory to: $target_directory"
# cd "$target_directory" || { echo "Failed to change directory to $target_directory"; exit 1; }

# #!/bin/bash

# # Define the expected number of days in each month
# declare -A days_in_month=( 
#     ["01"]=31 ["02"]=29 ["03"]=31 ["04"]=30 
#     ["05"]=31 ["06"]=30 ["07"]=31 ["08"]=31 
#     ["09"]=30 ["10"]=31 ["11"]=30 ["12"]=31 
# )

# # Function to check leap year
# is_leap_year() {
#     year=$1
#     if (( year % 4 == 0 && year % 100 != 0 )) || (( year % 400 == 0 )); then
#         return 0
#     else
#         return 1
#     fi
# }

# # Main script
# year=$1
# echo "Checking files for the year: $year"

# # Adjust February for leap years
# if is_leap_year $year; then
#     days_in_month["02"]=29
# else
#     days_in_month["02"]=28
# fi

# # Iterate over each month
# for month in "${!days_in_month[@]}"; do
#     pattern="metoffice-c-band-rain-radar_uk_${year}${month}*.nc"
#     expected_count=${days_in_month[$month]}

#     echo "Checking month: $year-$month"
#     echo "Expected number of files: $expected_count"

#     actual_count=$(ls $pattern 2>/dev/null | wc -l)
#     echo "Actual number of files: $actual_count"

#     if [ $actual_count -ne $expected_count ]; then
#         echo "Discrepancy found in $year-$month: Expected $expected_count files, found $actual_count files."
#     else
#         echo "All files present for $year-$month."
#     fi

#     echo "-----------------------------"
# done



# cd /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/