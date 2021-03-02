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
import logging


# set as environment variables
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

logger = logging.getLogger('examples.artist_recommendations')
logging.basicConfig(level='INFO')

# Creates a song object from Spotify song ID
def makeSongFromID(songID):

    songData = []

    trackdata = sp.track(songID)

    name = trackdata['name']
    albumName = trackdata['album']['name']
    year = trackdata['album']['release_date'][:4]
    artist = trackdata['artists'][0]['name']
    a_id = trackdata['artists'][0]['id']
    popularity = trackdata['popularity']
    availableMarkets = trackdata['album']['available_markets']
    externalURL = trackdata['external_urls']['spotify']
    imgURL = trackdata['album']['images'][2]['url']

    if len(trackdata['artists']) > 1 and util.secondArtistFlag == False:
        util.secondArtist.update({trackdata['artists'][1]['name']: trackdata['artists'][1]['id']})
    
    util.secondArtistFlag = True

    songData.append(songID)
    songData.append(name)
    songData.append(artist)
    songData.append(a_id)
    songData.append(year)
    songData.append(albumName)
    songData.append(popularity)
    songData.append(availableMarkets)
    songData.append(externalURL)
    songData.append(imgURL)

    songObj = getSongInfo(songData)

    return songObj

# Retrieves song ID from search string // should be ph
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
        acousticness = 0
        speechiness = 0
        mode = 0
    
    else:
        tempo = features[0]['tempo']
        loudness = features[0]['loudness']
        danceability = features[0]['danceability']
        energy = features[0]['energy']
        valence = features[0]['valence']
        acousticness = features[0]['acousticness']
        speechiness = features[0]['speechiness']
        mode = features[0]['mode']

    # Final song object
    genSong = Song(songStats[0], songStats[1], songStats[2], songStats[3], songStats[4], songStats[5], songStats[6], songStats[7], songStats[8], songStats[9], tempo, loudness, danceability, energy, valence, acousticness, speechiness, mode)

    return genSong

#Check to see if song is in tempo range (most important factor)
#If it is, then it'll be made into a song obect
def tempoCheck(songID, tempoRange):

    try:
        features = sp.audio_features('spotify:track:' + songID)

    except requests.exceptions.Timeout:
        features = sp.audio_features('spotify:track:' + songID)

    
        # Cases where API does not return any data for song ID
    if features == [None]:
        tempo = 0

    else:
        tempo = features[0]['tempo']


        if int(tempo) not in tempoRange:
            return False
        else:
            print("In range...")
            util.inRange += 1
            return True


# Retrieves related artists of the artist for the user's song
# Returns dictionary of artist IDs and names
def relatedArtists(genSong):

    artistLimit = 6
    jsonData = sp.artist_related_artists(genSong.a_id)

    if len(util.secondArtist.keys()) > 0:

        secondArtist = next(iter(util.secondArtist))

        if artistLimit - len(util.artistDict.keys()) >= 1:
            util.artistDict.update({secondArtist: util.secondArtist[secondArtist]})
        
    mainArtist = sp.artist(genSong.a_id)
    mainGenres = mainArtist['genres']
    numArtists = len(jsonData['artists'])


    for i in range(numArtists):
        if len(util.artistDict.keys()) >= artistLimit:
            break
        if any(genre in jsonData['artists'][i]['genres'] for genre in mainGenres):
            key = jsonData['artists'][i]['name']
            value = jsonData['artists'][i]['id']
            util.artistDict.update({key: value})

    if len(util.artistDict.keys()) < artistLimit:
        for i in range(artistLimit - len(util.artistDict.keys())):
            key = jsonData['artists'][i]['name']
            value = jsonData['artists'][i]['id']
            util.artistDict.update({key: value})

    print(util.artistDict.keys())
    print("ALREADY CHECKED", util.checkedArtists.keys())

    return util.artistDict



