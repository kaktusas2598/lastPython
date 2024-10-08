from lastFmApi import LastApi
from lastDb import LastDb
import lastFmScraper
import argparse
import sys
import matplotlib.pyplot as plot

lastApi = LastApi()
lastDb = LastDb()
# TODO: Experiment to approximate top artists based on listening time

# Scan top 5000 tracks and save their information in DB for analysing
for i in range(1, 100):
    print(f'Syncing top tracks to db.. {i}% done');
    tracks = lastApi.topTracks(i)
    for track in tracks:
        # print(track['name'] + ' (' + track['artist']['name'] + '): ' + track['playcount'])
        # Get track duration in ms
        trackInfo = lastApi.trackInfo(track['artist']['name'], track['name'])
        track['duration'] = 0
        if trackInfo:
            if 'duration' in trackInfo:
                track['duration'] = int(trackInfo['duration'])
    lastDb.addTracks(tracks)

# for artist in lastApi.topArtists():

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
        self.scrobbleParser.add_argument("-a", "--artist", required=True, nargs='+',
                help="Name of the artist to scrobble")
        self.scrobbleParser.add_argument("-al", "--album", required=False,
                help="Name of the album to scrobble")
        self.scrobbleParser.add_argument("-t", "--track", required=True, nargs='+',
                help="Name of the track to scrobble")
        self.scrobbleParser.set_defaults(func=self.scrobble)
        args = self.parser.parse_args()

        try:
            args.func(args)
        except AttributeError:
            print('No arguments provided.')

    def scrobble(self, args):
        lastApi.scrobbleTrack(' '.join(args.artist), ' '.join(args.track))

    def nowPlaying(self, args):
        lastApi.updateNowPlaying(' '.join(args.artist), ' '.join(args.track))

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
def ShowTagSummary():
    with plot.xkcd():
        tagSummary = lastDb.getTagSummary()
        # Set plot size (in inches) and dpi
        plot.figure(figsize=(19, 12), dpi=plot.rcParams['figure.dpi'])
        plot.ylabel("Number of artists (From Top 500)")
        plot.xlabel("Total plays")
        plot.title("Genre summary (2009-Now)")
        for idx, tag in enumerate(tagSummary):
            plot.scatter(tag[3], tag[0])
            plot.annotate(tag[1], [tag[3], tag[0]], [tag[3]+2, tag[0]+1])
    plot.show()

last = LastPython()

print("Welcome to lastPython!")
print("Choose what you would like to do (press q to quit):")
print("1. Update now playing")
print("2. Scrobble a track")
print("3. Scrobble an album")
print("4. Display tag summary chart")
print("5. Artists charts")
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
    elif choise == '4':
        ShowTagSummary()
    elif choise == '5':
        topArtists = []
        print('Top 100 Artists of all time\n')
        for i in range(1, 3):
            topArtists += lastApi.topArtists(page = i)
        for artist in topArtists:
            print(artist['@attr']['rank'] + '. ' +artist['name']
                      + '(' + artist['playcount'] + ' listens)')
        print('\nTop 50 Artists of last week\n')
        for artist in lastApi.topArtists(period = '7day'):
            print(artist['@attr']['rank'] + '. ' +artist['name']
                      + '(' + artist['playcount'] + ' listens)')
    elif choise == 'q':
        break
    else:
        print("Not a valid choise!")

