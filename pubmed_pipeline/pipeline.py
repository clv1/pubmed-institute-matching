"""PIPELINE"""

import time
import logging
from os import environ
from dotenv import load_dotenv
import extract
import transform
import load


PUBMED_DATA = './input_data/xml_data/pubmed_data.xml'
LATEST_DATA = './input_data/xml_data/latest_data.xml'

def run_pipeline():
    """
    Runs the entire ETL pipeline.
    """
    load_dotenv()
    # Listen for new XML files added to the input bucket
    # --- AWS step function

    # --- EXTRACT
    logging.info('Extracting data...')
    s3 = extract.get_s3_client()
    extract.download_latest_xml_file(
        s3, environ['DOWNLOAD_BUCKET'], environ['DOWN_BUCKET_PREFIX'])
    logging.info('Extraction complete.\n')

    # --- TRANSFORM
    logging.info('Transforming data...')
    root = transform.parse_xml(LATEST_DATA)
    dataframe = transform.assemble_articles_df(root)
    logging.info('Transforming complete.\n')

    # --- LOAD
    logging.info('Uploading data...')
    load.generate_output_files(dataframe)
    load.upload_file(s3, bucket=environ['UPLOAD_BUCKET'])
    logging.info('Data upload complete.\n')

    # Notify users when a task begins/ends
    # --- AWS SES/SNS?

if __name__ == "__main__":

    start_time = time.perf_counter()
    run_pipeline()
    stop_time = time.perf_counter()

    print(f"""total runtime ---
          {round(stop_time - start_time, 1)} seconds""")
