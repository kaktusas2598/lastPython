from lastFmApi import LastApi
from lastFmApi import LastDb
import lastFmScraper

lastApi = LastApi('keys.json')
lastDb = LastDb()

# Ideas:
# Use weekly artist or album, track charts to see trending tags
# and lookup lesser known recommendations (artist.getSimmilar)

# Tag summary:
# SELECT COUNT(a.name) as 'totalArtistCount', t.name, AVG(a.play_count) as 'avgScrobbles'
# FROM artist as a
# LEFT JOIN artist_tag as a_t ON a_t.artist_id = a.id
# LEFT JOIN tag as t ON t.id = a_t.tag_id
# WHERE a_t.count > 20
# GROUP BY t.name
# ORDER BY COUNT(a.name) DESC

def AddArtistsToDb(pages):
    for i in range(pages):
        print("Saving page {page}".format(page = (i+1)))
        topArtists = lastApi.topArtists(page = (i+1))
        lastDb.addArtists(topArtists)
def AddArtistTagsToDb():
    for i in range(10):
        for artist in lastDb.getArtists():
            print("Saving tags for {artist}...".format(artist = artist[2]))
            if artist[1]:
                topArtistTags = lastApi.artistTags(artist[2], mbid = artist[1])
                lastDb.addTags(topArtistTags)
                lastDb.addArtistTags(mbid = artist[1], tags = topArtistTags)
            else:
                topArtistTags = lastApi.artistTags(artist[2])
                lastDb.addArtistTags(artistId = artist[0], tags = topArtistTags)
def SyncArtist(artist):
    playCount = lastApi.artistInfo(name = artist)['stats']['userplaycount']
    lastDb.getArtistId(name = artist)
    # lastDb.updateArtist(artistId, playCount = playCount);

print(lastApi.artistInfo(name = "Led Zeppelin")['stats'])
