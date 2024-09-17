@echo off
setlocal

:: Exit if any command fails
set "ERRORLEVEL="

:: Create the network if it doesn't exist
docker network inspect data-labeling-network >nul 2>&1 || docker network create data-labeling-network

:: Build the image based on the Dockerfile
docker build -t data-label-cli -f Dockerfile .

:: Run all containers using docker-compose
docker-compose run --rm --service-ports data-label-cli

endlocal