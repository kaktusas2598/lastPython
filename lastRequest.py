import requests
from requests.utils import quote
import hashlib
from hashlib import md5
import webbrowser
import os.path
import json

class LastRequest:
    apiRoot = "http://ws.audioscrobbler.com/2.0/"
    headers = {'Content-Type': 'application/json'}

    def __init__(self):
        self.sessionKey = None;
        with open('keys.json') as f:
            keys = json.load(f)
        # TODO: check if file exists
        if os.path.exists('session.json'):
            with open('session.json') as f:
                session = json.load(f)
            self.sessionKey = session['key']
        with open('keys.json') as f:
            keys = json.load(f)
        self.apiKey = keys['apiKey']
        self.sharedSecret = keys['sharedSecret']

    def buildUrl(self, method, params = []):
        url = self.apiRoot + "?method=" + method
        for key, value in params.items():
            if value:
                url += "&" + key + "=" + str(value)
        return url + "&api_key=" + self.apiKey + "&format=json"

    # !!!! Construct your api method signatures by first ordering all the parameters
    # sent in your call ALPHABETICALLY by parameter name and concatenating them into
    # one string using a <name><value> scheme.
    def signRequest(self, method, params):
        params['method'] = method;
        params['api_key'] = self.apiKey;
        sortedParams = sorted(params.keys(), key=lambda x:x.lower())
        unencoded = ''
        for i in sortedParams:
            unencoded += i + params[i]
        unencoded += self.sharedSecret
        return md5(unencoded.encode('utf-8')).hexdigest()

    def getSessionKey(self):
        if self.sessionKey is None:
            params = {}
            methodName = "auth.getToken"
            params['api_sig'] = self.signRequest(methodName, params)
            params['token'] = self.execute(methodName, params)["token"];
            # Request user authentication from browser
            webbrowser.open('http://www.last.fm/api/auth/?api_key='+self.apiKey+'&token='+params['token'])
            input("Press grant access to app in browser and press Enter to continue...")

            methodName = "auth.getSession"
            params.pop('api_sig', None)
            params['api_sig'] = self.signRequest(methodName, params)

            self.sessionKey = self.execute(methodName, params = params)['session']['key']
            with open('session.json', 'w') as fp:
                json.dump({'key': self.sessionKey}, fp)
        return self.sessionKey

    def execute(self, method, params, auth = None, post = None):
        if auth:
            params['sk'] = self.getSessionKey()
            params['api_sig'] = self.signRequest(method, params)
        url = self.buildUrl(method, params = params)
        if post:
            response = requests.post(url, headers = self.headers, timeout = 5)
        else:
            response = requests.get(url, headers = self.headers, timeout = 5)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            print(response.content.decode('utf-8'))
            return response.status_code
