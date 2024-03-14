#!/bin/bash

### Exemple de commande pour exécuter le script
# ./process_remap_nc_files.sh global/tasmax_day/CMIP6/historical

# Vérifier si le nombre d'arguments est correct
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 dossier_source. Le dossier destination est par défaut local suivi de l'arborescence du dossier source"
    exit 1
fi

# Spécifier le dossier source et de destination
dossier="$1"
dossier_destination="${dossier/global\//local\/}"

# Créer le dossier de destination s'il n'existe pas déjà
echo "1. Création du dossier $dossier_destination"
mkdir -p "$dossier_destination"

# Appliquer la commande cdo remapnn à tous les fichiers .nc dans le dossier source
echo "2. Application de la commande cdo remapnn à tous les fichiers .nc dans $dossier"
for fichier in "$dossier"/*.nc; do
    # Vérifier si le fichier est un fichier .nc
    if [ -f "$fichier" ]; then
        # Appliquer la commande cdo remapnn
        cdo remapnn,lon=0.7936/lat=45.5698 "$fichier" "$dossier_destination/${fichier##*/}"
    fi
done
# Compter le nombre de fichiers .nc remappés
nb_fichiers=$(find "$dossier_destination" -type f -name "*.nc" | wc -l)
if [ "$nb_fichiers" -eq 0 ]; then
    echo "Aucun fichier n'a été remappé"
    exit 1
fi
echo "Nombre de fichiers remappés avec succès : $nb_fichiers"

echo "==> Le script a terminé avec succès !"
