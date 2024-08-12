#!/bin/bash
start_year=2061
end_year=2080
start_gauge=0
end_gauge=1293

# Define the batch size
batch_size=10

# Define the centralized log file
log_file="/nfs/a319/gy17m2a/PhD/logs/centralized_log_new.log"
touch "$log_file"  # Create the log file if it doesn't exist

# Define the base directory for file checks
base_dir="/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/UKCP18_30mins/bb189/"

# Define the output file for missing combinations
missing_combinations_file="/nfs/a319/gy17m2a/PhD/logs/missing_combinations.log"
> "$missing_combinations_file"  # Create or clear the log file if it exists

# Array to store missing combinations
missing_combinations=()

# Function to check if any screens are still running
check_screens() {
    local running_screens
    running_screens=$(screen -ls | grep -c 'Detached')
    echo "$running_screens"
}

# Function to wait for all screens to finish
wait_for_screens() {
    echo "Waiting for screens to finish..." | tee -a $log_file
    while [ "$(check_screens)" -gt 0 ]; do
        sleep 10  # Wait 10 seconds before checking again
    done
    echo "All screens have finished." | tee -a $log_file
}

excluded_gauges=(423 444 888 827)

# Function to check if a gauge is in the excluded list
is_excluded() {
    local gauge=$1
    for excluded_gauge in "${excluded_gauges[@]}"; do
        if [ "$gauge" -eq "$excluded_gauge" ]; then
            return 0  # Gauge is excluded
        fi
    done
    return 1  # Gauge is not excluded
}



# Main processing loop to find missing combinations
for year in $(seq $start_year $end_year); do
    echo "Checking files for year: $year"
    
    for gauge in $(seq $start_gauge $end_gauge); do
        if is_excluded $gauge; then
            echo "Skipping excluded gauge: $gauge"
            continue
        fi
        
        for duration in 0.5 1 2 3 6 12 24; do
            file_path="${base_dir}/${gauge}/WholeYear/${duration}hrs_${year}_v2_part0.csv"
            if [ ! -f "$file_path" ]; then
                # echo "$file_path does not exist" | tee -a $log_file
                missing_combinations+=("$year $gauge")  # Store the missing combination
                break  # No need to check further if any file is missing
            fi
        done
    done
done
# Write missing combinations to the log file
for combination in "${missing_combinations[@]}"; do
    echo "$combination" >> "$missing_combinations_file"
    echo $combination
done

# echo "missing combinations: "$missing_combinations

# Process the missing combinations in batches
num_combinations=${#missing_combinations[@]}

for (( i=0; i<$num_combinations; i+=batch_size )); do
    # Create a batch of missing combinations
    batch=("${missing_combinations[@]:i:batch_size}")
    
    # Print batch details
    echo -n "Processing batch: "
    printf "%s " "${batch[@]}" | tee -a $log_file
    echo  # Ensure a newline after the batch details
    
    # Create a screen session for each combination in the batch
    for combination in "${batch[@]}"; do
        year=$(echo $combination | cut -d' ' -f1)
        gauge=$(echo $combination | cut -d' ' -f2)
        
        # Shorten the session name if needed
        session_name="y${year}_g${gauge}"
        
        # Print message indicating screen start
        echo "Starting screen for year $year and gauge $gauge" | tee -a $log_file
        
        # Create a new screen session for each combination
        screen -dmS "$session_name" bash -c "(
            echo '=== Running python script for year $year and gauge $gauge ===' | tee -a $log_file
            python untitled_30mins.py $year $gauge 2>&1 | tee -a $log_file
            if [ \$? -eq 0 ]; then
                echo '=== Python script completed successfully for year $year and gauge $gauge ===' | tee -a $log_file
                            else
                echo '=== Python script failed for year $year and gauge $gauge ===' | tee -a $log_file
            fi
            exit
        )"
    done
    
    # Wait for the current batch to finish
    wait_for_screens
done

echo "All jobs have been processed." | tee -a $log_file
