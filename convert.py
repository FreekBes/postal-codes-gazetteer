import argparse
import json
import os
from tqdm import tqdm

def feature_to_gazetteer_point(feature):
	# Get properties
	properties = feature["properties"]
	coordinates = feature["geometry"]["coordinates"]

	# Create name for location based on name + country code
	if "place_name" in properties:
		name = properties["place_name"]
	else:
		name = properties["admin_name1"] + ", " + properties["admin_name2"] + ", " + properties["country_code"]

	# Create new feature
	new_feature = {
		"keys": [
			f"{properties['country_code']}-{properties['postal_code']}"
		],
		"latitude": coordinates[1],
		"longitude": coordinates[0],
		"name": name,
	}

	return new_feature, properties["country_code"]

def postal_code_is_duplicate(point, seen_postal_codes):
	for postal_code in point["keys"]:
		if postal_code in seen_postal_codes:
			return True
	return False

def print_exit():
	print("Exiting...")
	exit()

# Check if python file is executed directly
if __name__ == "__main__":
	# Set up argument parser
	parser = argparse.ArgumentParser(description="Converts postal codes to a format that can be used in the gazetteer")
	parser.add_argument("--input", help="Input GeoJSON file from Opendatasoft", default="geonames-postal-code@public.geojson")
	parser.add_argument("--output", help="Output JSON file for the gazetteer", default="postal-codes.json")
	args = parser.parse_args()

	# Check if input file exists
	try:
		with open(args.input, "r") as f:
			pass
	except FileNotFoundError:
		download = input(f"Input file {args.input} does not exist! Would you like to download it automatically? (Y/n): ")
		if download.lower() != "n":
			import requests
			url = "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/geonames-postal-code@public/exports/geojson?lang=en&timezone=Europe%2FBerlin"
			response = requests.get(url, stream=True, allow_redirects=True)
			if response.status_code != 200:
				response.raise_for_status() # Will only raise for 4xx codes, so...
				raise Exception(f"Request to {url} failed with status code {response.status_code}")
			total_size = int(response.headers.get("content-length", 0))
			block_size = 1024
			with tqdm(total=total_size, unit="B", unit_scale=True, desc="Downloading Geonames Postal Code dataset") as pbar:
				with open(args.input, "wb") as f:
					for data in response.iter_content(block_size):
						f.write(data)
						pbar.update(len(data))
			if total_size != 0 and pbar.n != total_size:
				print("An error occurred while downloading the file. Cleaning up...")
				os.remove(args.input)
				print_exit()
		else:
			print_exit()

	# Create gazetteer json file
	gazetteer = []
	seen_postal_codes = dict() # dict with each key = country code, value = set of postal codes

	# Open input file
	print(f"Reading input file: {args.input}...")
	with open(args.input, "r") as f:
		data = f.read()

		# Parse geojson
		print("Parsing geojson... This may take a while.")
		geojson = json.loads(data)

		# Iterate over features
		with tqdm(total=len(geojson["features"]), desc="Converting features") as pbar:
			for feature in geojson["features"]:
				# Convert feature to gazetteer point
				point, country_code = feature_to_gazetteer_point(feature)

				# If the country has not been encountered yet, create a postal code set for it
				if not country_code in seen_postal_codes:
					seen_postal_codes[country_code] = set()

				# Add point to gazetteer if it is not a duplicate of an already seen postal code within the country
				if not postal_code_is_duplicate(point, seen_postal_codes[country_code]):
					gazetteer.append(point)
					for postal_code in point["keys"]:
						seen_postal_codes[country_code].add(postal_code)

				# Update progress bar
				pbar.update(1)

	print(f"Found {len(gazetteer)} unique postal codes in {len(seen_postal_codes)} countries.")

	# Write gazetteer to output file
	print(f"Writing gazetteer to output file: {args.output}...")

	# Check if file exists, if it does, ask for confirmation to overwrite
	try:
		with open(args.output, "r") as f:
			overwrite = input(f"Output file {args.output} already exists! Do you want to overwrite it? (y/N): ")
			if overwrite.lower() != "y":
				print_exit()
	except FileNotFoundError:
		pass

	try:
		with open(args.output, "w") as f:
			# Pretty print json
			json.dump(gazetteer, f, indent=4)
	except Exception as e:
		print(f"An error occurred while writing the output file: {e}")
		print_exit()

	# Clean up happens automatically when the script exits, but may take a while, so let's print a message
	print("Cleaning up before exiting... Please wait...")
