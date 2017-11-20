import googlemaps
import requests
import time
import os
import pickle
from crawler import get_detail

facebook_api_key = 'EAACEdEose0cBAIWRH9I6vlmfmAhEwOrsNpxQQscpDZBQPoDZBxIzOfrOY0NfgACC2wf4gESXTJ94Wp3bvBlCTPKqWbTIrk2jh7DBmUJLKn7I4If6pd2JfwqDcu6XlkFKRnVVnDjBryB1WkyiAY5yFLcn6Lcpyn4kRB12DbZC2LN8RzseuZCKjbQXYZB3GggUZD'
google_api_key = 'AIzaSyCpI8nDmM3-3jRegNuxX0Q_U7zus9zmRDU'
keywords = ['restaurant','cafe','bar','food']
maps_client = googlemaps.Client(key=google_api_key)

def main():
	print("Input location: ")
	locality = input()
	places = maps_client.places(query=locality)
	#print(places)
	coords = places['results'][0]['geometry']['location']
	place_id_list = get_place_ids(coords['lat'],coords['lng'],'restaurant')
	#print(place_id_list)
	get_place_details(place_id_list,locality)

def get_place_ids_per_type(lat,lng,key_list):
	place_id_list = list()
	for key in key_list:
		place_id_list.append(get_place_ids(lat,lng,key))
	return place_id_list

def get_place_ids(lat,lng,key):
	place_id_list = list()
	
	if os.path.exists(str(lat)+'-'+str(lng)+'.pickle'):
		place_id_list = load_place_ids(lat,lng)
	
	count = 0
	places_nearby = maps_client.places_nearby(location=(lat,lng),radius=1500,keyword=key)
	for place in places_nearby['results']:
		place_id_list.append(place['place_id'])
	#print(places_nearby)
	while count < 2:
		time.sleep(2)
		places_nearby = maps_client.places_nearby(location=(lat,lng),radius=1500,keyword=key,page_token=places_nearby['next_page_token'])	
		#print(places_nearby)
		for place in places_nearby['results']:
			place_id_list.append(place['place_id'])	
		count = count + 1
	save_place_ids(lat,lng,place_id_list)
	return list(set(place_id_list))

def load_place_ids(lat,lng):
	with open(str(lat)+'-'+str(lng)+'.pickle','rb') as file:
		return pickle.load(file)

def save_place_ids(lat,lng,place_id_list):
	with open(str(lat)+'-'+str(lng)+'.pickle','wb') as file:
		pickle.dump(place_id_list,file)
	print("Place IDs Cached")

def load_places_info():
	with open('places_info.pickle','rb') as file:
		return pickle.load(file)

def save_places_info(places_info):
	with open('places_info.pickle','wb') as file:
		pickle.dump(places_info,file)
	print("Place Info Cached")

def get_place_details(place_id_list,locality):
	places_info = list()
	if os.path.exists('places_info.pickle'):
		places_info = load_places_info()
	for place_id in place_id_list:
		place_info = get_detail(place_id,locality,google_api_key)
		places_info.append(place_info)
	save_places_info(places_info)
	return places_info

def get_three_places(place_id_list,locality):
	for num in range(0,3):
		place_info = get_detail(place_id_list[num],locality,google_api_key)
		print(place_info)

if __name__ == "__main__":
	main()