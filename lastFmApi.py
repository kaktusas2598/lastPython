import requests
from requests.utils import quote
import json
import sqlite3

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


class LastDb:
    dbFile = "lastFm.sqlite"
    def __init__(self):
        print("Connecting to database..")
        self.dbConn = sqlite3.connect(self.dbFile)
        self.dbCursor = self.dbConn.cursor()
        print("Creating tables..")
        self.createTables()
    def __del__(self):
        print("Closing connection..")
        self.dbConn.close()
    def createTables(self):
        artistTableSql = """CREATE TABLE IF NOT EXISTS artist(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                mbid VARCHAR(255),
                                name TEXT NOT NULL UNIQUE ,
                                play_count INTEGER NOT NULL,
                                rank INTEGER NOT NULL,
                                url VARCHAR(255)
                            )"""
        self.dbCursor.execute(artistTableSql)
        tagTableSql = """CREATE TABLE IF NOT EXISTS tag(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL UNIQUE
                            )"""
        artistTagTableSql = """CREATE TABLE IF NOT EXISTS artist_tag(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                tag_id INTEGER,
                                artist_id INTEGER,
                                count INTEGER,
                                FOREIGN KEY(tag_id) REFERENCES tag(id),
                                FOREIGN KEY(artist_id) REFERENCES artist(id)
                            )"""

        self.dbCursor.execute(artistTagTableSql)
        self.dbConn.commit()
        #Create unique complex index on artist and tag, so we dont get duplicates
        artistTagIndexSql = """CREATE UNIQUE INDEX IF NOT EXISTS `artist_tag_index` ON `artist_tag` (
                                `artist_id`,
                                `tag_id`
                                );"""
        self.dbCursor.execute(artistTagIndexSql)
        self.dbConn.commit()
    def getArtists(self):
        self.dbCursor.execute("SELECT id, mbid, name FROM artist;");
        return self.dbCursor.fetchall();
    def addArtists(self, artists):
        for artist in artists:
            try:
                self.dbCursor.execute("INSERT OR IGNORE INTO artist (mbid, name, play_count, rank, url) " + \
                        "VALUES (:mbid, :name, :count, :rank, :url) " + \
                        "UPDATE artist SET play_count=:count, rank=:rank WHERE name=:namei;",
                        {"name": artist['name'], "count": artist['playcount'], "mbid": artist['mbid'],
                            "rank": artist['@attr']['rank'], "url": artist['url']})
                self.dbConn.commit()
            except sqlite3.Error as e:
                print ("Error while adding artist to db: {error}".format(error= e.args[0]))
    def addArtistTags(self, tags, mbid = None, artistId = None):
        if not artistId:
            self.dbCursor.execute("SELECT id FROM artist WHERE mbid=:mbid", {"mbid": mbid})
            artistId = self.dbCursor.fetchone()[0]
        try:
            for tag in tags:
                self.dbCursor.execute("SELECT id FROM tag WHERE name=:name", {"name": tag['name']})
                tagId = self.dbCursor.fetchone()
                if tagId is None:
                    self.addTag(tag);
                    tagId = [self.dbCursor.lastrowid]
                self.dbCursor.execute("INSERT INTO artist_tag (tag_id, artist_id, count)" + \
                        "VALUES (:tagId, :artistId, :count);",{"tagId": tagId[0], "artistId": artistId,"count": tag["count"] })
                self.dbConn.commit()
        except sqlite3.Error as e:
            print ("Error while adding artist tag: {error}".format(error= e.args[0]))
        return None
    def addTag(self, tag):
        try:
            self.dbCursor.execute("INSERT INTO tag (name) VALUES (:name);",{"name": tag['name']})
            self.dbConn.commit()
        except sqlite3.Error as e:
            print ("Error while adding tag: {error}".format(error= e.args[0]))
    def addTags(self, tags):
        for tag in tags:
            self.addTag(tag)
    def getArtistId(name):
        try:
            self.dbCursor.execute("SELECT id FROM artist WHERE name=:name", {"name": name})
            return self.dbCursor.fetchone()
        except sqlite3.Error as e:
            print ("Error while getting artist ID: {error}".format(error= e.args[0]))
    def getTagSummary(self):
        self.dbCursor.execute("SELECT COUNT(a.name) as 'totalArtistCount', " +\
                "t.name, AVG(a.play_count) as 'avgScrobbles', SUM(a.play_count) as 'totalPlays ' "+\
                "FROM artist as a " +\
                "LEFT JOIN artist_tag as a_t ON a_t.artist_id = a.id " +\
                "LEFT JOIN tag as t ON t.id = a_t.tag_id " +\
                "WHERE a_t.count > 20 and t.name != 'rock'" +\
                # and t.name LIKE '%rock%'
                "GROUP BY t.name " +\
                "ORDER BY COUNT(a.name) DESC")
        return self.dbCursor.fetchall()


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
