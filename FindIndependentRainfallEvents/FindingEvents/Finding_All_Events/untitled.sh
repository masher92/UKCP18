#!/bin/bash

# Define the total number of gauges and the batch size
total_gauges=900
batch_size=20
start_gauge=0 # Starting gauge number
em="bb198" # Define or pass this variable

# Function to check if the output file exists for a gauge
output_file_exists() {
    gauge=$1
    output_file="../../../datadir/Gauge_Timeslices/2060_2081/${em}/gauge${gauge}_farFuture.nc"
    
    if [ -f "$output_file" ]; then
        return 0 # File exists
    else
        return 1 # File doesn't exist
    fi
}

# Function to run the script in a screen session and kill the session once it's done
run_script() {
    gauge=$1
    session_name="gauge_$gauge"
    output_file="../../../datadir/Gauge_Timeslices/2060_2081/${em}/gauge${gauge}_farFuture.nc"
    
    # Ensure the directory exists before running the script
    output_dir=$(dirname "$output_file")
    if [ ! -d "$output_dir" ]; then
        mkdir -p "$output_dir" # Create the directory if it doesn't exist
    fi

    echo "Starting gauge $gauge..."
    # Start the screen session in detached mode, and kill the session after the script finishes
    screen -dmS "$session_name" bash -c "python3 untitled.py $gauge > $output_file; screen -S $session_name -X quit"
}

# Create a list of gauges that need to be processed (missing output files)
missing_gauges=()

for (( gauge=start_gauge; gauge<=total_gauges; gauge++ )); do
    if output_file_exists $gauge; then
        echo "Gauge $gauge is already complete. Skipping."
    else
        missing_gauges+=($gauge)
    fi
done

# Now process the missing gauges in batches
total_missing_gauges=${#missing_gauges[@]}

if [ $total_missing_gauges -eq 0 ]; then
    echo "No missing output files. All gauges have been processed."
    exit 0
fi

echo "Processing ${total_missing_gauges} missing gauges..."

# Process the missing gauges in batches
for (( i=0; i<total_missing_gauges; i++ )); do
    gauge=${missing_gauges[$i]}

    # Start a new screen session for each gauge
    run_script $gauge

    # Check if we have reached the batch size
    if (( (i+1) % batch_size == 0 )); then
        echo "Waiting for batch to finish..."

        # Wait for all screen sessions in the current batch to finish
        while screen -list | grep -q "gauge_"; do
            sleep 5  # Check every 5 seconds if any screens are still running
        done

        echo "Batch finished. Starting next batch..."
    fi
done

# Final wait for any remaining screens (if not a perfect multiple of batch size)
echo "Waiting for final batch to finish..."
while screen -list | grep -q "gauge_"; do
    sleep 5
done

echo "All gauge scripts completed."
