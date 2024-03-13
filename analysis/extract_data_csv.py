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

# Data
LATITUDE = 45.569816
LONGITUDE = 0.79367470


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
    if variable_name == "tasmax":
        return round(data - 273.15, 2)
    else:
        return data


def extract_nc_files_to_csv(source_folder, destination_folder, year_start_model):
    """
    This function extracts the data from .nc files and save them in .csv files.

    Args:
    source_folder (str): the folder containing the .nc files
    destination_folder (str): the folder to save the .csv files
    date_start_model (int): the year to consider as the start of the model period

    Returns:
    None
    """
    # List the .nc files
    nc_files = find_recursievely_nc_files(source_folder)

    # Extract the data from the .nc files
    for i in tqdm(range(len(nc_files))):
        # Open the .nc file
        nc_file = nc_files[i]
        data = xr.open_dataset(nc_file)

        # Miscellaneous information
        relative_path = nc_file.split(source_folder)[-1]
        relative_path = "/".join(relative_path.split("/")[0:-1]) + "/"
        filename = nc_file.split("/")[-1].split(".nc")[0]

        # Get the variable name
        variable_name = re.search(r'(.*?)_', filename).group(1)

        # Get the ssp
        ssp = re.search(r'ssp(.+?)_', filename).group(1)

        # Get the destination folder
        relative_destination_path = destination_folder + relative_path + "ssp" + ssp + "/"

        # Create the destination folder if it does not exist
        if not os.path.exists(destination_folder + relative_path.split("/")[0]):
            os.makedirs(destination_folder + relative_path.split("/")[0])
        if not os.path.exists(destination_folder + relative_path):
            os.makedirs(destination_folder + relative_path)
        if not os.path.exists(relative_destination_path):
            os.makedirs(relative_destination_path)
        if not os.path.exists(relative_destination_path + "predictions/"):
            os.makedirs(relative_destination_path + "predictions/")
        if not os.path.exists(relative_destination_path + "historical/"):
            os.makedirs(relative_destination_path + "historical/")
        
        ### Process dataframe
        df = data.to_dataframe()

        # Change the index to a single column containing the date YYYY-MM-DD
        df.reset_index(inplace=True)
        df["time"] = df["time"].astype(str)
        df["time"] = df['time'].str.extract(r'(\d{4}-\d{2}-\d{2})')
        df.set_index("time", inplace=True)

        # Remove irrelevant columns
        df.drop(columns=[col for col in df.columns if col not in ["time", variable_name]], inplace=True)
        df[variable_name] = df[variable_name].round(2)

        # Apply the operation on the data
        df[variable_name] = operation_on_data(df[variable_name], variable_name)

        # Drop duplicates
        df = df[~df.index.duplicated(keep='first')]

        # Save the .csv file
        df.to_csv(f"{relative_destination_path}predictions/{filename}.csv")

        # Handle historical data
        df = df[df.index.map(lambda x: int(x.split("-")[0]) < year_start_model)]
        df.to_csv(f"{relative_destination_path}historical/{filename}.csv")

        # Close the .nc file
        data.close()


### Main
if __name__ == '__main__':
    extract_nc_files_to_csv(DATA_FOLDER_PREFIX, RESULTS_FOLDER_PREFIX, 2023)