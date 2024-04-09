# Loop through every .yml file in the folder
for file in *.yml; do
    # Run ansible-lint against the file and save output to a log file
    ansible-lint "$file" > "${file%.yml}.log" 2>&1
done