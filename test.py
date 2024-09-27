import requests
import json

print("https://api.themoviedb.org/3/movie/" + str(1108566) + "?api_key=" + "648d096ec16e3f691572593e44644d30" + "&language=en-US")
data = requests.get("https://api.themoviedb.org/3/movie/" + str(1108566) + "?api_key=" + "648d096ec16e3f691572593e44644d30" + "&language=en-US").json()
print(data.keys())