import requests
import json

class LastApi:
    apiRoot = "http://ws.audioscrobbler.com/2.0/"
    headers = {'Content-Type': 'application/json'}

    def __init__(self, apiKey, sharedSecret):
        self.apiKey = apiKey
        self.sharedSecret = sharedSecret
    def buildUrl(self, method, params = []):
        url = self.apiRoot + "?method=" + method
        for key, value in params.items():
            url += "&" + key + "=" + value
        return url + "&api_key=" + self.apiKey + "&format=json"
    def topArtists(self, page = None):
        params = {'user': 'kaktusas86', 'period': 'overall'}
        if page is not None:
            params['page'] = str(page)
        url = self.buildUrl("user.getTopArtists", params)
        response = requests.get(url, headers = self.headers, timeout = 5)
        if response.status_code == 200:
            # Should throw except if there are no artists
            return json.loads(response.content.decode('utf-8'))['topartists']['artist']
        else:
            return None
    def artistTags(self, mbid):
        url = "?method=artist.getTopTags&mbid="+mbid+"&api_key="+self.apiKey+"&format=json"
        response = requests.get(self.apiRoot+url, headers = self.headers, timeout = 5)
        if response.status_code == 200:
            # Should throw except if there are no tags
            return json.loads(response.content.decode('utf-8'))['toptags']['tag']
        else:
            return None

