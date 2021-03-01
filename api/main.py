import os, sys
from os.path import join, dirname
import json
import util
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from last import launch
from flask import Flask, request, session, redirect
from flask_cors import CORS
from flask_session import Session
import uuid

app = Flask(__name__, static_folder="../build", static_url_path="")
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
CORS(app)
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')


@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/isSignedIn', methods=['POST'])
def isSignedIn():
    if not session.get('uuid'):
        return json.dumps(False)
    else:
        return json.dumps(True)

@app.route('/api/signOut', methods=['POST'])
def signOut():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')

@app.route('/api/playlist', methods=['POST'])
def makePlaylist():
    if request.method == 'POST':
        song_info = request.get_json()
        try:
            songs = launch(song_info['search_str'])
            songs_response = json.dumps([ob.__dict__ for ob in songs])
            return (songs_response)
        except:
            e = sys.exc_info()[0]
            print(e)
            return

@app.route('/api/postPlaylist', methods=['POST'])
def postPlaylist():

    res1 = request.get_json()
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())
    
    scope = 'playlist-modify-public'
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,
                                                cache_path=session_cache_path(), 
                                                show_dialog=True, redirect_uri=res1[2])
    
    if not auth_manager.get_cached_token():
        auth_manager.get_access_token(res1[1])
    
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    if request.method == 'POST':
        try:
            if res1[0] == "True":
                res = launch("True", spotify)
        except:
            e = sys.exc_info()[0]
            print(e)
        return str(res)


if __name__== '__main__':
    app.run()
