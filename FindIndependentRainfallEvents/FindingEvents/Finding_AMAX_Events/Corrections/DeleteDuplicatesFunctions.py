import os
import pandas as pd
import shutil


def create_copy_of_files(current_directory,  gauge_num):
    target_directory = current_directory + "/EventSet"

    # Create the directory if it does not exist
    os.makedirs(target_directory, exist_ok=True)

    # List all files in the current directory
    files = [f for f in os.listdir(current_directory) if os.path.isfile(os.path.join(current_directory, f))]

    # Copy each file to the target directory
    for file in files:
        source_path = os.path.join(current_directory, file)
        destination_path = os.path.join(target_directory, file)
        shutil.copy(source_path, destination_path)

    # print(f"All files have been copied to {target_directory}.")

def load_csv_files(directory):
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    dataframes = {}
    
    for csv_file in csv_files:
        file_path = os.path.join(directory, csv_file)
        df = pd.read_csv(file_path)
        if 'precipitation (mm)' in df.columns:
            dataframes[csv_file] = df['precipitation (mm)']
    
    return dataframes

def compare_and_delete_duplicates(dataframes, directory_path):
    filenames = list(dataframes.keys())
    num_files = len(filenames)
    duplicates = set()

    for i in range(num_files):
        for j in range(i + 1, num_files):
            file1, file2 = filenames[i], filenames[j]
            if dataframes[file1].equals(dataframes[file2]):
                duplicates.add(file2)  # Add the second file to the set of duplicates
                # print(f"The 'rolling_sum' column in {file1} is the same as in {file2}. Deleting {file2}.")

    # Delete the duplicate files
    for file in duplicates:
        os.remove(os.path.join(directory_path, file))
        # print(f"Deleted file: {file}")

def compare_columns(dataframes):
    filenames = list(dataframes.keys())
    num_files = len(filenames)
    
    for i in range(num_files):
        for j in range(i + 1, num_files):
            file1, file2 = filenames[i], filenames[j]
            if dataframes[file1].equals(dataframes[file2]):
                print(f"The 'rolling_sum' column in {file1} is the same as in {file2}")       