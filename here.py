import sys
import requests
import json

def get_here_api_data(config):
	"""Get poi data from here API"""
	url = "https://places.cit.api.here.com/places/v1/browse?"
	if config.query:
		url += "&q={}".format(config.query)
	if config.lat_long:
		url += "&at={}".format(config.lat_long)
	url += "&app_id={}&app_code={}".format(config.app_id, config.app_code)
	return requests.get(url).text

def get_pois(json_data):
	"""Get pois from here API data"""
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

def read_json(config):
	"""Read in json file to avoid API call"""
	with open("json/{}.json".format(config.query), "r") as f:
		return f.read()

def write_json(config, json_data):
	"""Write pois to csv file"""
	with open("json/{}.json".format(config.query), "w") as f:
		f.write(json_data)

def write_csv(config, pois):
	"""Write pois to csv file"""
	with open("csv/{}.csv".format(config.query), "w") as f:
		for poi in pois:
			line = get_fields(poi)
			f.write(line+"\n")

def execute(config):
	if config.api_call:
		pois = get_pois(get_here_api_data(configs))
	else:
		pois = get_pois(read_json(config))
	write_csv(config, pois)

if __name__ == "__main__":
	import configargparse
	config_parser = configargparse.ArgParser()
	config_parser.add('-c', '--config-file', required=False, is_config_file=True, help='config file path')
	config_parser.add('--app_id', required=True, help='here api APP ID')
	config_parser.add('--app_code', required=True, help='here api APP CODE')
	config_parser.add('--query', help='can specify search word or specific location')
	config_parser.add('--lat_long', help='provide specific latitude longtitude to search around as a single value i.e. "32.8242404,-117.389167"')
	config_parser.add('--api_call', default=False, help='use local json file to avoid another API call')

	config = config_parser.parse_args()
	for key, value in vars(config).items():
		print('{} = {}'.format(key, value))

	execute(config)
