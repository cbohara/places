import sys
import requests
import json

def get_pois(config):
	"""Get poi data from here API"""
	url = "https://places.cit.api.here.com/places/v1/browse?"
	if config.query:
		url += "&q={}".format(config.query)

	if config.lat_long:
		url += "&at={}".format(config.lat_long)
	url += "&app_id={}&app_code={}".format(config.app_id, config.app_code)

	json_data = requests.get(url).text
	dict_data = json.loads(json_data)
	return dict_data["results"]["items"]

def get_fields(poi):
	"""Get line to write to output csv"""
	title = poi["title"]
	category = poi["category"]["title"]
	address = poi["vicinity"].split("<br/>")
	street = address[0]
	city, state_zip = address[1].split(",")
	state, zipcode = state_zip.split()
	lat,lon = poi["position"]
	to_write = [title, category, street, city, state, str(zipcode), str(lat), str(lon)]
	return ','.join(to_write)

def write_csv(configs, pois):
	"""Write pois to csv file"""
	with open("{}.csv".format(config.query), "w") as f:
		for poi in pois:
			line = get_fields(poi)
			f.write(line+"\n")

def execute(config):
	pois = get_pois(config)
	write_csv(config, pois)

if __name__ == "__main__":
	import configargparse
	config_parser = configargparse.ArgParser()
	config_parser.add('-c', '--config-file', required=False, is_config_file=True, help='config file path')
	config_parser.add('--app_id', required=True, help='here api APP ID')
	config_parser.add('--app_code', required=True, help='here api APP CODE')
	config_parser.add('--query', help='can specify search word or specific location')
	config_parser.add('--lat_long', help='provide specific latitude longtitude to search around as a single value i.e. "32.8242404,-117.389167"')

	config = config_parser.parse_args()
	for key, value in vars(config).items():
		print('{} = {}'.format(key, value))

	execute(config)
