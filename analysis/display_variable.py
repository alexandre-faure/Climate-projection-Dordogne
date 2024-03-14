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
from data_operations import process_tasmax, process_tas, process_pr

### Definition of constants
# Paths
DATA_FODER_PREFIX = "./data/csv/"
RESULTS_FOLDER_PREFIX = "./results/"

# Analysis
VARIABLE_NAME_OPERATIONS_CORRESPONDANCE = {
    "tasmax": process_tasmax,
    "tas": process_tas,
    "pr": process_pr
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
    "historical_start": 1950,
    "historical_end": 2014,
    "model_start": 2015,
    "model_end": 2099
}
REF_YEARS = [1980, 2009]
PROJECTION_YEARS = [2070, 2099]

# Style
COLORS = {
     "blue": (0.5, 0.6, 0.9),
     "light_blue": (0.75, 0.85, 1),
     "red": (1, 0.2, 0.2),
}






### Definition of functions
def plot_graphics(result, variable, ssp, season):
    print(f"\t\t-> Plotting {result['short_title']}...")
    # Plot the data
    plt.figure(figsize=(10, 5))
    plt.title(result["title"])
    plt.xlabel(result["xlabel"])
    plt.ylabel(result["ylabel"])
    
    deciles = np.percentile(list(result["data"].values()), [10, 90], axis=0)
    plt.fill_between(result["x_values"], deciles[0], deciles[1], color=COLORS["light_blue"], label="Déciles 1-9") 

    for model, values in result["data"].items():
            plt.plot(result["x_values"], values, color=COLORS["blue"], lw=1, alpha=0.6) 

    # On affiche les contours des déciles en tirets noirs
    plt.plot(result["x_values"], deciles[0], color="black", lw=1, linestyle="--", alpha=0.6)
    plt.plot(result["x_values"], deciles[1], color="black", lw=1, linestyle="--", alpha=0.6)

    # Ligne de référence
    if "drawRefLine" in result["misc"]:
        plt.axhline(y=result["misc"]["drawRefLine"], color="black", lw=1, linestyle="--", alpha=0.7)
    
    # Médiane entre les modèles
    median = np.median(list(result["data"].values()), axis=0)
    plt.plot(result["x_values"], median, color=COLORS["red"], lw=2, label="Médiane entre les modèles")
    
    # Limites du graphique
    plt.xlim(REF_YEARS[0], PROJECTION_YEARS[1]+1)
    if "yMin" in result["misc"]:
        plt.ylim(result["misc"]["yMin"], plt.gca().get_ylim()[1])

    
    # On affiche un trait vertical vert pour signifier l'année 2024 (actuelle)
    plt.axvline(x=2024, color="black", lw=2)
    # On affiche la légende de l'année actuelle
    if "yearTextPosition" in result["misc"] and result["misc"]["yearTextPosition"] == "top":
        plt.text(2024, plt.gca().get_ylim()[1] - 0.05 * (plt.gca().get_ylim()[1] - plt.gca().get_ylim()[0]),
                 "Année 2024", ha="center", va="center", color="black", bbox=dict(facecolor='white', alpha=0.9))
    else:
        plt.text(2024, plt.gca().get_ylim()[0] + 0.05 * (plt.gca().get_ylim()[1] - plt.gca().get_ylim()[0]),
                 "Année 2024", ha="center", va="center", color="black", bbox=dict(facecolor='white', alpha=0.9))
    
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)

    # On créé le dossier de sauvegarde si il n'existe pas
    if not os.path.exists(f"{RESULTS_FOLDER_PREFIX}plots/{variable}/{ssp}"):
        os.makedirs(f"{RESULTS_FOLDER_PREFIX}plots/{variable}/{ssp}")

    # On sauvegarde le graphique
    plt.savefig(f"{RESULTS_FOLDER_PREFIX}plots/{variable}/{ssp}/{result['short_title']}_{season}.png")


def display_variable(variable, ssp, season, threshold):
    # Define the variable names
    variable_period = "day"
    list_variable = variable
    list_ssp = ssp
    list_season = season
    list_threshold = threshold

    for variable in list_variable:
        for ssp in list_ssp:
            print(f"Processing {variable} for {ssp}...")

            # Load the predictions data
            data_folder = DATA_FODER_PREFIX + "models/" + variable+"_"+variable_period+"/CMIP6/"+ssp+"_ba"
            models_data = dict()
            for filename in os.listdir(data_folder):
                if filename.endswith(".csv"):
                    model = re.search(variable_period+'_(.+?)_ssp', filename).group(1)
                    models_data[model] = dict()
                    models_data[model]["data"] = pd.read_csv(data_folder+"/"+filename, index_col=0)

            # Load the prediction of the historical period
            data_folder = DATA_FODER_PREFIX + "models/" + variable+"_"+variable_period+"/CMIP6/historical_ba"
            for filename in os.listdir(data_folder):
                if filename.endswith(".csv"):
                    model = re.search(variable_period+'_(.+?)_historical', filename).group(1)
                    if model in models_data:
                        models_data[model]["data"] = pd.concat([models_data[model]["data"], pd.read_csv(data_folder+"/"+filename, index_col=0)])
            
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

                
                list_result = VARIABLE_NAME_OPERATIONS_CORRESPONDANCE[variable](models_data, variable, season,
                                                                        SEASONS_NAMES_CORRESPONDANCE[season], threshold, ssp,
                                                                        np.arange(YEARS["historical_start"], YEARS["model_end"]+1),
                                                                        REF_YEARS, PROJECTION_YEARS)
                for result in list_result:
                    plot_graphics(result, variable, ssp, season)







### Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prefix_chars="-", description='Analyse a variable')
    parser.add_argument('-v', '--variable', type=str, nargs='+', default=['tasmax', 'tas', 'pr'], help='Variable name')
    parser.add_argument('-S', '--ssp', type=str, nargs='+', default=['ssp245', 'ssp585'], help='SSP amongst ssp245, ssp585')
    parser.add_argument('-s', '--season', type=str, nargs='+', default=['DJF', 'JJA'], help='Season amongst DJF, MAM, JJA, SON')
    parser.add_argument('-t', '--threshold', type=float, nargs='+', default=[15, 35], help='Threshold for the variable')
    args = parser.parse_args().__dict__
    # Check if the variable is valid
    if any(variable not in VARIABLE_NAME_OPERATIONS_CORRESPONDANCE for variable in args["variable"]) :
        print(f"Variable {args['variable']} is not valid. Please choose amongst {VARIABLE_NAME_OPERATIONS_CORRESPONDANCE.keys()}")
        exit()
    if any(ssp not in SSP_NAMES for ssp in args["ssp"]):
        print(f"SSP {args['ssp']} is not valid. Please choose amongst {SSP_NAMES}")
        exit()
    if any(season not in SEASONS_SHORTNAMES for season in args["season"]):
        print(f"Season {args['season']} is not valid. Please choose amongst {SEASONS_SHORTNAMES}")
        exit()
    if len(args["season"]) != len(args["threshold"]):
        print("The number of season and threshold must be the same")
        exit()
    
    # Execute the function
    display_variable(**args)