#!/bin/bash

# Vérifier si le nombre d'arguments est correct
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 dossier_source dossier_destination"
    exit 1
fi

# Spécifier le dossier source et de destination
dossier_zip="$1"
dossier_models="$2"

# Créer le dossier de destination s'il n'existe pas déjà
mkdir -p "$dossier_models"

# Décompresser tous les fichiers zip dans le dossier source
for fichier_zip in "$dossier_zip"/*.zip; do
    # Vérifier si le fichier est un fichier zip
    if [ -f "$fichier_zip" ]; then
        # Décompresser le fichier zip dans le dossier de destination
        unzip "$fichier_zip" -d "$dossier_models/"
    fi
done

# Supprimer tous les fichiers extraits qui n'ont pas l'extension .nc
find "$dossier_models" -type f ! -name "*.nc" -delete
