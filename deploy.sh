
#!/bin/bash

CONTAINER_NAME="flask-client"
IMAGE_NAME="videotheque-client"

# Récupération du répertoire contenant ce script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
CLIENT_DIR="$SCRIPT_DIR/client"
DOCKERFILE="$SCRIPT_DIR/Dockerfile"

echo "Vérification de la configuration..."

if [ ! -f "$ENV_FILE" ]; then
    echo "Erreur : fichier .env introuvable."
    exit 1
fi

if [ ! -f "$DOCKERFILE" ]; then
    echo "Erreur : Dockerfile introuvable."
    exit 1
fi

if [ ! -f "$CLIENT_DIR/requirements.txt" ]; then
    echo "Erreur : requirements.txt introuvable dans client/."
    exit 1
fi

echo "Construction de l'image Docker..."

if ! docker build \
    -t "$IMAGE_NAME" \
    -f "$DOCKERFILE" \
    "$CLIENT_DIR"; then
    echo "Erreur lors de la construction de l'image."
    exit 1
fi

echo "Vérification de l'existence de l'ancien conteneur..."

# Vérifie si le conteneur existe (actif ou arrêté)
if [ "$(docker ps -aq -f name=^${CONTAINER_NAME}$)" ]; then
    echo "Le conteneur existe déjà. Suppression..."

    if ! docker rm -f "$CONTAINER_NAME"; then
        echo "Erreur lors de la suppression du conteneur."
        exit 1
    fi
fi

echo "Création du nouveau conteneur..."

if ! docker run -d \
    --name "$CONTAINER_NAME" \
    --env-file "$ENV_FILE" \
    -p 5001:5001 \
    "$IMAGE_NAME"; then

    echo "Erreur lors du démarrage du conteneur."
    exit 1
fi

echo "Déploiement terminé !"

echo "Vérification du démarrage..."

sleep 2

if [ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER_NAME")" = "true" ]; then
    echo "Le client fonctionne !"
else
    echo "Attention : le conteneur s'est arrêté."
    echo "Consulte les logs avec : docker logs $CONTAINER_NAME"
    exit 1
fi
