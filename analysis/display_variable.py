"""

This script is used to display a variable for a given SSP and season.
It can be executed with the following command:

python3 display_variable.py --variable tasmax --ssp ssp245 --season DJF

"""
import numpy as np
import pandas as pd
import cftime
import re
import os
import matplotlib.pyplot as plt
import argparse
from data_operations import process_tasmax

### Definition of constants
# Paths
DATA_FODER_PREFIX = "./data/csv/"
RESULTS_FOLDER_PREFIX = "./results/"

# Analysis
VARIABLE_NAME_OPERATIONS_CORRESPONDANCE = {
    "tasmax": process_tasmax
}
SSP_NAMES = ["ssp245", "ssp585"]
SEASONS_SHORTNAMES = ["DJF", "MAM", "JJA", "SON"]
SEASONS_NAMES_CORRESPONDANCE = {
    "DJF": "Déc-Jan-Fév",
    "MAM": "Mar-Avr-Mai",
    "JJA": "Juin-Juil-Août",
    "SON": "Sep-Oct-Nov"
}
SEASONS_MONTHS_CORRESPONDANCE = {
    "DJF": [12, 1, 2],
    "MAM": [3, 4, 5],
    "JJA": [6, 7, 8],
    "SON": [9, 10, 11]
}
YEARS = {
    "historical_start": 2015,
    "historical_end": 2022,
    "model_start": 2023,
    "model_end": 2070
}

# Style
COLORS = {
     "blue": (0.5, 0.6, 0.9),
     "light_blue": (0.75, 0.85, 1),
     "red": (1, 0.2, 0.2),
}






### Definition of functions
def display_variable(variable, ssp, season, threshold):
    # Define the variable names
    variable_ba = variable#+"_ba"
    variable_period = "day"
    list_ssp = ssp
    list_season = season
    list_threshold = threshold

    for ssp in list_ssp:
        print(f"Processing {variable} for {ssp}...")
        data_folder = DATA_FODER_PREFIX + "models/" + variable+"_"+variable_period+"/CMIP6/"+ssp+"/predictions"

        # Load the data
        models_data = dict()
        for filename in os.listdir(data_folder):
            if filename.endswith(".csv"):
                model = re.search(variable_period+'_(.+?)_ssp', filename).group(1)
                models_data[model] = dict()
                models_data[model]["data"] = pd.read_csv(data_folder+"/"+filename, index_col=0)
        
        for i in range(len(list_season)):
            print(f"\t-> Processing {SEASONS_NAMES_CORRESPONDANCE[list_season[i]]}...")
            season = list_season[i]
            threshold = list_threshold[i]
            # Operate the data
            for model, model_values in models_data.items():
                data = model_values["data"]
                # Add a season and year columns
                data["season"] = data.index.map(lambda x: [period for period, month in SEASONS_MONTHS_CORRESPONDANCE.items()
                                                        if int(x.split("-")[1]) in month][0])
                data["year"] = data.index.map(lambda x: int(x.split("-")[0]))

            
            result = VARIABLE_NAME_OPERATIONS_CORRESPONDANCE[variable](models_data, variable_ba, season,
                                                                    SEASONS_NAMES_CORRESPONDANCE[season], threshold, ssp,
                                                                    np.arange(YEARS["historical_start"], YEARS["model_end"]+1))

            # Plot the data
            plt.figure(figsize=(10, 5))
            plt.title(result["title"])
            plt.xlabel(result["xlabel"])
            plt.ylabel(result["ylabel"])

            deciles = np.percentile(list(result["data"].values()), [10, 90], axis=0)
            plt.fill_between(result["x_values"], deciles[0], deciles[1], color=COLORS["light_blue"], label="Déciles 1-9") 

            for model, values in result["data"].items():
                    plt.plot(result["x_values"], values, color=COLORS["blue"], lw=1, alpha=0.6)   
            
            median = np.median(list(result["data"].values()), axis=0)
            plt.plot(result["x_values"], median, color=COLORS["red"], lw=3, label="Médiane")
            
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.6)

            plt.savefig(f"{RESULTS_FOLDER_PREFIX}plots/{variable}_{ssp}_{season}.png")







### Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prefix_chars="-", description='Analyse a variable')
    parser.add_argument('-v', '--variable', type=str, default='tasmax', help='Variable name')
    parser.add_argument('-S', '--ssp', type=str, nargs='+', default=['ssp245', 'ssp585'], help='SSP amongst ssp245, ssp585')
    parser.add_argument('-s', '--season', type=str, nargs='+', default=['DJF', 'JJA'], help='Season amongst DJF, MAM, JJA, SON')
    parser.add_argument('-t', '--threshold', type=float, nargs='+', default=[15, 35], help='Threshold for the variable')
    args = parser.parse_args().__dict__
    # Check if the variable is valid
    if args["variable"] not in VARIABLE_NAME_OPERATIONS_CORRESPONDANCE:
        print(f"Variable {args['variable']} is not valid. Please choose amongst {VARIABLE_NAME_OPERATIONS_CORRESPONDANCE.keys()}")
        exit()
    if all(ssp not in SSP_NAMES for ssp in args["ssp"]):
        print(f"SSP {args['ssp']} is not valid. Please choose amongst {SSP_NAMES}")
        exit()
    if all(season not in SEASONS_SHORTNAMES for season in args["season"]):
        print(f"Season {args['season']} is not valid. Please choose amongst {SEASONS_SHORTNAMES}")
        exit()
    if len(args["season"]) != len(args["threshold"]):
        print("The number of season and threshold must be the same")
        exit()
    
    # Execute the function
    display_variable(**args)