def recommendedTracks(genSong):

    tempoRange = util.calcTempoRange(int(genSong.tempo))

    #loudRange = util.calcLoudnessRange(genSong.loudness)
    popRange = util.calcPopularityRange(genSong.popularity)
    danceRange = util.calcDanceabilityRange(genSong.danceability)
    energyRange = util.calcEnergyRange(genSong.energy)
    valenceRange = util.calcValenceRange(genSong.valence)
    acousticRange = util.calcAcousticnessRange(genSong.acousticness)
    #speechRange = util.calcSpeechRange(genSong.speechiness)


    yearRange = util.calcYearRange(genSong.year)
    recList = list(util.artistDict.values())
    recList = [recList[0]]
    idList = []

    for song in util.albumtracks:
        idList.append(song.id)
    
    if len(idList) > 3:
        idList = idList[0:4]
    

    
    tempList = []

    results = sp.recommendations(seed_tracks=idList, country='US',
     limit=30, min_tempo=tempoRange[0] - 5, max_tempo=genSong.tempo + 5, target_tempo=genSong.tempo,
     min_popularity = int(popRange[0]), max_popularity=int(popRange[-1]),
     min_energy=energyRange[0], max_energy=energyRange[-1], target_energy=genSong.energy,
     min_valence=valenceRange[0], max_valence=valenceRange[-1], target_valence=genSong.valence,
     min_danceability=danceRange[0], max_danceability=danceRange[-1], target_danceability=genSong.danceability,
     min_acousticness=acousticRange[0], max_acousticness=acousticRange[-1], target_acousticness=genSong.acousticness)
    for track in results['tracks']:
        if int(track['album']['release_date'][:4]) in yearRange:
            logger.info(' Recommendation: %s - %s', track['name'],
                        track['artists'][0]['name'])
            songObj = makeSongFromID(track['id'])
            if songObj not in util.albumtracks and len(util.albumtracks) != util.limit:
                tempList.append(songObj)
    
    if len(tempList) > 1:
        random.shuffle(tempList)
        for songObj in tempList:
            if len(util.albumtracks) < util.limit:
                util.albumtracks.append(songObj)
            else:
                break


# Finds albums published within the correct time frame
def artistAlbums(dictionary, genSong):

    albumList = {}
    yearRange = util.calcYearRange(genSong.year)
    albums = []

    for artistID in dictionary.values():
        
        albumResults = sp.artist_albums(artistID, album_type='album', country='US')
        albums.extend(albumResults['items'])
        while albumResults['next']:
            albumResults = sp.next(albumResults)
            albums.extend(albumResults['items'])


        
        singleResults = sp.artist_albums(artistID, album_type='single', country='US')
        albums.extend(singleResults['items'])
        while singleResults['next']:
            singleResults = sp.next(singleResults)
            albums.extend(singleResults['items'])


    for album in albums:
        if album['name'] not in albumList:
            if int(album['release_date'][:4]) in yearRange:
                if album['id'] not in util.checkedAlbums:
                    albumList.update({album['name']: album['id']})
    
    print("ALBUM NAMES: ")
    print(albumList.keys())
    print("CHECKED ALBUMS: ")
    print(util.checkedAlbums)

    return albumList

