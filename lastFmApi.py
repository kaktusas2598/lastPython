import requests
import json
from bs4 import BeautifulSoup

class LastApi:
    apiKey = "c9ed7d90823350da12b8eb9fda41c128"
    sharedSecret = "71b5230c49a48d0b138ad3daa283ce60"
    apiRoot = "http://ws.audioscrobbler.com/2.0/"
    headers = {'Content-Type': 'application/json'}

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

