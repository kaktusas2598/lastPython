from lastRequest import LastRequest
import time
import json

class LastApi:
    def __init__(self):
        self.req = LastRequest()

    # Get top artists for user
    def topArtists(self, period = 'overall', page = None):
        return self.req.execute("user.getTopArtists",
                params = {'user': 'kaktusas86', 'period': period, 'page' : page}
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

    # Get album info with tracks in it and user play count if possible
    def albumInfo(self, artist, album):
        try:
            return self.req.execute("album.getInfo",
                    params = {'user': 'kaktusas86', 'artist': artist, 'album': album}
                    )['album']
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

    # Scrobble a track or multiple tracks from same artist
    def scrobbleTrack(self, artist, track, album = None, trackNumber = None,
            albumArtist = None, duration = None):
        timestamp = str(int(time.time()))
        params = {}
        if type(track) is set or type(track) is list:
            for i, t in enumerate(track):
                params['artist['+str(i)+']'] = artist
                params['track['+str(i)+']'] = t
                params['timestamp['+str(i)+']'] = timestamp
        else:
            params = {'artist': artist, 'track': track, 'timestamp': timestamp}
        return self.req.execute("track.scrobble", params = params, auth = True, post = True)

    # Scrobble whole album
    # TODO: Implement scrobbling specific side for records
    def scrobbleAlbum(self, artist, album, side = None):
        tracks = self.albumInfo(artist,album)['tracks']
        trackList = []
        for track in tracks['track']:
            trackList.append(track['name'])
        return self.scrobbleTrack(artist, trackList)

    # Notify last fm of what user is playing now
    def updateNowPlaying(self, artist, track, album = None, trackNumber = None,
            albumArtist = None, duration = None):
        return self.req.execute("track.updateNowPlaying",
                params = {'artist': artist, 'track': track}, auth = True, post = True)


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
