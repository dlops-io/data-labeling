@echo off
setlocal

:: Exit if any command fails
set "ERRORLEVEL="

:: Build the image based on the Dockerfile
docker build -t data-label-cli -f Dockerfile .

:: Remove container if it exists
docker rm -f data-label-cli >nul 2>&1 || echo Container does not exist, continuing...

:: Run data-label-cli container
docker run --rm -ti ^
  --name data-label-cli ^
  --network data-labeling-network ^
  -v "%cd%\..\secrets:/secrets" ^
  -v "%cd%\..\data-labeling:/app" ^
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/data-service-account.json" ^
  -e GCP_PROJECT="ac215-project" ^
  -e GCP_ZONE="us-central1-a" ^
  -e GCS_BUCKET_NAME="cheese-app-data-demo" ^
  -e LABEL_STUDIO_URL="http://data-label-studio:8080" ^
  data-label-cli

endlocal