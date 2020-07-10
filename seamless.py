from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import spotipy
import pylast
import sys
import pprint
import json
from song import Song
import random
import numpy as np
import requests
import util
import operator


# set as environment variables
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# Creates a song object from Spotify song ID
def makeSongFromID(songID):

    songData = []

    trackdata = sp.track(songID)

    name = trackdata['name']
    albumName = trackdata['album']['name']
    year = trackdata['album']['release_date'][:4]
    artist = trackdata['album']['artists'][0]['name']
    a_id = trackdata['album']['artists'][0]['id']
    availableMarkets = trackdata['album']['available_markets']

    songData.append(songID)
    songData.append(name)
    songData.append(artist)
    songData.append(a_id)
    songData.append(year)
    songData.append(albumName)
    songData.append(availableMarkets)

    songObj = getSongInfo(songData)

    return songObj

# Retrieves song ID from search string
def getSongData(search_str):

    result = sp.search(search_str, limit=3)

    songID = result['tracks']['items'][0]['id']

    return songID

# Obtains audio features from each track to then compose a complete song object
def getSongInfo(songStats):

    # Simply put: try, try again
    try:

        features = sp.audio_features('spotify:track:' + songStats[0])

    except requests.exceptions.Timeout:

        features = sp.audio_features('spotify:track:' + songStats[0])

    # Cases where API does not return any data for song ID
    if features == [None]:
        tempo = 0
        loudness = 0
        danceability = 0
        energy = 0
        valence = 0
        speechiness = 0
        mode = 0
    
    else:
        tempo = features[0]['tempo']
        loudness = features[0]['loudness']
        danceability = features[0]['danceability']
        energy = features[0]['energy']
        valence = features[0]['valence']
        speechiness = features[0]['speechiness']
        mode = features[0]['mode']

    # Final song object
    genSong = Song(songStats[0], songStats[1], songStats[2], songStats[3], songStats[4], songStats[5], songStats[6], tempo, loudness, danceability, energy, valence, speechiness, mode)

    return genSong

# Retrieves related artists of the artist for the user's song
# Returns dictionary of artist IDs and names
def relatedArtists(genSong):

    util.artistDict = {}

    jsonData = sp.artist_related_artists(genSong.a_id)

    util.artistDict.update({genSong.artist: genSong.a_id})

    numArtists = len(jsonData['artists'])

    for i in range(numArtists):
        key = jsonData['artists'][i]['name']
        value = jsonData['artists'][i]['id']
        util.artistDict.update({key: value})

    return util.artistDict

# Finds albums published within the correct time frame
def artistAlbums(dictionary, genSong):

    songYear = int(genSong.year)
    songYRange1 = songYear - 3
    songYRange2 = songYear + 3

    albums = []

    for artistID in dictionary.values():

       results = sp.artist_albums(artistID, album_type='album')
       albums.extend(results['items'])
       while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])

    albumList = {}

    for album in albums:
        if album['name'] not in albumList:
            if int(album['release_date'][:4]) in range(songYRange1, songYRange2):
                if album['id'] not in util.checkedAlbums:
                    albumList.update({album['name']: album['id']})
    

    print("ALBUM NAMES: ")
    print(albumList.values())
    print("CHECKED ALBUMS: ")
    print(util.checkedAlbums)

    return albumList

