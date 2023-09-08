# Mushroom App: Data Labeling & Versioning Demo

## Prerequisites
* Have Docker installed
* Cloned this repository to your local machine with a terminal up and running
* Check that your Docker is running with the following command

`docker run hello-world`

### Install Docker 
Install `Docker Desktop`

#### Ensure Docker Memory
- To make sure we can run multiple container go to Docker>Preferences>Resources and in "Memory" make sure you have selected > 4GB

### Install VSCode  
Follow the [instructions](https://code.visualstudio.com/download) for your operating system.  
If you already have a preferred text editor, skip this step.  

## Mushroom App: Data Labeling
In this tutorial we will setup a data labeling web app to label data for the mushroom app. We will use Docker to run everything inside containers.

### Clone the github repository
- Clone or download from [here](https://github.com/dlops-io/data-labeling)

## Setup GCP Credentials
Next step is to enable our container to have access to GCP Storage buckets. 

### Create a local **secrets** folder

It is important to note that we do not want any secure information in Git. So we will manage these files outside of the git folder. At the same level as the `data-labeling` folder create a folder called **secrets**

Your folder structure should look like this:
```
   |-data-labeling
   |-secrets
```

### Setup GCP Service Account
- Here are the step to create a service account:
- To setup a service account you will need to go to [GCP Console](https://console.cloud.google.com/home/dashboard), search for  "Service accounts" from the top search box. or go to: "IAM & Admins" > "Service accounts" from the top-left menu and create a new service account called "data-service-account". For "Service account permissions" select "Cloud Storage" > "Storage Admin". Then click done.
- This will create a service account
- On the right "Actions" column click the vertical ... and select "Create key". A prompt for Create private key for "data-service-account" will appear select "JSON" and click create. This will download a Private key json file to your computer. Copy this json file into the **secrets** folder. Rename the json file to `data-service-account.json`


### Attach GCP Credentials to Container
- To setup GCP Credentials in a container we need to set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` inside the container to the path of the secrets file from the previous step

- Update `docker-shell.sh` or `docker-shell.bat` to add the new environment variable

`docker-compose.yml`
```
version: "3.8"
networks:
    default:
        name: data-labeling-network
        external: true
services:
    data-label-cli:
        image: data-label-cli
        container_name: data-label-cli
        volumes:
            - ../secrets:/secrets
            - ../data-labeling:/app
        environment:
            GOOGLE_APPLICATION_CREDENTIALS: /secrets/data-service-account.json 
            GCP_PROJECT: "ac215-project" [CHANGE TO YOUR GCP PROJECT]
            GCP_ZONE: "us-central1-a"
        depends_on:
            - data-label-studio
    data-label-studio:
        image: heartexlabs/label-studio:latest
        container_name: data-label-studio
        ports:
            - 8080:8080
        volumes:
            - ./docker-volumes/label-studio:/label-studio/data
            - ../secrets:/secrets
        environment:
            LABEL_STUDIO_DISABLE_SIGNUP_WITHOUT_LINK: "true"
            LABEL_STUDIO_USERNAME: "pavlos@seas.harvard.edu" [CHANGE TO YOUR EMAIL]
            LABEL_STUDIO_PASSWORD: "awesome" [CHANGE IF NECESSARY]
            GOOGLE_APPLICATION_CREDENTIALS: /secrets/data-service-account.json
            GCP_PROJECT: "ac215-project" [CHANGE TO YOUR GCP PROJECT]
            GCP_ZONE: "us-central1-a"
```

## Prepare Dataset
In this step we will assume we have already collected some data for the mushroom app. The images are of various mushrooms belonging to either `amanita`, `crimini`, or `oyster` type. None of the images are labeled and our task here is to use label studio to manage labeling of images.

### Download data
- Download the unlabeled data from [here](https://github.com/dlops-io/datasets/releases/download/v3.0/mushrooms_unlabeled.zip)
- Extract the zip file

### Create GCS Bucket
- Go to `https://console.cloud.google.com/storage/browser`
- Create a bucket `mushroom-app-data-demo` (REPLACE WITH YOUR BUCKET NAME)
- Create a folder `mushrooms_unlabeled` inside the bucket
- Create a folder `mushrooms_labeled` inside the bucket

### Upload data to Bucket
- Upload the images from your local folder into the folder `mushrooms_unlabeled` inside the bucket

## Run Label Studio Container

### Run `docker-shell.sh` or `docker-shell.bat`
Based on your OS, run the startup script to make building & running the container easy

- Make sure you are inside the `data-labeling` folder and open a terminal at this location
- Run `sh docker-shell.sh` or `docker-shell.bat` for windows

This will run two container. The label studio container and a CLI container that can call API's to label studio. You can verify them by running `docker container ls` on another terminal prompt. You should see something like this:
```
CONTAINER ID   IMAGE                             COMMAND                  CREATED              STATUS              PORTS                                                      NAMES
00d808ab0386   data-label-cli                    "pipenv shell"           About a minute ago   Up About a minute                                                              data-labeling-data-label-cli-run
4ab1ec940b4a   heartexlabs/label-studio:latest   "./deploy/docker-ent…"   2 days ago           Up 2 days           0.0.0.0:8080->8080/tcp                                     data-label-studio
```


## Setup Label Studio

### Create Annotation Project
Here we will setup the Label Studio App to user our mushroom images so we can annotate them. 
- Run the Label Studio App by going to `http://localhost:8080/`
- Login with `pavlos@seas.harvard.edu` / `awesome`, use the credentials in the docker compose file that you used
- Click `Create Project` to create a new project
- Give it a project name
- Skip `Data Import` tab and go to `Labeling Setup`
- Select Template: Computer Vision > Image Classification
- Remove the default label choices and add: `amanita`, `crimini`, `oyster`
- Save

### Configure Cloud Storage
Next we will configure Label Studio to read images from a GCS bucket and save annotations to a GCS bucket
- Go the project created in the previous step
- Click on `Settings` and select `Cloud Storage` on the left options
- Click `Add Source Storage`
- Then in the popup for storage details:
    - Storage Type: `Google Cloud Storage`
    - Storage Title: `Mushroom Images`
    - Bucket Name: `mushroom-app-data-demo` (REPLACE WITH YOUR BUCKET NAME)
    - Bucket Prefix: `mushrooms_unlabeled`
    - File Filter Regex: `.*`
    - Enable: Treat every bucket object as a source file
    - Enable: Use pre-signed URLs
    - Ignore: Google Application Credentials
    - Ignore: Google Project ID
- You can `Check Connection` to make sure your connection works
- `Save` your changes
- Click `Sync Storage` to start syncing from the bucket to label studio
- Click `Add Target Storage`
- Then in the popup for storage details:
    - Storage Type: `Google Cloud Storage`
    - Storage Title: `Mushroom Images`
    - Bucket Name: `mushroom-app-data-demo` (replace with your bucket name)
    - Bucket Prefix: `mushrooms_labeled`
    - Ignore: Google Application Credentials
    - Ignore: Google Project ID
- You can `Check Connection` to make sure your connection works
- `Save` your changes

### Enable cross-origin resource sharing (CORS)
In odder to view images in Label studio directly from GCS Bucket, we need to enable CORS
- Go to the shell where we ran the docker containers
- Run `python cli.py -c`
- To view the CORs settings, run `python cli.py -m`
- To view all the code open `data-labeling` folder in VSCode or any IDE of choice


### Annotate Data
Go into the newly create project and you should see the images automatically pulled in from the GCS Cloud Storage Bucket
- Click on an item in the grid to annotate using the UI
- Repeat for a few of the images

### View Annotations in GCS Bucket
- Go to `https://console.cloud.google.com/storage/browser`
- Go into the `mushroom-app-data` (replace with your bucket name) and then into the folder `mushrooms_labeled`
- You should see some json files corresponding to the images in the `mushrooms_unlabeled` that have been annotated


### View Annotations using CLI
- Go to the shell where ran the docker containers
- Open `data-labeling` folder in VSCode 
- Uncomment the function call:
    ```
    # Get projects from label studio using API
    await get_projects()
    ```
- Run `python -m cli`
- Uncomment the function call:
    ```
    # View Annotation Tasks
    await get_project_tasks(1)
    ```
- Run `python -m cli`

You will see the json output of the annotations for each image that is being stored in Label Studio
```
Annotations: [{'id': 5, 'created_username': ' pavlos@seas.harvard.edu, 1', 'created_ago': '1\xa0hour, 53\xa0minutes', 'completed_by': 1, 'result': [{'value': {'choices': ['amanita']}, 'id': 'qHjUzqXO6W', 'from_name': 'choice', 'to_name': 'image', 'type': 'choices', 'origin': 'manual'}], 'was_cancelled': False, 'ground_truth': False, 'created_at': '2023-09-06T17:33:08.558474Z', 'updated_at': '2023-09-06T17:33:08.558492Z', 'draft_created_at': None, 'lead_time': 5.981, 'import_id': None, 'last_action': None, 'task': 1, 'project': 1, 'updated_by': 1, 'parent_prediction': None, 'parent_annotation': None, 'last_created_by': None}]

Annotations: [{'id': 1, 'created_username': ' pavlos@seas.harvard.edu, 1', 'created_ago': '1\xa0hour, 55\xa0minutes', 'completed_by': 1, 'result': [{'value': {'choices': ['amanita']}, 'id': 'Hp3wZORhBI', 'from_name': 'choice', 'to_name': 'image', 'type': 'choices', 'origin': 'manual'}], 'was_cancelled': False, 'ground_truth': False, 'created_at': '2023-09-06T17:31:04.307102Z', 'updated_at': '2023-09-06T17:31:04.307117Z', 'draft_created_at': None, 'lead_time': 11.197, 'import_id': None, 'last_action': None, 'task': 2, 'project': 1, 'updated_by': 1, 'parent_prediction': None, 'parent_annotation': None, 'last_created_by': None}]
```

## Mushroom App: Data Versioning
In this tutorial we will setup a data versioning pipeline step for the mushroom app. We will use Docker to run everything inside containers.

### Clone the github repository
- Clone or download from [here](https://github.com/dlops-io/data-versioning)

Your folder structure should look like this:
```
   |-data-labeling
   |---docker-volumes
   |-----label-studio
   |-data-versioning
   |-secrets
```


By the end of this tutorial your folder structure should look like this:
```
   |-data-labeling
   |---docker-volumes
   |-----label-studio
   |-data-versioning
   |---dataset
   |---dataset_prep
   |-secrets
```

## Docker Cleanup
To make sure we do not have any running containers and clear up an unused images
* Run `docker container ls`
* Stop any container that is running
* Run `docker system prune`
* Run `docker image ls`
