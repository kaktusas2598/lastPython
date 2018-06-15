from lastFmApi import LastApi
from lastFmApi import LastDb
import lastFmScraper

lastApi = LastApi(apiKey = "c9ed7d90823350da12b8eb9fda41c128", sharedSecret = "71b5230c49a48d0b138ad3daa283ce60")
lastDb = LastDb()

for i in range(10):
    print("Saving page {page}".format(page = (i+1)))
    topArtists = lastApi.topArtists(page = (i+1))
    lastDb.saveArtists(topArtists)
