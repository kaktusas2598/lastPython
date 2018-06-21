import requests
from requests.utils import quote
import json

class LastRequest:
    apiRoot = "http://ws.audioscrobbler.com/2.0/"
    headers = {'Content-Type': 'application/json'}

    def __init__(self, apiKey):
        with open('keys.json') as f:
            keys = json.load(f)
        self.apiKey = keys['apiKey']
        self.sharedSecret = keys['sharedSecret']

    def buildUrl(self, method, params = []):
        url = self.apiRoot + "?method=" + method
        for key, value in params.items():
            if value:
                url += "&" + key + "=" + str(value)
        return url + "&api_key=" + self.apiKey + "&format=json"

    def execute(self, method, params):
        url = self.buildUrl(method, params = params)
        response = requests.get(url, headers = self.headers, timeout = 5)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return response.status_code

class LastApi:
    def __init__(self, keyFile):
        self.req = LastRequest(keyFile)

    # Get top artists for user
    def topArtists(self, page = None):
        return self.req.execute("user.getTopArtists",
                params = {'user': 'kaktusas86', 'period': 'overall', 'page' : page}
                )['topartists']['artist']

    # Get top albums for user
    def topAlbums(self, page = None):
        return self.req.execute("user.getTopAlbums",
                params = {'user': 'kaktusas86', 'period': 'overall', 'page' : page}
                )['topalbums']['album']

    # Get top tags for artist
    def artistTags(self, name = None, mbid = None):
        if name:
            name = quote(name,  safe='')
        try:
            return self.req.execute("artist.getTopTags",
                    params = {'mdib': mbid, 'artist': name})['toptags']['tag']
        except KeyError as error:
            print(error)

    # Get artist info with user count if possible
    def artistInfo(self, name = None, mbid = None):
        if name:
            name = quote(name,  safe='')
        try:
            return self.req.execute("artist.getInfo",
                    params = {'user': 'kaktusas86', 'mdib': mbid, 'artist': name}
                    )['artist']
        except KeyError as error:
            print(error)

    # Get similar artists to artist
    def getSimilar(self, name = None, mbid = None):
        if name:
            name = quote(name,  safe='')
        try:
            return self.req.execute("artist.getSimilar",
                    params = {'user': 'kaktusas86', 'mdib': mbid, 'artist': name}
                    )['similarartists']['artist']
        except KeyError as error:
            print(error)

################################################################################

class Tag:
    def __init__(self, name):
        self.name = name;

class Artist:
    def __init__(self, name , rank, playCount, url, mbid = None, tags = {}):
        self.name = name
        self.rank = rank
        self.playCount = playCount
        self.url = url
        self.mbid = mbid
        self.tags = tags
    def addTags(self, tags):
        self.tags.update(tags)
