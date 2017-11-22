import googlemaps
import requests
import time
import os
import json
from crawler import get_detail
import urllib
import hashlib
import json
import glob
import pickle
from clustering import clustering
from point import Point


google_decode_api_key = 'AIzaSyCeiKxOd3WF5fnL_XjcpHTaynEmfgUPRog'
facebook_api_key = 'EAACEdEose0cBAPbea2ctmI8bdlpz9fAS2X4Sf73IWroarTmjBZANYEhlsBmNXqAy8UMszuxZAwrwGYtfN2wZAqpbVpKHTzgHEB07Yci4k3nX0DZCExfYOZCMJc7ZARbQZAWCdoo92hZBmPGXKChsGBT0VewkwZAo8mE72RaJMP6vCUKIwOfH9HddtysMFyhwpmHsI5cuniGJ9qAZDZD'
google_api_key = 'AIzaSyAAdDOghckmq0YNN9lSrAG0sJLta1znuCc'
keywords = ['restaurant', 'cafe', 'bar', 'food']
maps_client = googlemaps.Client(key=google_api_key)


def priority_value(rating, n_ratings, min_ratings, mean_ratings):
	return ((n_ratings) / (n_ratings + min_ratings)) * mean_ratings + (min_ratings / (n_ratings + min_ratings)) * mean_ratings


def get_events_from_facebook(lat, lng, distance=2500, accessToken=facebook_api_key):
	payload = {
		'lat': lat,
		'lng': lng,
		'distance': distance,
		'accessToken': accessToken
	}
	event_data = requests.get(
		'http://localhost:3000/events', params=payload).json()
	return event_data['events']


def geocode_facebook_latlng(lat, lng):
	conditional_response = get_if_exists('latlng', get_hash_name(lat=lat, lng=lng))
	if not conditional_response:
		response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng={},%20{}&key={}".format(lat, lng, google_decode_api_key))
		response_json = response.json()
		response_json = response.json()['results'][0]
		try:
			data = {
				"place_id": response_json['place_id'],
				"location": {
					"lat": response_json['geometry']['location']['lat'],
					"lng": response_json['geometry']['location']['lng']
				},
				"types": response_json['types']
			}
			return store_response('latlng', get_hash_name(lat=lat, lng=lng), data)
		except KeyError:
			print(response_json["error_message"])
			return None
	else:
		return conditional_response


def get_hash_name(place=None, lat=None, lng=None):
	if place is None:
		return hashlib.md5((str(lat) + ';' + str(lng)).upper().encode('utf-8')).hexdigest()
	return hashlib.md5(place.strip().upper().encode('utf-8')).hexdigest()


def get_if_exists(folder, fname):
	if not os.path.exists(folder):
		os.mkdir(folder)
		return None
	filename = folder + '/' + str(get_hash_name(place=fname)) + ".json"
	if os.path.exists(filename):
		with open(filename) as fname:
			return json.load(fname)
	return None


def store_response(folder, fname, data):
	with open(os.path.join(folder, get_hash_name(fname) + ".json"), 'w') as wfile:
		json.dump(data, wfile, indent='\t')
	return data


def geocode_facebook_plname(place):
	conditional_response = get_if_exists('plname', place)
	if not conditional_response:
		response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(urllib.parse.quote_plus(place), google_decode_api_key))
		response_json = response.json()
		response_json = response.json()['results'][0]
		try:
			data = {
				"place_id": response_json['place_id'],
				"place": place,
				"location": {
					"lat": response_json['geometry']['location']['lat'],
					"lng": response_json['geometry']['location']['lng']
				},
				"types": response_json['types']
			}
			return store_response('plname', place, data)
		except KeyError:
			print(response_json["error_message"])
			return None
	else:
		return conditional_response


