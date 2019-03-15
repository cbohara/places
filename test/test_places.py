import pytest
from src import places

def test_get_lat_long_from_osm():
	location = "Pacific Beach San Diego CA USA"
	latitude, longitude = places.get_lat_long_from_osm(location)
	assert latitude == 32.7978268
	assert longitude == -117.2403183

def test_get_lat_long_from_osm_neighborhood_only():
	location = "Pacific Beach"
	latitude, longitude = places.get_lat_long_from_osm(location)
	assert latitude == 32.7978268
	assert longitude == -117.2403183

def test_get_lat_long_from_osm_city_only():
	location = "San Diego"
	latitude, longitude = places.get_lat_long_from_osm(location)
	assert latitude == 32.7174209
	assert longitude == -117.1627714

def test_get_lat_long_from_lat_long_arg():
	lat_long = "32.8242404,-117.389167"
	latitude, longitude = places.get_lat_long(lat_long, None)
	assert latitude == 32.8242404
	assert longitude == -117.389167

def test_get_lat_long_from_location():
	location = "Pacific Beach San Diego"
	latitude, longitude = places.get_lat_long(None, location)
	assert latitude == 32.7978268
	assert longitude == -117.2403183

def test_get_lat_long_missing_all_input():
	with pytest.raises(Exception):
		places.get_lat_long(None, None)
