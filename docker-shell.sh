#!/bin/bash

set -e

# Create the network if it doesn't exist
docker network inspect data-labeling-network >/dev/null 2>&1 || docker network create data-labeling-network
 
# Remove container if it exists
docker rm -f data-label-studio 2>/dev/null || true
 
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

