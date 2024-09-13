#!/bin/bash

set -e

# Create the network if it doesn't exist
docker network inspect data-labeling-network >/dev/null 2>&1 || docker network create data-labeling-network

# Build the image based on the Dockerfile
docker build -t data-label-cli -f Dockerfile .

# Remove container if it exists
docker rm -f data-label-studio 2>/dev/null || true
docker rm -f data-label-cli 2>/dev/null || true

# Run data-label-studio container
docker run -d \
  --name data-label-studio \
  --network data-labeling-network \
  -p 8080:8080 \
  -v "$(pwd)/docker-volumes/label-studio:/label-studio/data" \
  -v "$(pwd)/../secrets:/secrets" \
  -e LABEL_STUDIO_DISABLE_SIGNUP_WITHOUT_LINK="true" \
  -e LABEL_STUDIO_USERNAME="pavlos@seas.harvard.edu" \
  -e LABEL_STUDIO_PASSWORD="awesome" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/data-service-account.json" \
  -e GCP_PROJECT="ac215-project" \
  -e GCP_ZONE="us-central1-a" \
  heartexlabs/label-studio:latest

# Run data-label-cli container
docker run --rm -ti \
  --name data-label-cli \
  --network data-labeling-network \
  -v "$(pwd)/../secrets:/secrets" \
  -v "$(pwd)/../data-labeling:/app" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/data-service-account.json" \
  -e GCP_PROJECT="ac215-project" \
  -e GCP_ZONE="us-central1-a" \
  -e GCS_BUCKET_NAME="cheese-app-data-demo" \
  -e LABEL_STUDIO_URL="http://data-label-studio:8080" \
  data-label-cli