import requests
import json
from bs4 import BeautifulSoup

class LastApi:
    apiRoot = "http://ws.audioscrobbler.com/2.0/"
    headers = {'Content-Type': 'application/json'}

    def __init__(self, apiKey, sharedSecret):
        self.apiKey = apiKey
        self.sharedSecret = sharedSecret
    def topArtists(self):
        url = "?method=user.getTopArtists&user=kaktusas86&period=overall&api_key="+self.apiKey+"&format=json"
        response = requests.get(self.apiRoot+url, headers = self.headers, timeout = 5)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None
    def artistTags(self, mbid):
        url = "?method=artist.getTopTags&mbid="+mbid+"&api_key="+self.apiKey+"&format=json"
        response = requests.get(self.apiRoot+url, headers = self.headers, timeout = 5)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

