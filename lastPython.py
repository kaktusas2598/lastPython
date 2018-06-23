from lastFmApi import LastApi
from lastDb import LastDb
import lastFmScraper
import matplotlib.pyplot as plot

lastApi = LastApi('keys.json')
lastDb = LastDb()

# Ideas:
# Use weekly artist or album, track charts to see trending tags
# and lookup lesser known recommendations (artist.getSimmilar)
# TODO:
#  Filter out uneccessary tags in api: %seen%

def AddArtistsToDb(pages):
    for i in range(pages):
        print("Saving page {page}".format(page = (i+1)))
        topArtists = lastApi.topArtists(page = (i+1))
        lastDb.addArtists(topArtists)
def AddArtistTagsToDb(pages):
    for i in range(pages):
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

while True:
    artist = input("Artist: ")
    track = input("Track: ")
    lastApi.scrobbleTrack(artist, track)

with plot.xkcd():
    tagSummary = lastDb.getTagSummary()
    plot.ylabel("Number of artists (From Top 500)")
    plot.xlabel("Total plays")
    plot.title("Genre summary (2009-2018)")
    for idx, tag in enumerate(tagSummary):
        plot.scatter(tag[3], tag[0])
        plot.annotate(tag[1], [tag[3], tag[0]], [tag[3]+2, tag[0]+1])
plot.show()
