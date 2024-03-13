"""

This module contains functions to operate data.

"""
import pandas as pd
import re


def process_tasmax(models_data, variable_name, season, season_name, threshold, ssp, years):
    """
    This function processes the data for the variable tasmax.

    Args:
    models_data (pd.DataFrame): the data to process
    variable_name (str): the name of the variable to process
    season (str): the season to consider
    season_name (str): the name of the season
    threshold (float): the threshold to consider
    ssp (str): the ssp to consider
    years (list): the years to consider 

    Returns:
    dict: the dictionnary of models with their annual count of days above the threshold
    """
    nb_days_over_threshold = {}

    for model, model_values in models_data.items():
        data = model_values["data"]
        period_data = data[data["season"] == season].groupby("year")
        nb_days_over_threshold[model] = list(period_data.apply(lambda x: len(x[x[variable_name] > threshold])))

    result = {
        "title": f"Nombre de jours au-dessus du seuil de {threshold}°C pour la saison {season_name} et le SSP{re.sub('ssp', '', ssp)}",
        "xlabel": "Année",
        "ylabel": "Nombre de jours",
        "data": nb_days_over_threshold,
        "x_values": years,
    }

    return result