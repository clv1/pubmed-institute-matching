curl https://sigma-resources-public.s3.eu-west-2.amazonaws.com/pharmazer/pubmed_result_sjogren.xml \
--output ./input_data/xml_data/pubmed_data.xml

curl https://sigma-resources-public.s3.eu-west-2.amazonaws.com/pharmazer/addresses.csv \
--output ./input_data/grid_data/grid_addresses.csv

curl https://sigma-resources-public.s3.eu-west-2.amazonaws.com/pharmazer/institutes.csv \
--output ./input_data/grid_data/grid_institutes.csv

curl https://sigma-resources-public.s3.eu-west-2.amazonaws.com/pharmazer/aliases.csv \
--output ./input_data/grid_data/grid_aliases.csv
