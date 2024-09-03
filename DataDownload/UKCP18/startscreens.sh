#!/bin/bash
start_year=2079
end_year=2080
em_code=$1

# Start SSH agent and add the private key
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa_jasmin

# Test SSH connection to ensure authentication is successful before proceeding
ssh -q -o BatchMode=yes masher92@xfer1.jasmin.ac.uk "exit"
if [ $? -ne 0 ]; then
    echo "SSH authentication failed. Please check your credentials or SSH setup."
    exit 1
fi

# Define the batch size
batch_size=5

# Define the centralized log file
log_file="/nfs/a319/gy17m2a/PhD/logs/centralized_log_download.log"
touch "$log_file"  # Create the log file if it doesn't exist

echo "Ensemble Member Code: $em_code"

# Define the base directory for file checks
base_dir="/nfs/a319/gy17m2a/PhD/datadir/UKCP18_first30mins/2060_2081/$em_code"
echo "Base Directory: $base_dir"
mkdir -p "$base_dir"

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

# Main processing loop to find missing files
for year in $(seq $start_year $end_year); do
    echo "Checking files for year: $year"
    
    for month in 01 02 03 04 05 06 07 08 09 10 11 12; do
        for day in $(seq -w 01 30); do
            # Construct the filename pattern
            file_pattern="${em_code}a.pr${year}${month}${day}*"
            file_path="${base_dir}/${file_pattern}"
            
            if [ ! -e $file_path ]; then
                echo "$file_path does not exist" | tee -a $log_file
                missing_combinations+=("$year $month $day")  # Store the missing combination
            else
                echo "File for ${year}-${month}-${day} exists, skipping download." | tee -a $log_file
            fi
        done
    done
done

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
        month=$(echo $combination | cut -d' ' -f2)
        day=$(echo $combination | cut -d' ' -f3)
        
        # Shorten the session name if needed
        session_name="y${year}_m${month}_d${day}"
        
        # Print message indicating screen start
        echo "Starting screen for year $year, month $month, day $day" | tee -a $log_file
        
        # Create a new screen session for each combination
        screen -dmS "$session_name" bash -c "(
            echo 'SSH_AUTH_SOCK is set to: $SSH_AUTH_SOCK' | tee -a $log_file
            echo '=== Downloading files for $year-$month-$day ===' | tee -a $log_file
            rsync -avzh --progress masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/masher/${em_code}/${em_code}a.pr${year}${month}${day}* $base_dir 2>&1 | tee -a $log_file
            if [ \$? -eq 0 ]; then
                echo '=== Download completed successfully for $year-$month-$day ===' | tee -a $log_file
            else
                echo '=== Download failed for $year-$month-$day ===' | tee -a $log_file
            fi
            exit
        )"
    done
    
    # Wait for the current batch to finish
    wait_for_screens
done

echo "All jobs have been processed." | tee -a $log_file