import pytest
from src import places

def test_get_query():
	query = places.get_query("Pacific Beach", "San Diego", "CA", "USA")
	assert query == "Pacific Beach San Diego CA USA"

def test_get_query_with_None_values():
	query = places.get_query(None, "San Diego", "CA", None)
	assert query == "San Diego CA"

def test_get_lat_long_from_osm():
	query = "Pacific Beach San Diego CA USA"
	latitude, longitude = places.get_lat_long_from_osm(query)
	assert latitude == 32.7978268
	assert longitude == -117.2403183

def test_get_lat_long_from_osm_neighborhood_only():
	query = "Pacific Beach"
	latitude, longitude = places.get_lat_long_from_osm(query)
	assert latitude == 32.7978268
	assert longitude == -117.2403183

def test_get_lat_long_from_osm_city_only():
	query = "San Diego"
	latitude, longitude = places.get_lat_long_from_osm(query)
	assert latitude == 32.7174209
	assert longitude == -117.1627714

def test_get_lat_long_from_lat_long_arg():
	latitude = "32.8242404"
	longitude = "-117.389167"
	latitude, longitude = places.get_lat_long(latitude, longitude, None, None, None, None, None)
	assert latitude == 32.8242404
	assert longitude == -117.389167

def test_get_lat_long_from_location():
	location = "Pacific Beach San Diego"
	latitude, longitude = places.get_lat_long(None, None, location, None, None, None, None)
	assert latitude == 32.7978268
	assert longitude == -117.2403183

def test_get_lat_long_location_overrides_other_args():
	latitude, longitude = places.get_lat_long(None, None, "San Diego", "Los Angeles", None, None, None)
	assert latitude == 32.7174209
	assert longitude == -117.1627714

def test_get_lat_long_uses_other_args():
	latitude, longitude = places.get_lat_long(None, None, None, None, "San Diego", "CA", None)
	assert latitude == 32.7174209
	assert longitude == -117.1627714