# Adds songs that satisfy the requirements to the final playlist
def getTracks(albumList, genSong, limit):

    # Add original song to list
    #if genSong not in util.albumtracks:
        #util.albumtracks.append(genSong)

    # Shuffles the list of albums 
    albums = list(albumList.values())
    random.seed(datetime.now())
    random.shuffle(albums)

    # Search for songs in each album that satisfy requirements
    for value in albums:

        result = sp.album_tracks(value)
        random.shuffle(result['items'])

        for i in range(len(result['items'])):

            songID = result['items'][i]['id']

            try:
                songObj = makeSongFromID(songID)

            except requests.exceptions.Timeout:

                songObj = makeSongFromID(songID)

            tempo = int(songObj.tempo)
            loudness = float(songObj.loudness)
            danceability = float(songObj.danceability)
            energy = float(songObj.energy)
            valence = float(songObj.valence)
            speech = float(songObj.speechiness)
            #mode = songObj.mode # Unused 

            # creates of range of values that songs must be in to be added to the playlist
            tempoRange = util.calcTempoRange(int(genSong.tempo))
            loudRange = util.calcLoudnessRange(genSong.loudness)
            danceRange = util.calcDanceabilityRange(genSong.danceability)
            energyRange = util.calcEnergyRange(genSong.energy)
            valenceRange = util.calcValenceRange(genSong.valence)
            speechRange = util.calcSpeechRange(genSong.speechiness)
            #modeVal = genSong.mode # Unused 

            if (tempo in tempoRange and loudness in loudRange
                and danceability in danceRange and energy in energyRange
                and valence in valenceRange and speech in speechRange):

                if songObj in util.albumtracks:
                    print("Already in list, not adding...")
                else:
                    # measure to prevent artists from appearing in the playlist too many times
                    count = 0
                    for track in util.albumtracks:
                        if track.title == songObj.title:
                            count += 3
                        elif track.artist == songObj.artist:
                            count += 1
                            if track.album == songObj.album:
                                count += 1
                    
                    if count > 2:
                        print("Artist/Song in list thrice, not adding...")
                    else:
                        # only working with songs available in the US (for now)
                        if 'US' in songObj.availableMarkets:
                            songObj.printInfo()
                            util.albumtracks.append(songObj)
                        else:
                            continue

        # maximum amount of songs in a playlist                       
        if len(util.albumtracks) == limit:
            break

        util.checkedAlbums.append(value)
        
    
    for track in util.albumtracks:
        print(track.title)
       
# Generates a playlist from the list of song objects 
def genPlaylist(tracks):

    # Authentication to create playlist
    scope = 'playlist-modify-public'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(username='1244117742', scope=scope))

    user_id = sp.me()['id']

    tracklist = []

    for track in tracks:
        tracklist.append(track.id)
        print(track.title + " " + str(track.tempo))

    # Playlist creation on user's spotify account
    sp.user_playlist_create(user_id, 'Test 29')
    playlists = sp.user_playlists(user_id)

    playlistID = ''

    for playlist in playlists['items']:
        if playlist['name'] == 'Test 29':
            playlistID = playlist['id']
    
    # Adding tracks to newly created playlist
    sp.user_playlist_add_tracks(user_id, playlistID, tracklist)


def main():

    random.seed(datetime.now())

    limit = 10
    songData = util.albumtracks[0]
    artistsDict = relatedArtists(songData)
    validAlbums = artistAlbums(artistsDict, songData)
    getTracks(validAlbums, songData, limit)
    originSong = util.albumtracks[0]

    originSong.printInfo()

    # Takes other songs on the list, and finds songs related to them
    while len(util.albumtracks) < limit:

        songData = originSong

        while songData in util.alreadyChosenSP:
            songData = random.choice(util.albumtracks)
            
            # If there is only one song to choose from
            if len(util.albumtracks) == 1:
                genPlaylist(util.albumtracks)
                print("Sorry!!")
                exit()

        artistsDict = relatedArtists(songData)
        validAlbums = artistAlbums(artistsDict, originSong)
        getTracks(validAlbums, originSong, limit)
        util.alreadyChosenSP.append(songData)

        # All the songs on the list have been chosen already 
        if len(util.alreadyChosenSP) == len(util.albumtracks):
            print("Sorry! Couldn't find more songs")
            
            genPlaylist(util.albumtracks)
            exit()
        
    # Songs organized by tempo    
    util.albumtracks = sorted(util.albumtracks, key=operator.attrgetter("tempo"))

    genPlaylist(util.albumtracks)


if __name__ == "__main__":

    main()


