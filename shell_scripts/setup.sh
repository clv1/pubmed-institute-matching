mkdir -p ./input_data/xml_data
mkdir -p ./input_data/grid_data
mkdir -p ./output_data

pip3 install -r requirements.txt
sleep 5
python3 -m spacy download en_core_web_sm

echo -e "\n\nSETUP COMPLETE."
sleep 5


