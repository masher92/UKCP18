eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa_jasmin

em_code=$1
echo $em_code

# Ensure the directory exists, or create it if it doesn't
mkdir -p /nfs/a319/gy17m2a/PhD/datadir/UKCP18_first30mins/2060_2081/${em_code}/

for year in {2061..2080}
do
    echo "Checking files for year: $year"
    for month in 01 02 03 04 05 06 07 08 09 10 11 12
    do
        for day in $(seq -w 01 30)
        do
            # Construct the filename pattern
            file_pattern="${em_code}a.pr${year}${month}${day}*"
            
            # Destination directory
            dest_dir="/nfs/a319/gy17m2a/PhD/datadir/UKCP18_first30mins/2060_2081/${em_code}/"
            
            # Check if the file already exists at the destination
            file_exists=false
            for file in ${dest_dir}${file_pattern}; do
                if [ -e "$file" ]; then
                    file_exists=true
                    break
                fi
            done
            
            if $file_exists; then
                echo "File for ${year}-${month}-${day} exists, skipping download."
            else
                echo "File for ${year}-${month}-${day} is missing, starting download..."
                scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/masher/${em_code}/${file_pattern} ${dest_dir}
            fi
        done
    done
done





# for year in {2061..2080}
# do
#     echo "output: $year"
#     for month in 01 02 03 04 05 06 07 08 09 10 11 12
#     do
#         # Construct the filename pattern
#         file_pattern="${em_code}a.pr${year}${month}*"
        
#         # Destination directory
#         dest_dir="/nfs/a319/gy17m2a/PhD/datadir/UKCP18_first30mins/2060_2081/${em_code}/"
#         echo $dest_dir
        
#         # Check if the file already exists at the destination
#         file_exists=false
#         for file in ${dest_dir}${file_pattern}; do
#             if [ -e "$file" ]; then
#                 file_exists=true
#                 break
#             fi
#         done
        
#         if $file_exists; then
#             echo "File for ${year} month ${month} already exists, skipping..."
#         else
#             echo "Copying file for ${year} month ${month}..."
#             scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/masher/${em_code}/${file_pattern} ${dest_dir}
#         fi
#     done
# done
# scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/masher/bc013/bc013a.pr20200402.pp "/nfs/a319/gy17m2a/PhD/datadir/UKCP18_first30mins/2002_2020/bc013/"


# Ensure the directory exists, or create it if it doesn't
# mkdir -p /nfs/a319/gy17m2a/PhD/datadir/UKCP18_first30mins/2002_2020/${em_code}/

# for year in {2000..2021}
# do
#     echo "output: $year"
#     for month in 01 02 03 04 05 06 07 08 09 10 11 12
#     do
#         # Construct the filename pattern
#         file_pattern="${em_code}a.pr${year}${month}*"
        
#         # Destination directory
#         dest_dir="/nfs/a319/gy17m2a/PhD/datadir/UKCP18_first30mins/2002_2020/${em_code}/"
        
#         # Check if the file already exists at the destination
#         if ls ${dest_dir}${file_pattern} 1> /dev/null 2>&1; then
#             echo "File for ${year} month ${month} already exists, skipping..."
#         else
#             echo "Attempting to copy file for ${year} month ${month}..."
#             # Use timeout command to limit each scp command to 120 seconds
#             if timeout 120 scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/masher/${em_code}/${file_pattern} ${dest_dir}; then
#                 echo "File successfully copied."
#             else
#                 echo "File copy timed out or failed for ${year} month ${month}, skipping..."
#             fi
#         fi
#     done
# done


# for day in {01..03}
# do
#     echo "output: $day"

#     # Construct the filename pattern
#     file_pattern="bc015a.pr201303${day}.pp"

#     # Destination directory
#     dest_dir="/nfs/a319/gy17m2a/PhD/datadir/UKCP18_first30mins/2002_2020/${em_code}/"

#     # Check if the file already exists at the destination
#     if ls ${dest_dir}${file_pattern} 1> /dev/null 2>&1; then
#         echo "File for ${year} month ${month} already exists, skipping..."
#     else
#         echo "Attempting to copy file for ${year} month ${month}..."
#         # Use timeout command to limit each scp command to 120 seconds
#         if timeout 120 scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/masher/${em_code}/${file_pattern} ${dest_dir}; then
#             echo "File successfully copied."
#         else
#             echo "File copy timed out or failed for ${year} month ${month}, skipping..."
#         fi
#     fi
# done

