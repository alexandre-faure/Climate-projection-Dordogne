#!/bin/bash

### Exemple de commande pour exécuter le script
# ./process_unzip_archives.sh ssp245_tasmax/ ../raw/global/tasmax_day/CMIP6/ssp245

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
echo "1. Création du dossier $dossier_models"

# Décompresser tous les fichiers zip dans le dossier source
echo "2. Décompression des fichiers zip dans $dossier_models"
for fichier_zip in "$dossier_zip"/*.zip; do
    # Vérifier si le fichier est un fichier zip
    if [ -f "$fichier_zip" ]; then
        # Décompresser le fichier zip dans le dossier de destination
        unzip "$fichier_zip" -d "$dossier_models/" > /dev/null
    fi
done
# Compter le nombre de fichiers dézippés
nb_fichiers=$(find "$dossier_models" -type f -name "*.nc" | wc -l)
if [ "$nb_fichiers" -eq 0 ]; then
    echo "Aucun fichier n'a été dézippé"
    exit 1
fi
echo "Nombre de fichiers dézippés avec succès : $nb_fichiers"

# Supprimer tous les fichiers extraits qui n'ont pas l'extension .nc
echo "3. Suppression des fichiers extraits qui n'ont pas l'extension .nc"
find "$dossier_models" -type f ! -name "*.nc" -delete
echo "Suppression terminée"


echo "==> Le script a terminé avec succès !"
