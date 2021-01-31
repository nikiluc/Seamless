import requests
import json
import pylast
import seamless
import pprint
import util
import random
import time
from song import Song
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Authentication for LastFM API
USER_AGENT = 'nikiluc'
API_KEY = '846582a62ca98c795f915ab5f4a9cfa1'
API_SECRET = "41e8df4034b1d349d141d618111a05f3"

username = "nikiluc"
password_hash = pylast.md5("Nikiluc1!")

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                               username=username, password_hash=password_hash)

# Gets similar tracks through last FM API
def lastfm_get(payload):
    # define headers and URL
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
    new_data = r.json()
    genSong.printInfo()

    for i in range(len(new_data['similartracks']['track'])):

        songInfo = new_data['similartracks']['track'][i]['name'] + ' ' + new_data['similartracks']['track'][i]['artist']['name']
        matchData = float(new_data['similartracks']['track'][i]['match'])

        try:
            # LastFM match value
            if matchData > 0.35:
                data2 = seamless.getSongData(songInfo)
                songObj2 = seamless.makeSongFromID(data2)
                util.artistDict.update(({songObj2.artist: songObj2.a_id}))
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

    for track in valid:
        print("TRACK IN: " + track.title)
    
    # Songs that satisfy the requirements
    reqValid = [song for song in valid if int(song.tempo) in tempoRange
    and float(song.danceability) in danceabilityRange
    and float(song.energy) in energyRange
    and float(song.popularity) in popRange
    and int(song.year) in yearRange]

    # Songs that at least match the tempo (last resort)
    util.tempotracks = [song for song in valid if int(song.tempo) in tempoRange]

    for track in reqValid:
        if track in util.albumtracks:
            print("TRACK IN: " + track.title)
        if len(util.albumtracks) < 10:
            util.albumtracks.append(track)
    

    print([song.title for song in util.albumtracks])

# Uses search string to find similar songs 
def launch(search_str):

    #Authentication to create playlist
    scope = 'playlist-modify-public'
    spUser = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    user_id = spUser.me()['id']

    if (search_str == "True"):
        seamless.genPlaylist(util.albumtracks, util.albumtracks[0].title, spUser, user_id)
        return True

    # initialization of global variables
    util.init()

    # playlist length
    limit = util.limit

    # creation of song object
    data = seamless.getSongData(search_str)
    songObj = seamless.makeSongFromID(data)

    util.year = songObj.year

    util.albumtracks.append(songObj)
    validTracks(songObj, songObj)

    util.alreadyChosenFM.append(songObj)

    print("AMOUNT OF TRACKS: ")
    print(len(util.albumtracks))

    # finds similar songs of tracks that have already satisfied the requirements
    while len(util.albumtracks) < limit:

        songData = random.sample(util.albumtracks, 1)[0]

        while songData in util.alreadyChosenFM:
            songData = random.sample(util.albumtracks, 1)[0]
            if len(util.albumtracks) == len(util.alreadyChosenFM):
               seamless.main(spUser, user_id)
               limit = len(util.albumtracks)
               break

        if len(util.albumtracks) < limit:
            validTracks(songData, songObj)
            util.alreadyChosenFM.append(songData)


    for track in util.albumtracks:
        print(track.title)
    
    songsChosen = util.albumtracks

    return songsChosen



if __name__ == "__main__":

    random.seed()

    launch(search_str="starving zedd")

    



