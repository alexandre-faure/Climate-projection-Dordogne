library(CDFt)
library(stringr)

### Définition des variables
variable <- "pr"
time_freq <- "day"
ssp <- "ssp245" # parmi ssp245 et ssp585
path_to_data <- paste("data/csv/models/",variable, "_",time_freq, "/CMIP6/",sep="")
path_to_predictions <- paste(path_to_data, ssp, "/", sep="")
path_to_historical <- paste(path_to_data, "historical/", sep="")
path_to_bias_adjusted <- paste(path_to_data, ssp, "_ba/", sep="")
real_historical_data_path <- "data/csv/observations/open-meteo-45.59N0.85E335m.csv"

### On crée le dossier pour les données ajustées
dir.create(path_to_bias_adjusted, showWarnings = FALSE)

### Charger les noms des modèles
get_model_names <- function(folder, extension) {
    filenames <- list.files(path = folder, pattern = extension, full.names = FALSE)
    # On extrait les noms des modèles à partir des noms des fichiers
    # compris entre "day_" et "_ssp" ou  "_historical"
    filenames <- str_extract(filenames, paste("(?<=",time_freq, "_).*(?=_ssp|_historical)", sep=""))
    return(filenames)
}

model_names <- get_model_names(path_to_historical, ".csv")

### Récupération des données historiques réelles
real_historical_data <- read.csv(real_historical_data_path, header = TRUE)
real_historical_data <- real_historical_data[[paste(variable, "_day", sep="")]]
real_historical_data <- as.numeric(unlist(real_historical_data))

# Fonction pour récupérer le nom du fichier de données
get_data_filename <- function(path, model_name, with_extension = TRUE){
    filenames <- list.files(path = path, pattern = paste(model_name, ".*.csv", sep=""), full.names = with_extension)
    # Si on trouve plus d'un fichier, on envoie un message d'avertissement
    if(length(filenames) > 1){
        warning(paste("Plus d'un fichier correspondant au modèle", model_name, "a été trouvé pour le dossier", path, ". Le premier fichier trouvé sera utilisé."))
    }
    # Si aucun fichier n'est trouvé
    if(length(filenames) == 0){
        warning(paste("Aucun fichier correspondant au modèle", model_name, "n'a été trouvé pour le dossier", path, "."))
        return(-1)
    }
    # On renvoie le nom du premier fichier trouvé
    return(filenames[1])
}

### Pour chaque modèle, on ajuste le modèle en enlevant le biais
for (model_name in model_names){
    writeLines(paste("Etude du modèle :", model_name))

    # On récupère les fichiers correspondants aux données du modèle
    filename_historical <- get_data_filename(path_to_historical, model_name)
    filename_prediction <- get_data_filename(path_to_predictions, model_name)

    # Si un des fichiers n'est pas trouvé, on passe au modèle suivant
    if(filename_historical == -1 || filename_prediction == -1){
        writeLines("--> Modèle non traité !\n")
        next
    }

    # On charge les données
    historical_data <- read.csv(filename_historical, header = TRUE)
    historical_data <- historical_data[[variable]]
    historical_data <- as.numeric(unlist(historical_data))

    prediction_data <- read.csv(filename_prediction, header = TRUE)
    time <- prediction_data$time
    prediction_data <- prediction_data[[variable]]
    prediction_data <- as.numeric(unlist(prediction_data))

    # On retire le biais avec le module CDFt
    CT <- CDFt(real_historical_data, historical_data, prediction_data)

    # On créé un dataframe contenant les données sans biais
    ds <- CT$DS
    ds <- round(ds, 2)
    df <- data.frame(time, ds)

    # On écrit le dataframe dans un fichier csv
    write.csv(df,
    paste(path_to_bias_adjusted, get_data_filename(path_to_predictions, model_name, FALSE) ,sep=""),
    row.names = FALSE)

    writeLines("--> Modèle traité !\n")
}

cat("Tous les modèles ont été traités !", "\n")