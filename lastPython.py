from lastFmApi import LastApi
from lastDb import LastDb
import lastFmScraper
import argparse
import sys
import matplotlib.pyplot as plot

lastApi = LastApi()
lastDb = LastDb()

# Ideas:
# Use weekly artist or album, track charts to see trending tags
# and lookup lesser known recommendations (artist.getSimmilar)
# TODO:
#  Filter out uneccessary tags in api: %seen%
class LastPython:

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.subparsers = self.parser.add_subparsers()

        self.scrobbleParser = self.subparsers.add_parser('scrobble')
        self.scrobbleParser.add_argument("-a", "--artist", required=True,
                help="Name of the artist to scrobble")
        self.scrobbleParser.add_argument("-al", "--album", required=False,
                help="Name of the album to scrobble")
        self.scrobbleParser.add_argument("-t", "--track", required=True,
                help="Name of the track to scrobble")
        self.scrobbleParser.set_defaults(func=self.scrobble)
        args = self.parser.parse_args()

        args.func(args)

    def scrobble(self, args):
        lastApi.scrobbleTrack(args.artist, args.track)

    def nowPlaying(self, args):
        lastApi.updateNowPlaying(args.artist, args.track)

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

last = LastPython()

print("Welcome to lastPython!")
print("Choose what you would like to do:")
print("1. Update now playing")
print("2. Scrobble a track")
print("3. Scrobble an album")
while True:
    choise = input("# ")
    if choise == '1':
        artist = input("Artist: ")
        track = input("Track: ")
        lastApi.updateNowPlaying(artist, track)
    elif choise == '2':
        artist = input("Artist: ")
        track = input("Track: ")
        lastApi.scrobbleTrack(artist, track)
    elif choise == '3':
        artist = input("Artist: ")
        album = input("Album: ")
        lastApi.scrobbleAlbum(artist, album)
    else:
        print("Not a valid choise!")

with plot.xkcd():
    tagSummary = lastDb.getTagSummary()
    plot.ylabel("Number of artists (From Top 500)")
    plot.xlabel("Total plays")
    plot.title("Genre summary (2009-2018)")
    for idx, tag in enumerate(tagSummary):
        plot.scatter(tag[3], tag[0])
        plot.annotate(tag[1], [tag[3], tag[0]], [tag[3]+2, tag[0]+1])
plot.show()
