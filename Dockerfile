FROM python:latest

WORKDIR /pipeline_app

COPY pubmed_pipeline/extract.py .
COPY pubmed_pipeline/transform.py .
COPY pubmed_pipeline/load.py .
COPY pubmed_pipeline/pipeline.py .

COPY requirements.txt .
COPY shell_scripts/setup.sh .
RUN bash setup.sh
RUN curl https://sigma-resources-public.s3.eu-west-2.amazonaws.com/pharmazer/institutes.csv \
--output ./input_data/grid_data/grid_institutes.csv

RUN echo "Building the pipeline image." 
CMD python3 pipeline.py