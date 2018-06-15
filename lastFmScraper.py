import re
import requests
import json
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import sqlite3

# Web scraping details
lastFmUrl = "https://www.last.fm"
topArtistsUrl = "/user/kaktusas86/library/artists?date_preset=ALL_TIME&page=1"
headers = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}

def fetchUrl(url, headers):
    response =  requests.get(url, timeout=60, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')
def fetchTopArtistsWithSoup():
    topArtistsSoup = fetchUrl(url = (lastFmUrl + topArtistsUrl), headers = headers)
    topArtistsHtml = topArtistsSoup.find(id="top-artists-section");
    # Loop through table rows reading basiuc info about artist
    for artistInfo in topArtistsHtml.find_all('tr'):
        try:
            #Parse basic info: rank, title and scrobble count
            rank = artistInfo.find('td', class_="chartlist-index");
            rank = " ".join(rank.string.split())
            name = artistInfo.find('td', class_="chartlist-name");
            href = name.find('a', class_="link-block-target").get('href');
            name = " ".join(name.text.split())
            scrobbles = artistInfo.find('td', class_="chartlist-countbar")
            scrobbles = " ".join(scrobbles.text.split())
            scrobblesMatch = re.match(r"(\d*\,?\d+)", scrobbles)
            print(rank + ": " + name + " (" + scrobblesMatch.group() + ")\n")
            # Fetch tags
            artistSoup = fetchUrl(url = (lastFmUrl + href), headers = headers)
            artistTags = artistSoup.find("ul", class_="tags-list")
            for tag in artistTags.find_all("li", class_="tag"):
                print(tag.text.strip() + ", ")
            print("\n")
        except AttributeError as error:
            continue
class LastApi:
    apiKey = "c9ed7d90823350da12b8eb9fda41c128"
    sharedSecret = "71b5230c49a48d0b138ad3daa283ce60"
    apiRoot = "http://ws.audioscrobbler.com/2.0/"
    headers = {'Content-Type': 'application/json'}

    def topArtists(self):
        url = "?method=user.getTopArtists&user=kaktusas86&period=overall&api_key="+self.apiKey+"&format=json"
        response = requests.get(self.apiRoot+url, headers = self.headers, timeout = 5)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None
    def artistTags(self, mbid):
        url = "?method=artist.getTopTags&mbid="+mbid+"&api_key="+self.apiKey+"&format=json"
        response = requests.get(self.apiRoot+url, headers = self.headers, timeout = 5)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None



lastFmApi = LastApi()
topArtists= lastFmApi.topArtists()
for artist in topArtists['topartists']['artist']:
    # print(json.dumps(artist['@attr']))
    print(artist['@attr']['rank'] + ": " + artist['name'] + " (" + artist['playcount'] + ")\n")
    tags = lastFmApi.artistTags(artist['mbid'])
    for tag in tags['toptags']['tag']:
        print(tag['name'] + " ")
    print("\n")
# dbConn = sqlite3.connect("lastFm.sqlite")


