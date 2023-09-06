import os
import asyncio
import pandas as pd
import traceback
import time
from google.cloud import storage
from label_studio_sdk import Client


GCS_BUCKET_NAME = "mushroom-app-data"  # Your bucket name
# Connect to the Label Studio API and check the connection
LABEL_STUDIO_URL = "http://data-label-studio:8080"
API_KEY = "bcc79f6a249c5b482d441018af20e952798db2b4"  # Get your API key from User > Account & Settings > Access Token
AUTH_HEADER = {"Authorization": f"Token {API_KEY}"}

label_studio_client = None


async def set_cors_configuration():
    """Set a bucket's CORS policies configuration."""

    print("set_cors_configuration()")
    bucket_name = GCS_BUCKET_NAME

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    bucket.cors = [
        {
            "origin": ["*"],
            "method": ["GET"],
            "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
            "maxAgeSeconds": 3600,
        }
    ]
    bucket.patch()

    print(f"Set CORS policies for bucket {bucket.name} is {bucket.cors}")
    return bucket


async def view_bucket_metadata():
    """Prints out a bucket's metadata."""

    print("view_bucket_metadata()")
    bucket_name = GCS_BUCKET_NAME

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    print(f"ID: {bucket.id}")
    print(f"Name: {bucket.name}")
    print(f"Storage Class: {bucket.storage_class}")
    print(f"Location: {bucket.location}")
    print(f"Location Type: {bucket.location_type}")
    print(f"Cors: {bucket.cors}")
    print(f"Default Event Based Hold: {bucket.default_event_based_hold}")
    print(f"Default KMS Key Name: {bucket.default_kms_key_name}")
    print(f"Metageneration: {bucket.metageneration}")
    print(
        f"Public Access Prevention: {bucket.iam_configuration.public_access_prevention}"
    )
    print(f"Retention Effective Time: {bucket.retention_policy_effective_time}")
    print(f"Retention Period: {bucket.retention_period}")
    print(f"Retention Policy Locked: {bucket.retention_policy_locked}")
    print(f"Requester Pays: {bucket.requester_pays}")
    print(f"Self Link: {bucket.self_link}")
    print(f"Time Created: {bucket.time_created}")
    print(f"Versioning Enabled: {bucket.versioning_enabled}")
    print(f"Labels: {bucket.labels}")


async def get_projects():
    print("get_projects")

    # Examples using SDK: https://labelstud.io/sdk/project.html#label_studio_sdk.project.Project

    projects = label_studio_client.get_projects()
    print(projects)
    for project in projects:
        print(project.id)

    project = label_studio_client.get_project(1)
    print(project)


async def get_project_tasks(project_id):
    print("get_project_tasks")

    # Examples using SDK: https://labelstud.io/sdk/project.html#label_studio_sdk.project.Project
    project = label_studio_client.get_project(project_id)
    print(project)
    # print(project.get_tasks())
    print("Number of tasks:", len(project.tasks))

    labeled_tasks = project.get_labeled_tasks()
    print("Number of labled tasks:", len(labeled_tasks))
    for labeled_task in labeled_tasks:
        print("Annotations:", labeled_task["annotations"])


async def run():
    try:
        print("CLI....")
        total_start_time = time.time()

        global label_studio_client
        enable_label_studio = True

        if enable_label_studio:
            label_studio_client = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
            label_studio_client.check_connection()

        # Set the CORS configuration on a bucket
        # await set_cors_configuration()

        # View the CORS configuration for a bucket
        # await view_bucket_metadata()

        # Get projects from label studio using API
        # await get_projects()

        # Tasks
        # await get_project_tasks(1)

        print("************** Complete ****************")
        execution_time = (time.time() - total_start_time) / 60.0
        print("Total execution time (mins)", execution_time)

    except Exception as e:
        print(e)
        traceback.print_exc()


asyncio.run(run())