def main():
	# locality = input("Enter locality: ")
	locality = 'Indiranagar'
	itime = int(input("Enter time 0-23: "))
	iday = int(input("Enter day: "))
	placesinfo = None
	with open("places_info.pickle", 'rb') as pfile:
		placesinfo = pickle.load(pfile)
	#print(placesinfo)
	alldetails = list()
	plist = list()
	for place in placesinfo:
		popular_count = -1
		if place['populartimes']:
			print(place['populartimes'])
			day = place['populartimes'][iday]['data']
			popular_count = day[itime]
		pt = Point(place['coordinates']['lat'],place['coordinates']['lng'])
		pt.set_cpop(popular_count)
		pt.set_nreviews(place['rating_n'])
		plist.append(pt)

		# alldetails.append([Point(place['coordinates']['lat'],place['coordinates']['lng']),place['rating_n'],popular_count])
	# print(alldetails)
	cluster = clustering(plist, 5)
	flag = cluster.k_means(False)
	if flag == -1:
		print("Error")
	else:
		cluster.print_clusters(cluster.clusters)
		print("Cluster means")
		for point in cluster.means:
			print(point)
	'''



	places = maps_client.places(query=locality)
	event_list = None
	coords = places['results'][0]['geometry']['location']

	if os.path.exists("output.json"):
		with open("output.json") as infile:
			event_list = json.load(infile)

	else:
		event_list = get_events_from_facebook(lat=coords['lat'], lng=coords['lng'])
		with open("output.json", "w") as opfile:
			json.dump(event_list, opfile, indent='\t')

	print("{} events found.".format(len(event_list)))
	for event in event_list:
		print('Event: {}'.format(event['name']), end='\r')
	print()
	res_json = store_response('events', event['venue']['name'], geocode_facebook_plname(event['venue']['name']))
	for file in glob.iglob("events/*.json"):
		with open(file) as f:
			fjson = json.load(f)
			resp_json = get_place_details(list(fjson['place_id']), locality)
			with open("events/details-" + file.json, 'w') as ofile:
				json.dump(resp_json[0], ofile)

	place_id_list = get_place_ids(coords['lat'], coords['lng'], 'restaurant')
	# print(place_id_list)
	get_place_details(place_id_list, locality)
	'''

def get_place_ids_per_type(lat, lng, key_list):
	place_id_list = list()
	for key in key_list:
		place_id_list.append(get_place_ids(lat, lng, key))
	return place_id_list


def get_place_ids(lat, lng, key):
	place_id_list = list()

	if os.path.exists(str(lat) + '-' + str(lng) + '.json'):
		place_id_list = load_place_ids(lat, lng)

	count = 0
	places_nearby = maps_client.places_nearby(
		location=(lat, lng), radius=1500, keyword=key)
	for place in places_nearby['results']:
		place_id_list.append(place['place_id'])
	# print(places_nearby)
	while count < 2:
		time.sleep(2)
		places_nearby = maps_client.places_nearby(location=(
			lat, lng), radius=1500, keyword=key, page_token=places_nearby['next_page_token'])
		for place in places_nearby['results']:
			place_id_list.append(place['place_id'])
		count = count + 1
	save_place_ids(lat, lng, place_id_list)
	return list(set(place_id_list))


def load_place_ids(lat, lng):
	with open(get_hash_name(lat=lat, lng=lng) + '.json') as file:
		return json.load(file)


def save_place_ids(lat, lng, place_id_list):
	with open(get_hash_name(lat=lat, lng=lng) + '.json', 'w') as file:
		json.dump(place_id_list, file, indent='\t')
	print("Place IDs Cached")


def load_places_info():
	with open('places_info.json') as file:
		return json.load(file)


def save_places_info(places_info):
	with open('places_info.json', 'w') as file:
		json.dump(places_info, file, indent='\t')
	print("Place Info Cached")


def get_place_details(place_id_list, locality):
	places_info = list()
	if os.path.exists('places_info.json'):
		places_info = load_places_info()
	for place_id in place_id_list:
		place_info = get_detail(place_id, locality, google_api_key)
		places_info.append(place_info)
	save_places_info(places_info)
	return places_info


def get_three_places(place_id_list, locality):
	for num in range(0, 3):
		place_info = get_detail(place_id_list[num], locality, google_api_key)
		print(place_info)


if __name__ == "__main__":
	main()
