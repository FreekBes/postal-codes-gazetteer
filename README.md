# Gazetteer for Postal Codes in Grafana
This is a Grafana plugin that provides a gazetteer for postal codes.

---

## Creating the Gazetteer dataset

### Data source
Before beginning, download the postal codes data from [Opendatasoft](https://data.opendatasoft.com/explore/dataset/geonames-postal-code@public/export/) in GeoJSON format.

### Converting the data source for usage with Grafana
1. Set up a virtual environment:
```bash
python3 -m venv venv
```
2. Activate the virtual environment:
```bash
source venv/bin/activate
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```
4. Run the conversion script:
```bash
python convert.py --input <path to the GeoJSON file> --output <path to the output JSON file>
```

---

## How to use in Grafana
Upload the generated *postal-codes.json* output file to the Grafana *public/gazetteer* folder (in my case `/usr/share/grafana/public/gazetteer`).

Then, when creating a new panel, select the Geomap visualization.

Set the Location Mode to Lookup, specify the Lookup field to a combination of a country code and a postal code in the following format: `CN-POSTALCODE` (e.g. `DE-12345` or `US-12345`). Specific postal codes for buildings or addresses will not work, you will need to truncate them to use only the area code. You will need to figure out yourself how to do this.

Set the Gazetteer to the uploaded JSON file by pasting the URL to it into the input field and pressing enter.

> Example URL: *http://grafana.example.com/public/gazetteer/postal-codes.json*

## Warning
The data might be incomplete. In this case, do not reach out to me, instead complain to Opendatasoft.

Also, the dataset will be approximately 170MB in size. Loading a Geomap with this dataset will use a lot of network bandwidth and RAM on your device. Be aware of this before using it.