# Adds songs that satisfy the requirements to the final playlist
def getTracks(albumList, genSong, limit):

    # creates of range of values that songs must be in to be added to the playlist
    tempoRange = util.calcTempoRange(int(genSong.tempo))
    loudRange = util.calcLoudnessRange(genSong.loudness)
    popRange = util.calcPopularityRange(genSong.popularity)
    danceRange = util.calcDanceabilityRange(genSong.danceability)
    energyRange = util.calcEnergyRange(genSong.energy)
    valenceRange = util.calcValenceRange(genSong.valence)
    acousticRange = util.calcAcousticnessRange(genSong.acousticness)
    speechRange = util.calcSpeechRange(genSong.speechiness)
    #modeVal = genSong.mode # Unused 

    # Shuffles the list of albums 
    albums = list(albumList.values())
    #random.seed(datetime.now())
    #random.shuffle(albums)

    # Search for songs in each album that satisfy requirements
    for value in albums:

        result = sp.album_tracks(value)
        random.shuffle(result['items'])

        if result['items'][0]['artists'][0]['id'] not in util.checkedArtists.values():

            for i in range(len(result['items'])):

                songID = result['items'][i]['id']

                if (tempoCheck(songID, tempoRange) == True): #To implement: return tuple with second value being half of song Obj

                    try:
                        songObj = makeSongFromID(songID)

                    except requests.exceptions.Timeout:

                        songObj = makeSongFromID(songID)

                    tempo = int(songObj.tempo)
                    loudness = float(songObj.loudness)
                    popularity = float(songObj.popularity)
                    danceability = float(songObj.danceability)
                    energy = float(songObj.energy)
                    valence = float(songObj.valence)
                    speech = float(songObj.speechiness)
                    acousticness = float(songObj.acousticness)
                    #mode = songObj.mode # Unused 

                    if (popularity in popRange
                        and danceability in danceRange and energy in energyRange and valence in valenceRange
                        and acousticness in acousticRange):

                        if songObj in util.albumtracks:
                            print("Already in list, not adding...")
                        else:
                            # measure to prevent artists from appearing in the playlist too many times
                            count = 0
                            for track in util.albumtracks:
                                if track.album == songObj.album and track.artist == songObj.artist:
                                    count += 2
                                elif track.artist == songObj.artist:
                                    count += 2
                            
                            if count > 3:
                                print("Artist/Song in list thrice, not adding...")
                                util.checkedArtists.update({songObj.artist: songObj.a_id})
                            else:
                                if len(util.albumtracks) == util.limit:
                                    break
                                # only working with songs available in the US (for now)
                                if 'US' in songObj.availableMarkets:
                                    songObj.printInfo()
                                    util.albumtracks.append(songObj)
                                else:
                                    continue
                
                    else:

                        if (energy in energyRange and danceability in danceRange and valence in valenceRange
                        and acousticness in acousticRange):
                            if songObj in util.albumtracks:
                                print("Already in list, not adding...")
                            else:
                                util.tempotracks.append(songObj)
                                print("ADDED TO TEMPO TRACKS")


                                if len(util.tempotracks) >= 5 and len(util.albumtracks) >= 3:
                                    random.shuffle(util.tempotracks)
                                    for track in util.tempotracks:
                                        count = 0 
                                        if len(util.albumtracks) < util.limit:
                                            for song in util.albumtracks:
                                                if track.artist == song.artist:
                                                    count += 1
                                                    if track.album == song.album:
                                                        count += 1
                                        
                                            if track not in util.albumtracks and count < 4 and track.a_id not in util.checkedArtists.values():
                                                if 'US' in track.availableMarkets:
                                                    util.albumtracks.append(track)
                                            else:
                                                util.checkedArtists.update({track.artist: track.a_id})

                else:

                    continue

                if len(util.albumtracks) == 1:
                    if util.inRange > 7:
                        recommendedTracks(genSong)
                        if len(util.albumtracks) >= 2:
                            recommendedTracks(util.albumtracks[1])
                        elif len(util.tempotracks) > 1:
                            util.albumtracks.append(util.tempotracks[0])
                            util.tempotracks.pop(0)
                                    
  
                if len(util.albumtracks) + len(util.tempotracks) >= 3:
                    recommendedTracks(genSong)
                
                    if len(util.albumtracks) < util.limit and len(util.albumtracks) > 1:
                        recommendedTracks(util.albumtracks[1])
                      
                if len(util.albumtracks) == util.limit:
                    break

            # maximum amount of songs in a playlist                       
            if len(util.albumtracks) == util.limit:
                break
            util.checkedAlbums.append(value)
        
        else:
            util.checkedAlbums.append(value)

    if len(util.albumtracks) < util.limit:
        recommendedTracks(genSong)

        
       
# Generates a playlist from the list of song objects 
def genPlaylist(tracks, title, artist, sp, user_id):

    tracklist = []

    for track in tracks:
        tracklist.append(track['id'])
        print(track['title'] + " " + str(track['tempo']))

    print("after")
    
    
    playlistTitle = "Seamless: " + artist + " - " + title

    # Playlist creation on user's spotify account
    playlistInfo = sp.user_playlist_create(user_id, playlistTitle)

    # Adding tracks to newly created playlist
    sp.user_playlist_add_tracks(user_id, playlistInfo['id'], tracklist)


def main():

    random.seed(datetime.now())

    songData = util.albumtracks[0]
    artistsDict = relatedArtists(songData)
    validAlbums = artistAlbums(artistsDict, songData)
    getTracks(validAlbums, songData, util.limit)
    originSong = util.albumtracks[0]

    originSong.printInfo()

    # Takes other songs on the list, and finds songs related to them
    while len(util.albumtracks) < util.limit:

        songData = originSong

        #Choosing which song to repeat the process with
        while songData in util.alreadyChosenSP:
            songData = random.choice(util.albumtracks)
            
            # If there is only one song to choose from
            if len(util.albumtracks) == 1:
                break

        artistsDict = relatedArtists(songData)
        validAlbums = artistAlbums(artistsDict, originSong)
        getTracks(validAlbums, originSong, util.limit)
        util.alreadyChosenSP.append(songData)

        # All the songs on the list have been chosen already 
        if len(util.alreadyChosenSP) == len(util.albumtracks):
            print("Couldn't find more songs")

            random.shuffle(util.tempotracks)

            for track in util.tempotracks:
                count = 0 
                if len(util.albumtracks) < util.limit:
                    for song in util.albumtracks:
                        if track.artist == song.artist:
                            count += 1
                
                    if track not in util.albumtracks and count < 3:
                        if 'US' in track.availableMarkets:
                            util.albumtracks.append(track)
                else:
                    break
            
            break
        
    # Songs organized by tempo    
    #util.albumtracks = sorted(util.albumtracks, key=operator.attrgetter("valence"))

 




