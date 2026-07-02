import requests
import pandas as pd
import json
from datetime import datetime
import s3fs
import os 
from airflow.sdk import Variable

def run_etl():
    # AUTHENTICATION
    personal_access_token = os.getenv("GITHUB_TOKEN") or Variable.get("GITHUB_TOKEN", default=None)
    
    if not personal_access_token:
        raise ValueError("CRITICAL: GITHUB_TOKEN is missing from both OS Environment and Airflow Variables!")
    headers = {"Authorization": f"Bearer {personal_access_token}"}

    #Extracting data from GitHub API
    url = "https://api.github.com/repos/apache/airflow"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"GitHub API returned error {response.status_code}: {response.text}")
        
    data = response.json()

    # Transforming data into a DataFrame
    df = pd.DataFrame([{
        "repo_name": data["name"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "language": data["language"]
    }]) 
    import io
    import boto3

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # 1. Fetch keys and store them in variables first
    aws_id = Variable.get("AWS_ACCESS_KEY_ID", default=None)
    aws_secret = Variable.get("AWS_SECRET_ACCESS_KEY", default=None)
    aws_region = Variable.get("AWS_DEFAULT_REGION", default="ap-south-1")

    # 2. Check if Airflow failed to retrieve them
    if not aws_id or not aws_secret:
        raise ValueError("CRITICAL: Airflow Variables for AWS keys are empty or missing!")

    # 3. Create the client with explicit configuration options
    from botocore.config import Config
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_id,
        aws_secret_access_key=aws_secret,
        region_name=aws_region,
        config=Config(signature_version='s3v4') # Forces modern authentication protocols
    )
    s3.put_object(
        Bucket="githubetl-5705",
        Key="github_repo_data.csv",
        Body=csv_buffer.getvalue()
    )

    print("File uploaded successfully to S3")# Saving DataFrame to S3 as a CSV file