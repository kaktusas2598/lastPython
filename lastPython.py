from lastFmApi import LastApi
from lastFmApi import LastDb
import lastFmScraper
import matplotlib.pyplot as plot

lastApi = LastApi('keys.json')
lastDb = LastDb()

# Ideas:
# Use weekly artist or album, track charts to see trending tags
# and lookup lesser known recommendations (artist.getSimmilar)

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

with plot.xkcd():
    tagSummary = lastDb.getTagSummary()
    plot.xlabel("Number of artists (From Top 500)")
    plot.ylabel("Total plays")
    plot.title("Genre summary (2009-2018)")
    for idx, tag in enumerate(tagSummary):
        plot.scatter(tag[0], tag[3])
        plot.annotate(tag[1], [tag[0], tag[3]], [tag[0]+2, tag[3]+1])
plot.show()
