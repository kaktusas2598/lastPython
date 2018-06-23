import requests
from requests.utils import quote
import hashlib
from hashlib import md5
import time
import json
import webbrowser

class LastRequest:
    apiRoot = "http://ws.audioscrobbler.com/2.0/"
    headers = {'Content-Type': 'application/json'}

    def __init__(self, apiKey):
        self.sessionKey = None;
        with open('keys.json') as f:
            keys = json.load(f)
        # TODO: check if file exists
        with open('session.json') as f:
            session = json.load(f)
        self.sessionKey = session['key']
        self.apiKey = keys['apiKey']
        self.sharedSecret = keys['sharedSecret']

    def buildUrl(self, method, params = []):
        url = self.apiRoot + "?method=" + method
        for key, value in params.items():
            if value:
                url += "&" + key + "=" + str(value)
        return url + "&api_key=" + self.apiKey + "&format=json"

    # !!!! Construct your api method signatures by first ordering all the parameters
    # sent in your call ALPHABETICALLY by parameter name and concatenating them into
    # one string using a <name><value> scheme.
    def signRequest(self, method, params):
        params['method'] = method;
        params['api_key'] = self.apiKey;
        sortedParams = sorted(params.keys(), key=lambda x:x.lower())
        uncoded = ''
        for i in sortedParams:
            uncoded += i + params[i]
        unencoded += self.sharedSecret
        return md5(unencoded.encode('utf-8')).hexdigest()

    def getSessionKey(self):
        if self.sessionKey is None:
            params = {}
            methodName = "auth.getToken"
            params['api_sig'] = self.signRequest(methodName, params)
            params['token'] = self.execute(methodName, params)["token"];
            # Request user authentication from browser
            webbrowser.open('http://www.last.fm/api/auth/?api_key='+self.apiKey+'&token='+params['token'])
            input("Press grant access to app in browser and press Enter to continue...")

            methodName = "auth.getSession"
            params.pop('api_sig', None)
            params['api_sig'] = self.signRequest(methodName, params)

            self.sessionKey = self.execute(methodName, params = params)['session']['key']
        return self.sessionKey

    def execute(self, method, params, auth = None, post = None):
        if auth:
            params['sk'] = self.getSessionKey()
            params['api_sig'] = self.signRequest(method, params)
        url = self.buildUrl(method, params = params)
        if post:
            response = requests.post(url, headers = self.headers, timeout = 5)
        else:
            response = requests.get(url, headers = self.headers, timeout = 5)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            print(response.content.decode('utf-8'))
            return response.status_code

class LastApi:
    def __init__(self, keyFile):
        self.req = LastRequest(keyFile)
        with open('keys.json') as f:
            keys = json.load(f)
        self.apiKey = keys['apiKey']

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


    # Scrobble a track
    def scrobbleTrack(self, artist, track, album = None, trackNumber = None,
            albumArtist = None, duration = None):
        return self.req.execute("track.scrobble",
                params = {'artist': artist, 'track': track, 'timestamp': str(int(time.time()))}, auth = True, post = True)

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
