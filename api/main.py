import os, sys
import json
import util
from last import launch
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/playlist', methods=['GET', 'POST'])
def makePlaylist():
    if request.method == 'POST':
        song_info = request.get_json()
        print(song_info['search_str'])
        try:
            songs = launch(song_info['search_str'])
            #print(songs)
            print(util.albumtracks)
            songs_response = json.dumps([ob.__dict__ for ob in songs])
            return (songs_response)
        except:
            e = sys.exc_info()[0]
            print(e)
            return

@app.route('/postPlaylist', methods=['POST'])
def postPlaylist():
    if request.method == 'POST':
        userResponse = request.get_json()
        print(userResponse['ans'])
        try:
            if userResponse['ans'] == "True":
                res = launch(userResponse['ans'])
        except:
            e = sys.exc_info()[0]
            print(e)
        return str(res)


