import googlemaps
import populartimes

api_key = 'AIzaSyAAdDOghckmq0YNN9lSrAG0sJLta1znuCc'
client = googlemaps.Client(key=api_key)

loc = (12.980016, 77.640701)
#places = client.places(query='restaurant',location=(40.7589,-73.9851))

data = populartimes.get(api_key,['restaurant'],(12.980016, 77.640701), (12.962483, 77.641551),radius=1)

print(data)
#for result in places['results']:
#	print(result)