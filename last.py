import requests
import json
import pylast
import seamless
import pprint
import util
import random
import concurrent.futures
from song import Song
from datetime import datetime

# Authentication for LastFM API
USER_AGENT = 'username'
API_KEY = 'apiKey'
API_SECRET = 'apiSecret'

username = "username"
password_hash = pylast.md5("password")

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
    energyRange = util.calcEnergyRange(float(genSong.energy))
    danceabilityRange = util.calcDanceabilityRange(float(genSong.danceability))
    valenceRange = util.calcValenceRange(float(genSong.valence))
    speechRange = util.calcSpeechRange(float(genSong.speechiness))
    yearRange = util.calcYearRange(int(genSong.year))
    
    # Songs that satisfy the requirements
    tempoValid = [song for song in valid if int(song.tempo) in tempoRange
    and float(song.energy) in energyRange
    and float(song.danceability) in danceabilityRange
    and float(song.valence) in valenceRange
    and float(song.speechiness) in speechRange
    and float(song.loudness) in loudnessRange
    and int(song.year) in yearRange]


    for track in tempoValid:
        if track in util.albumtracks:
            print("TRACK IN: " + track.title)
        else:
            if len(util.albumtracks) < 10:
                util.albumtracks.append(track)
    

    print([song.title for song in util.albumtracks])

# Uses search string to find similar songs 
def launch(search_str):

    limit = 10

    # initialization of global variables
    util.init()

    # creation of song object
    data = seamless.getSongData(search_str)
    songObj = seamless.makeSongFromID(data)

    util.albumtracks.append(songObj)
    validTracks(songObj, songObj)

    util.alreadyChosenFM.append(songObj)

    # finds similar songs of tracks that have already satisfied the reuqirements
    while len(util.albumtracks) < limit:

        songData = random.sample(util.albumtracks, 1)[0]

        while songData in util.alreadyChosenFM:
            songData = random.sample(util.albumtracks, 1)[0]
            if len(util.albumtracks) == len(util.alreadyChosenFM):
               seamless.main()
               exit()

        validTracks(songData, songObj)
        util.alreadyChosenFM.append(songData)


    for track in util.albumtracks:
        print(track.title)



if __name__ == "__main__":

    random.seed(datetime.now())

    launch("starving zedd")
    seamless.main()
    

    



