"""

This module contains functions to operate data.

"""
import pandas as pd
import re
import numpy as np
from copy import deepcopy


def process_tasmax(models_data, variable_name, season, season_name, threshold, ssp, years, ref_years, projection_years):
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
    ref_years (list): the years extrema of the reference period
    projection_years (list): the years extrema of the projection period

    Returns:
    dict: the dictionnary of models with their annual count of days above the threshold
    """
    result = []
    nb_days_over_threshold = {}

    for model, model_values in models_data.items():
        data = model_values["data"]
        period_data = data[data["season"] == season].groupby("year")
        nb_days_over_threshold[model] = list(period_data.apply(lambda x: len(x[x[variable_name] > threshold])))

    result.append({
        "short_title": f"threshold-{threshold}°C",
        "title": f"Nombre de jours où la température maximale excède {threshold}°C pour la saison {season_name}\n"+
                    f"selon le SSP{re.sub('ssp', '', ssp)} sur la base de {len(models_data)} modèles",
        "xlabel": "Année",
        "ylabel": "Nombre de jours",
        "data": nb_days_over_threshold,
        "x_values": years,
        "misc":{
            "yearTextPosition": "top"
        }
    })

    return result

def process_tas(models_data, variable_name, season, season_name, threshold, ssp, years, ref_years, projection_years):
    """
    This function processes the data for the variable tas.

    Args:
    models_data (pd.DataFrame): the data to process
    variable_name (str): the name of the variable to process
    season (str): the season to consider
    season_name (str): the name of the season
    threshold (float): the threshold to consider
    ssp (str): the ssp to consider
    years (list): the years to consider 
    ref_years (list): the years extrema of the reference period
    projection_years (list): the years extrema of the projection period

    Returns:
    dict: the dictionnary of models with their annual mean temperature for the season
    """
    result = []

    mean_temperature = {}

    for model, model_values in models_data.items():
        data = model_values["data"]
        period_data = data[data["season"] == season].groupby("year")
        mean_temperature[model] = list(period_data.apply(lambda x: x[variable_name].mean()))
    
    # On calcule la moyenne de la médiane des températures entre les modèles
    # sur les années de la période de référence
    mean_ref = np.mean(
        np.median([mean_temperature[model][ref_years[0] - years[0]:ref_years[1] - years[0] + 1]
                   for model in mean_temperature], axis=1))
    
    result.append({
        "short_title": f"evolution-absolue",
        "title": f"Température moyenne pour la saison {season_name} selon le SSP{re.sub('ssp', '', ssp)}\n"+
                    f"sur la base de {len(models_data)} modèles",
        "xlabel": "Année",
        "ylabel": "Température moyenne (°C)",
        "data": deepcopy(mean_temperature),
        "x_values": years,
        "misc":{
            "drawRefLine":mean_ref
        }
    })

    # On soustrait la médiane de la température médiane sur la période de référence
    for model in mean_temperature:
        mean_temperature[model] = mean_temperature[model] - mean_ref

    result.append({
        "short_title": f"evolution-relative",
        "title": f"Variation de la température moyenne pour la saison {season_name} selon le SSP{re.sub('ssp', '', ssp)}\n"+
                    f"sur la base de {len(models_data)} modèles par rapport à la période {ref_years[0]}-{ref_years[1]}",
        "xlabel": "Année",
        "ylabel": "Variation de température (°C)",
        "data": mean_temperature,
        "x_values": years,
        "misc":{
            "drawRefLine":0,
        }
    })

    return result

def process_pr(models_data, variable_name, season, season_name, threshold, ssp, years, ref_years, projection_years):
    """
    This function processes the data for the variable pr.

    Args:
    models_data (pd.DataFrame): the data to process
    variable_name (str): the name of the variable to process
    season (str): the season to consider
    season_name (str): the name of the season
    threshold (float): the threshold to consider
    ssp (str): the ssp to consider
    years (list): the years to consider 
    ref_years (list): the years extrema of the reference period
    projection_years (list): the years extrema of the projection period

    Returns:
    dict: the dictionnary of models with their annual total precipitation for the season
    """
    result = []
    total_precipitation = {}

    for model, model_values in models_data.items():
        data = model_values["data"]
        period_data = data[data["season"] == season].groupby("year")
        total_precipitation[model] = list(period_data.apply(lambda x: x[variable_name].sum()))

    # On calcule la moyenne de la médiane des précipitations entre les modèles
    # sur les années de la période de référence
    mean_ref = np.mean(
        np.median([total_precipitation[model][ref_years[0] - years[0]:ref_years[1] - years[0] + 1]
                   for model in total_precipitation], axis=1))
    
    result.append({
        "short_title": f"evolution-absolue",
        "title": f"Précipitations totales pour la saison {season_name} selon le SSP{re.sub('ssp', '', ssp)}\n"+
                    f"sur la base de {len(models_data)} modèles",
        "xlabel": "Année",
        "ylabel": "Précipitations totales (mm)",
        "data": deepcopy(total_precipitation),
        "x_values": years,
        "misc":{
            "drawRefLine":mean_ref,
            "yMin": 0,
        }
    })
    
    # On calcule l'évolution des précipitations en partant d'une base 100
    for model in total_precipitation:
        total_precipitation[model] = 100 * np.array(total_precipitation[model]) / mean_ref


    result.append({
        "short_title": f"evolution-relative",
        "title": f"Précipitations totales pour la saison {season_name} selon le SSP{re.sub('ssp', '', ssp)}\n"+
                    f"sur la base de {len(models_data)} modèles",
        "xlabel": "Année",
        "ylabel": f"Évolution des précipitations\n(base 100 sur la période {ref_years[0]}-{ref_years[1]})",
        "data": total_precipitation,
        "x_values": years,
        "misc":{
            "drawRefLine":100,
            "yMin": 0,
        }
    })

    return result