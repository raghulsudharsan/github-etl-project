import requests
import pandas as pd
import json
from datetime import datetime
import s3fs
import os 

def run_etl():
    # AUTHENTICATION
    personal_access_token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {personal_access_token}"}

    #Extracting data from GitHub API
    url = "https://api.github.com/repos/apache/airflow"
    response = requests.get(url, headers=headers)
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

    s3 = boto3.client("s3")
    s3.put_object(
        Bucket="githubetl-5705",
        Key="github_repo_data.csv",
        Body=csv_buffer.getvalue()
    )

    print("File uploaded successfully to S3")# Saving DataFrame to S3 as a CSV file