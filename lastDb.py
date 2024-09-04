import json
import sqlite3

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
        self.dbCursor.execute(tagTableSql)

        artistTagTableSql = """CREATE TABLE IF NOT EXISTS artist_tag(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                tag_id INTEGER,
                                artist_id INTEGER,
                                count INTEGER,
                                FOREIGN KEY(tag_id) REFERENCES tag(id),
                                FOREIGN KEY(artist_id) REFERENCES artist(id)
                            )"""
        self.dbCursor.execute(artistTagTableSql)

        trackTableSql = """CREATE TABLE IF NOT EXISTS track(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL UNIQUE,
                                artist_id INTEGER,
                                play_count INTEGER,
                                duration INTEGER,
                                FOREIGN KEY(artist_id) REFERENCES artist(id)
                            )"""
        self.dbCursor.execute(trackTableSql)

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

    def addTracks(self, tracks):
        for track in tracks:
            try:
                # First get artist_id
                artistId = self.getArtistId(track['artist']['name'])
                self.dbCursor.execute("INSERT OR IGNORE INTO track (name, artist_id, play_count, duration) " + \
                    "VALUES (:name, :artist_id, :play_count, :duration) " + \
                    "UPDATE track SET play_count=:count WHERE name=:namei;",
                                      {"name": track['name'], "count": track['playcount'],
                                       "artist_id": artistId, "duration": track['duration']})
                self.dbConn.commit()
            except sqlite3.Error as e:
                print ("Error while adding artist to db: {error}".format(error= e.args[0]))

    # Get sunmmary of tags with information of total plays, total artist count
    def getTagSummary(self):
        self.dbCursor.execute("SELECT COUNT(a.name) as 'totalArtistCount', " +\
                "t.name, AVG(a.play_count) as 'avgScrobbles', SUM(a.play_count) as 'totalPlays ' "+\
                "FROM artist as a " +\
                "LEFT JOIN artist_tag as a_t ON a_t.artist_id = a.id " +\
                "LEFT JOIN tag as t ON t.id = a_t.tag_id " +\
                "WHERE a_t.count > 20 and t.name != 'rock'" +\
                # and t.name LIKE '%rock%'
                # "and t.name NOT LIKE '%lassic rock%'" +\
                "GROUP BY t.name " +\
                "ORDER BY COUNT(a.name) DESC")
        return self.dbCursor.fetchall()

    # Instead of standard LastFM top artists with most scrobbles get actual top artists using
    # time they were listened to
    # def getTopArtistsByTimeListened(self):
        # self.dbCursor.execute("SELECT COUNT(a.name) as 'totalArtistCount', " +\
                # "t.name, AVG(a.play_count) as 'avgScrobbles', SUM(a.play_count) as 'totalPlays ' "+\
                # "FROM artist as a " +\
                # "LEFT JOIN artist_tag as a_t ON a_t.artist_id = a.id " +\
                # "LEFT JOIN tag as t ON t.id = a_t.tag_id " +\
                # "WHERE a_t.count > 20 and t.name != 'rock'" +\
                # # and t.name LIKE '%rock%'
                # # "and t.name NOT LIKE '%lassic rock%'" +\
                # "GROUP BY t.name " +\
                # "ORDER BY COUNT(a.name) DESC")
        # return self.dbCursor.fetchall()
