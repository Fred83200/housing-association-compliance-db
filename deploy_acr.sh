set -e
# Ensure docker is running before executing this script

# Load the env variables
set -a
source .env
set +a


IMAGE_NAME=compliance-api:latest
az acr login --name $ACR_NAME

HEAD_COMMIT_ID=$(git rev-parse --short HEAD)

docker build --platform linux/amd64 -t $IMAGE_NAME .

docker tag $IMAGE_NAME $ACR_NAME.azurecr.io/$IMAGE_NAME

docker push $ACR_NAME.azurecr.io/$IMAGE_NAME
