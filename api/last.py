import os
from os.path import join, dirname
import uuid
import requests
import json
import pylast
import seamless
import pprint
import util
import random
import time
from dotenv import load_dotenv
from song import Song
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth

dp = join(dirname(__file__), '.env')
load_dotenv(dotenv_path=dp)

# Authentication for LastFM API
USER_AGENT = os.getenv('USER_AGENT')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

username = os.getenv('username')
password = os.getenv('password')
password_hash = pylast.md5(password)



# Gets similar tracks through last FM API


def lastfm_get(payload):
    # define headers and URL
    print(API_KEY, "KEY")
    print(USER_AGENT, "KEY")
    headers = {'user-agent': USER_AGENT}
    url = 'http://ws.audioscrobbler.com/2.0/'

    # Add API key and format to the payload
    payload['method'] = 'track.getSimilar'
    payload['api_key'] = API_KEY
    payload['format'] = 'json'

    response = requests.get(url, headers=headers, params=payload)
    return response

# Choosing tracks that satisfy the requiremnts


def validTracks(genSong, songObj):

    valid = []

    r = lastfm_get({'artist': songObj.artist, 'track': songObj.title})
    util.artistDict.update(({songObj.artist: songObj.a_id}))
    print("HEY2")
    new_data = r.json()
    genSong.printInfo()
    print(new_data)

    for i in range(len(new_data['similartracks']['track'])):

        songInfo = new_data['similartracks']['track'][i]['name'] + \
            ' ' + new_data['similartracks']['track'][i]['artist']['name']
        matchData = float(new_data['similartracks']['track'][i]['match'])


        try:
            # LastFM match value
            if matchData > 0.6:
                data2 = seamless.getSongData(songInfo)
                songObj2 = seamless.makeSongFromID(data2)
                songObj2.printInfo()
                if songObj2 not in util.albumtracks:
                    valid.append(songObj2)
            else:
                pass

        except:
            pass

    loudnessRange = util.calcLoudnessRange(float(genSong.loudness))
    tempoRange = util.calcTempoRange(int(genSong.tempo))
    popRange = util.calcPopularityRange(float(genSong.popularity))
    energyRange = util.calcEnergyRange(float(genSong.energy))
    danceabilityRange = util.calcDanceabilityRange(float(genSong.danceability))
    valenceRange = util.calcValenceRange(float(genSong.valence))
    speechRange = util.calcSpeechRange(float(genSong.speechiness))
    yearRange = util.calcYearRange(int(util.year))

    # Songs that satisfy the requirements
    reqValid = [song for song in valid if int(song.tempo) in tempoRange
                and float(song.energy) in energyRange
                and int(song.year) in yearRange]
    

    # Songs that at least match the tempo (last resort)
    util.tempotracks = [
        song for song in valid if int(song.tempo) in tempoRange]

    for track in reqValid:
        if track in util.albumtracks:
            print("TRACK IN: " + track.title)
        elif len(util.albumtracks) < util.limit:
            util.albumtracks.append(track)

    print([song.title for song in util.albumtracks])

# Uses search string to find similar songs
def launch(search_str, auth=None, user_id=None):

    #Authentication only occurs when user adds playlist
    if (search_str == "True"):
        spUser = auth
        user_id = spUser.me()['id']
        seamless.genPlaylist(
            util.albumtracks, util.albumtracks[0].title, util.albumtracks[0].artist, spUser, user_id)
        return True

    # initialization of global variables
    util.init()

    # creation of song object
    songObj = seamless.makeSongFromID(search_str)
    util.year = songObj.year
    util.albumtracks.append(songObj)
    validTracks(songObj, songObj)

    util.alreadyChosenFM.append(songObj)
    print("AMOUNT OF TRACKS: ")
    print(len(util.albumtracks))

    # finds similar songs of tracks that have already satisfied the requirements
    while len(util.albumtracks) < util.limit:

        songData = random.sample(util.albumtracks, 1)[0]

        while songData in util.alreadyChosenFM:
            
            songData = random.sample(util.albumtracks, 1)[0]
            if len(util.albumtracks) == len(util.alreadyChosenFM):
                seamless.main()
                break

        if len(util.albumtracks) < util.limit:
            validTracks(songData, songObj)
            seamless.recommendedTracks(songData)
            util.alreadyChosenFM.append(songData)

    for track in util.albumtracks:
        print(track.title)

    songsChosen = util.albumtracks
    return songsChosen


if __name__ == "__main__":
    launch(search_str="starving zedd")
