library(CDFt)
library(stringr)

### Définition des variables
variable <- "tasmax"
time_freq <- "day"
ssp <- "ssp585" # parmi ssp245 et ssp585
path_to_data <- paste("data/csv/models/",variable,"_",time_freq,"/CMIP6/",ssp,"/",sep="")
path_to_predictions <- paste(path_to_data,"predictions",sep="")
path_to_historical <- paste(path_to_data,"historical",sep="")
path_to_unbiased <- paste(path_to_predictions,"/unbiased",sep="")

### Charger les noms des modèles
get_model_names <- function(folder, extension) {
    filenames <- list.files(path = folder, pattern = extension, full.names = FALSE)
    # On extrait les noms des modèles à partir des noms des fichiers
    # compris entre "tasmax_day_" et "_ssp245"
    filenames <- str_extract(filenames, paste("(?<=",time_freq,"_).*(?=_ssp)", sep=""))
    return(filenames)
}

model_names <- get_filenames_from_folder(path_to_predictions, ".csv")

### Fonction pour récupérer le fichier correspondant au nom du modèle dans le dossier demandé
get_data_filename <- function(folder, model_name, with_fullname = TRUE){
    filename <- list.files(path = folder, pattern = paste(time_freq,"_",model_name,"_ssp", sep=""), full.names = with_fullname)
    return(filename)
}

### Récupération des données historiques réelles
real_historical_filename <- list.files(path = "data/csv/observations", pattern = variable, full.names = TRUE)
real_historical_data <- read.csv(real_historical_filename, header = TRUE)
real_historical_data <- real_historical_data[[variable]]
real_historical_data <- as.numeric(unlist(real_historical_data))

### Pour chaque modèle, on ajuste le modèle en enlevant le biais
for (model_name in model_names){
    writeLines(paste("Etude du modèle :", model_name))

    # On récupère les fichiers correspondants aux données du modèle
    filename_historical <- get_data_filename(path_to_historical, model_name)
    filename_prediction <- get_data_filename(path_to_predictions, model_name)

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
    colnames(df) <- c("time", paste(variable,"_ba",sep=""))

    # On écrit le dataframe dans un fichier csv
    write.csv(df,
    paste(path_to_unbiased,"/", sub(".csv", "", get_data_filename(path_to_predictions, model_name, FALSE)),"_ba.csv",sep=""),
    row.names = FALSE)

    writeLines("--> Modèle traité !\n")
}

cat("Tous les modèles ont été traités !","\n")