from lastFmApi import LastApi
import sqlite3
import lastFmScraper

lastApi = LastApi(apiKey = "c9ed7d90823350da12b8eb9fda41c128", sharedSecret = "71b5230c49a48d0b138ad3daa283ce60")
topArtists= lastApi.topArtists(page = 2)
for artist in topArtists:
    # print(json.dumps(artist['@attr']))
    print(artist['@attr']['rank'] + ": " + artist['name'] + " (" + artist['playcount'] + ")\n")
    tags = lastApi.artistTags(artist['mbid'])
    for tag in tags:
        print(tag['name'] + " ")
    print("\n")

# dbConn = sqlite3.connect("lastFm.sqlite")
# dbC = dbConn.cursor()
# createTableSql = """CREATE TABLE IF NOT EXISTS artist(
    # id INTEGER PRIMARY KEY AUTOINCREMENT,
    # name TEXT,
    # play_count INTEGER,
    # mbid VARCHAR(255),
    # url mbid VARCHAR(255)
    # )"""
# dbC.execute(createTableSql)
# Committing changes and closing the connection to the database file
# dbConn.commit()
# dbConn.close()

