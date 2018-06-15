import requests
import json
import sqlite3

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
    # Get top artists for user
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
    # Get top tags for artist
    def artistTags(self, mbid):
        url = "?method=artist.getTopTags&mbid="+mbid+"&api_key="+self.apiKey+"&format=json"
        response = requests.get(self.apiRoot+url, headers = self.headers, timeout = 5)
        if response.status_code == 200:
            # Should throw except if there are no tags
            return json.loads(response.content.decode('utf-8'))['toptags']['tag']
        else:
            return None

class LastDb:
    dbFile = "lastFm.sqlite"
    def __init__(self):
        print("Connecting to database..")
        self.dbConn = sqlite3.connect(self.dbFile)
        self.dbCursor = self.dbConn.cursor()
        print("Creating tables..")
        self.createTables()
    def __del__(self):
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
    def addArtists(self, artists):
        for artist in artists:
            try:
                self.dbCursor.execute("INSERT INTO artist (mbid, name, play_count, rank, url)" + \
                        "VALUES ( :mbid, :name, :count, :rank, :url);",
                        {"name": artist['name'], "count": artist['playcount'], "mbid": artist['mbid'],
                            "rank": artist['@attr']['rank'], "url": artist['url']})
                self.dbConn.commit()
            except sqlite3.Error as e:
                print ("An error occurred: {error}".format(error= e.args[0]))
    def addArtistTags(self, mbid, tags):
        self.dbCursor.execute("SELECT id FROM artist WHERE mbid=:mbid", {"mbid": mbid})
        artistId = self.dbCursor.fetchone()[0]
        try:
            for tag in tags:
                self.dbCursor.execute("SELECT id FROM tag WHERE name=:name", {"name": tag['name']})
                tagId = self.dbCursor.fetchone()
                if not tagId:
                    self.addTag(tag);
                self.dbCursor.execute("INSERT INTO artist_tag (tag_id, artist_id, count)" + \
                        "VALUES (:tagId, :artistId, :count);",{"tagId": tagId[0], "artistId": artistId,"count": tag["count"] })
                self.dbConn.commit()
        except sqlite3.Error as e:
            print ("An error occurred: {error}".format(error= e.args[0]))
        return None
    def addTag(self, tag):
        try:
            self.dbCursor.execute("INSERT INTO tag (name) VALUES (:name);",{"name": tag['name']})
            self.dbConn.commit()
        except sqlite3.Error as e:
            print ("An error occurred: {error}".format(error= e.args[0]))
    def addTags(self, tags):
        for tag in tags:
            self.addTag(tag)
