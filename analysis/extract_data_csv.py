"""

This module aims to extract data from .nc files and save them in .csv files.

"""

import os
import re
import xarray as xr
import numpy as np
import argparse
from tqdm import tqdm

### Definition of constants
# Paths
DATA_FOLDER_PREFIX = "./data/raw/local/"
RESULTS_FOLDER_PREFIX = "./data/csv/models/"


### Definition of functions
def find_recursievely_nc_files(folder):
    """
    This function finds the .nc files in a folder and its subfolders.

    Args:
    folder (str): the folder to search

    Returns:
    list: the list of .nc files
    """
    nc_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".nc"):
                nc_files.append(os.path.join(root, file))
    return nc_files

def operation_on_data(data, variable_name):
    """
    This function returns the operation to apply on data according to
    their name
    """
    if "tas" in variable_name:
        return round(data - 273.15, 3)
    if variable_name == "pr":
        # Conversion des kg.m-2.s-1 en mm/m-2/j
        return round(data * 3600 * 24, 3)
    return data


def extract_nc_files_to_csv(source_folder):
    """
    This function extracts the data from .nc files and save them in .csv files.

    Args:
    source_folder (str): the folder containing the .nc files
    destination_folder (str): the folder to save the .csv files
    historical (bool): a boolean to tell wether data are historical or not

    Returns:
    None
    """
    # List the .nc files
    nc_files = find_recursievely_nc_files(source_folder)

    print(f"Extracting data from {source_folder}...")
    print(f"Found {len(nc_files)} .nc files.")

    # Extract the data from the .nc files
    for i in tqdm(range(len(nc_files))):
        # Open the .nc file
        nc_file = nc_files[i]
        data = xr.open_dataset(nc_file)

        # Name of the file
        filename = nc_file.split("/")[-1].split(".nc")[0]

        # Get the variable name
        variable_name = re.search(r'(.*?)_', filename).group(1)

        # Get the ssp or historical
        if "historical" in filename:
            ssp = "historical"
        else:
            ssp = "ssp" + re.search(r'ssp(.+?)_', filename).group(1)
        
        # Get the period of the data
        period = re.search(f'{variable_name}_(.+?)_', filename).group(1)

        # Get the destination folder
        relative_path = f"{variable_name}_{period}/CMIP6/{ssp}/"
        relative_destination_path = RESULTS_FOLDER_PREFIX + relative_path

        # Create the destination folder if it does not exist
        if not os.path.exists(relative_destination_path):
            os.makedirs(relative_destination_path)
        
        ### Process dataframe
        df = data.to_dataframe()

        # Change the index to a single column containing the date YYYY-MM-DD
        df.reset_index(inplace=True)
        df["time"] = df["time"].astype(str)
        df["time"] = df['time'].str.extract(r'(\d{4}-\d{2}-\d{2})')
        df.set_index("time", inplace=True)

        # Remove irrelevant columns
        df.drop(columns=[col for col in df.columns if col not in ["time", variable_name]], inplace=True)
        df[variable_name] = df[variable_name]

        # Apply the operation on the data
        df[variable_name] = operation_on_data(df[variable_name], variable_name)

        # Drop duplicates
        df = df[~df.index.duplicated(keep='first')]

        # Save the .csv file
        df.to_csv(f"{relative_destination_path}{filename}.csv")

        # Close the .nc file
        data.close()


### Main
if __name__ == '__main__':
    # Parse the arguments
    parser = argparse.ArgumentParser(prefix_chars="-", description="Extract data from .nc files and save them in .csv files.")
    parser.add_argument("--source_folder", type=str,default=DATA_FOLDER_PREFIX, help="The folder containing the .nc files")
    args = parser.parse_args().__dict__
    extract_nc_files_to_csv(**args)