#!/bin/bash

# Vérifier si le nombre d'arguments est correct
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 dossier_source dossier_destination"
    exit 1
fi

# Spécifier le dossier source et de destination
dossier="$1"
dossier_destination="$2"

# Créer le dossier de destination s'il n'existe pas déjà
mkdir -p "$dossier_destination"

# Appliquer la commande cdo remapnn à tous les fichiers .nc dans le dossier source
for fichier in "$dossier"/*.nc; do
    # Vérifier si le fichier est un fichier .nc
    if [ -f "$fichier" ]; then
        # Appliquer la commande cdo remapnn
        cdo remapnn,lon=0.7936/lat=45.5698 "$fichier" "$dossier_destination/${fichier##*/}"
    fi
done
