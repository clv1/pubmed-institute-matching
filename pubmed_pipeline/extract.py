"""Extract script."""

import os
from os import environ, path
import botocore.exceptions

from boto3 import client
from dotenv import load_dotenv


def get_s3_client() -> client:
    """Connects to the s3 by authenticating a boto3 client."""
    load_dotenv()

    s3_client = client("s3",
                       aws_access_key_id=environ["AWS_ACCESS_KEY_ID"],
                       aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])

    return s3_client


def get_sorted_bucket_keys(s3_client: client, bucket: str, prefix=None) -> list[str]:
    """
    Lists the contents of an S3 bucket, optionally filtered by a prefix and
    sorted in ascending order of upload recency.
    """
    if not prefix:
        contents = s3_client.list_objects(Bucket=bucket)["Contents"]
    else:
        contents = s3_client.list_objects(
            Bucket=bucket, Prefix=prefix)["Contents"]

    sorted_contents = sorted(contents, key=lambda d: d['LastModified'])
    return [s3_object["Key"] for s3_object in sorted_contents]


def download_latest_xml_file(s3_client: client, bucket: str, s3_folder_prefix=None):
    """
    Downloads the most recent file uploaded to S3.
    TODO: add a timestamp to download.
    """
    try:
        latest_key = get_sorted_bucket_keys(
            s3_client, bucket, s3_folder_prefix)[-1]
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'NoSuchBucket':
            # logging.error("The bucket %s is not available.", bucket)
            return {'error': f'The bucket {bucket} is not available.'}
        raise

    if not path.exists('input_data/xml_data'):
        os.mkdir('input_data/xml_data')

    # key_name = os.path.basename(latest_key)
    # local_filepath = f'input_data/xml_data/{key_name}'
    local_filepath = f'input_data/xml_data/latest_data.xml'

    if ".xml" in latest_key:
        s3_client.download_file(bucket, latest_key, local_filepath)
        return {'success': 'Latest XML data downloaded from S3 bucket.'}
    return {'error': 'No downloadable data exists at this S3 location.'}


# if __name__ == "__main__":
#     load_dotenv()
#     s3 = get_s3_client()

    # --- Explore the S3 contents:
    # print(get_bucket_keys(s3, environ['BUCKET']))
    # print(get_sorted_bucket_keys(
    #     s3, environ['BUCKET'], prefix=environ['BUCKET_SUBFOLDER_PREFIX']))\

    # --- Download files:
    # print(download_latest_xml_file(
    #     s3, environ['BUCKET'], environ['BUCKET_SUBFOLDER_PREFIX']))
