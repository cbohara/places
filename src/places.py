import sys
import requests
import json
from geopy.geocoders import Nominatim


def get_lat_long_from_osm(location):
	"""Leverage open source OpenStreetMap API for geocoding"""
	geolocator = Nominatim(user_agent="my_app")
	response = geolocator.geocode(location)
	if response:
		return (response.latitude, response.longitude)
	else:
		raise Exception("Unable to generate latitude and longitude from location input")

def get_lat_long(lat_long, location):
	"""Get latitude and longitude for Here API search"""
	if lat_long:
		latitude, longitude = lat_long.split(',')
		return (float(latitude), float(longitude))
	elif location:
		return get_lat_long_from_osm(location)
	else:
		raise Exception("Did not provide location input")

def get_here_start_url(app_id, app_code, search, latitude, longitude):
	"""Get json data from here API and save to local file if enabled"""
	url = "https://places.cit.api.here.com/places/v1/browse?"
	if search:
		url += "&q={}".format(search)
	if latitude and longitude:
		url += "&at={},{}".format(latitude, longitude)
	url += "&app_id={}&app_code={}".format(app_id, app_code)
	return url

def get_here_json(url):
	"""Get here API json data"""
	return requests.get(url).text

def parse_address(place):
	"""Parse field contaning address data"""
	address = place["vicinity"].split("<br/>")
	if len(address) > 1:
		street = address[0]
		city, state_zip = address[1].split(",")
		state, zipcode = state_zip.split()
		return (street, city, state, zipcode)

	if len(address) == 1:
		address = address[0].split(",")
		if len(address) > 1:
			city = address[0]
			state, zipcode = address[1].split()
			return ('', city, state, zipcode)
		elif len(address) == 1:
			street = address[0]
			return (street, '', '', '')

def get_fields(place):
	"""Get line to write to output csv"""
	name = place["title"]
	category = place["category"]["id"]
	street, city, state, zipcode = parse_address(place)
	lat, lon = place["position"]
	to_write = [name, street, city, state, str(zipcode), str(lat), str(lon), category]
	return ','.join(to_write)

def read_json(search, latitude, longitude):
	"""Read in json file to avoid API call"""
	with open("json/{}.{}.{}.json".format(search, latitude, longitude), "r") as f:
		return f.readlines()

def write_json(all_json, search, latitude, longitude):
	"""Write places to csv file"""
	with open("json/{}.{}.{}.json".format(search, latitude, longitude), "w") as f:
		for json in all_json:
			f.write(json + "\n")

def write_csv(search, latitude, longitude, places):
	"""Write places to csv file"""
	with open("csv/{}.{}.{}.csv".format(search, latitude, longitude), "w") as f:
		header = 'name,street,city,state,zipcode,latitude,longitude,category'
		for place in places:
			line = get_fields(place)
			f.write(line + "\n")

def json_to_dict(json_data):
	return json.loads(json_data)

def execute(config):
	latitude, longitude = get_lat_long(config.lat_long, config.location)
	app_id = config.app_id
	app_code = config.app_code
	search = config.search

	all_json = []
	all_places = []
	if config.api_enabled:
		url = get_here_start_url(app_id, app_code, search, latitude, longitude)

		for page in range(1, config.api_calls + 1):
			json_data = get_here_json(url)
			all_json.append(json_data)
			dict_data = json_to_dict(json_data)

			if page == 1:
				url = dict_data["results"]["next"]
				all_places.extend(dict_data["results"]["items"])
			else:
				url = dict_data["next"]
				all_places.extend(dict_data["items"])

		if config.save_json:
			write_json(all_json, search, latitude, longitude)
	else:
		json = read_json(search, latitude, longitude)

	if config.save_csv:
		write_csv(search, latitude, longitude, all_places)


if __name__ == "__main__":
	import configargparse
	config_parser = configargparse.ArgParser()
	config_parser.add('-c', '--config-file', required=False, is_config_file=True, help='config file path')

	api = config_parser.add_argument_group()
	api.add('--app_id', required=True, help='here API app id')
	api.add('--app_code', required=True, help='here API app code')
	api.add('--search', help='specify search word or specific location')
	api.add('--api_enabled', default=False, help='for testing use local json file to avoid another API call', action='store_true')
	api.add('--api_calls', type=int, default=1, help='number of next pages to gather data from')

	geocode = config_parser.add_mutually_exclusive_group(required=True)
	geocode.add('--lat_long', help='specific start latitude,longitude')
	geocode.add('--location', help='location to search around - does not have to be a specific address')

	storage = config_parser.add_argument_group()
	storage.add('--save_json', default=True, help='save json from here API')
	storage.add('--save_csv', default=True, help='save csv generated from json fields')

	config = config_parser.parse_args()
	for key, value in vars(config).items():
		print('{} = {}'.format(key, value))

	execute(config)
