set -e
# Ensure docker is running before executing this script

# Load the env variables
set -a
source .env
set +a


IMAGE_NAME=compliance-api:latest
source deploy_acr.sh

echo "Binding the container registry image to the container app..."

az containerapp update \
  --name $CONTAINER_APP \
  --resource-group rg-cmplianz-hack-uksouth \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME
