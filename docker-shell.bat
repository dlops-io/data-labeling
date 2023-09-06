
REM Create the network if we don't have it yet
docker network inspect data-labeling >/dev/null 2>&1 || docker network create data-labeling

REM Build the image based on the Dockerfile
docker build -t data-label-cli -f Dockerfile .

REM Run All Containers
docker-compose run --rm --service-ports data-label-cli