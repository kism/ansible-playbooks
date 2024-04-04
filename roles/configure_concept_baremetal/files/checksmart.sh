#!/bin/bash

# Run smartctl --scan and store the output in a variable
scan_output=$(sudo smartctl --scan)

# Initialize an empty array to store device paths
device_paths=()

# Iterate over each line of the scan output
while IFS= read -r line; do
    # Extract the device path from the line
    device_path=$(echo "$line" | awk '{print $1}')
    # Add the device path to the array
    device_paths+=("$device_path")
done <<< "$scan_output"


for device in "${device_paths[@]}"; do
    echo "--------------------------------------"
    echo "${device}"
    smartctl ${device} -a | grep "SMART overall-health self-assessment test result"
    smartctl --attributes ${device}|grep -E "^ 12|^193"
done


