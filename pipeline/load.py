# pylint: disable = invalid-name
"""Load script."""

import os
from os import environ
import pandas as pd
from boto3 import client
import botocore.exceptions
from dotenv import load_dotenv

load_dotenv()
PREFIX = environ['UP_BUCKET_PREFIX']
OUTPUT_FILE_PATH = './output_data/matched_institutes.csv'

def generate_output_files(dataframe: pd.DataFrame) -> dict:
    """
    Takes in a pandas dataframe and exports it to a csv and xlsx file.
    """
    dataframe.to_csv("./output_data/matched_institutes.csv", index=False)
    dataframe.to_excel("./output_data/matched_institutes.xlsx", index=False)
    return {'success': 'Data exported as output files.'}

def upload_file(s3_client: client, bucket: str) -> dict:
    """
    Uploads generated csv file to designated S3 bucket.
    """
    output_file_name = os.path.basename(OUTPUT_FILE_PATH)

    try:
        s3_client.upload_file(OUTPUT_FILE_PATH, bucket, f'{PREFIX}/{output_file_name}')
    except botocore.exceptions.ClientError:
        return {'error': f'S3 client is unable to access {bucket} bucket.'}
    return {'success': 'Data uploaded to S3 bucket.'}
