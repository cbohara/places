import sys
import requests
import json
from geopy.geocoders import Nominatim

def get_query(neighborhood, city, state, country):
	"""Piece together location options for a location query"""
	all_args = [neighborhood, city, state, country]
	valid_args = [arg for arg in all_args if arg is not None]
	if len(valid_args) > 1:
		return " ".join(valid_args)
	elif len(valid_args) == 1:
		return valid_args[0]
	else:
		raise Exception("No location input provided")

def get_lat_long_from_osm(query):
	"""Leverage open source OpenStreetMap API for geocoding"""
	geolocator = Nominatim(user_agent="my_app")
	response = geolocator.geocode(query)
	if response:
		return (response.latitude, response.longitude)
	else:
		raise Exception("Unable to generate latitude and longitude from location input")

def get_lat_long(latitude, longitude, location, neighborhood, city, state, country):
	"""Get latitude and longitude for Here API search"""
	if latitude and longitude:
		return (float(latitude), float(longitude))
	else:
		if location:
			query = location
		else:
			query = get_query(neighborhood, city, state, country)
		return get_lat_long_from_osm(query)

def write_json(json_data, search, latitude, longitude):
	"""Write places to csv file"""
	with open("json/{}.{}.{}.json".format(search, latitude, longitude), "w") as f:
		f.write(json_data)

def get_here_api_data(app_id, app_code, search, latitude, longitude, config):
	"""Get json data from here API and save to local file if enabled"""
	url = "https://places.cit.api.here.com/places/v1/browse?"
	url += "&q={}".format(search)
	url += "&at={},{}".format(latitude, longitude)
	url += "&app_id={}&app_code={}".format(config.app_id, config.app_code)
	json_data = requests.get(url).text

	if config.save_json:
		write_json(json_data, search, latitude, longitude)
	return json_data

def get_places(json_data):
	"""Get places from here API json data"""
	dict_data = json.loads(json_data)
	return dict_data["results"]["items"]

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
		return f.read()

def write_csv(search, latitude, longitude, places):
	"""Write places to csv file"""
	with open("csv/{}.{}.{}.csv".format(search, latitude, longitude), "w") as f:
		header = 'name,street,city,state,zipcode,latitude,longitude,category'
		for place in places:
			line = get_fields(place)
			f.write(line+"\n")

def execute(config):
	latitude, longitude = get_lat_long(config.latitude, config.longitude, config.location, config.neighborhood, config.city, config.state, config.country)
	app_id = config.app_id
	app_code = config.app_code
	search = config.search

	if config.api_enabled:
		places = get_places(get_here_api_data(app_id, app_code, search, latitude, longitude, config))
	else:
		places = get_places(read_json(search, latitude, longitude))

	if config.save_csv:
		write_csv(search, latitude, longitude, places)


if __name__ == "__main__":
	import configargparse
	config_parser = configargparse.ArgParser()
	config_parser.add('-c', '--config-file', required=False, is_config_file=True, help='config file path')

	api = config_parser.add_argument_group()
	api.add('--app_id', required=True, help='here API app id')
	api.add('--app_code', required=True, help='here API app code')
	api.add('--search', help='specify search word or specific location')
	api.add('--api_enabled', default=False, help='for testing use local json file to avoid another API call', action='store_true')

	geocode = config_parser.add_argument_group()
	geocode.add('--latitude', help='specific start latitude')
	geocode.add('--longitude', help='specific start longitude')
	geocode.add('--location', help='location to search around - does not have to be a specific address')
	geocode.add('--neighborhood', help='neighborhood to search within')
	geocode.add('--city', help='city to search within')
	geocode.add('--state', help='state to search within')
	geocode.add('--country', help='country to search within')

	storage = config_parser.add_argument_group()
	storage.add('--save_json', default=True, help='save json from here API')
	storage.add('--save_csv', default=True, help='save csv generated from json fields')

	config = config_parser.parse_args()
	for key, value in vars(config).items():
		print('{} = {}'.format(key, value))

	execute(config)
