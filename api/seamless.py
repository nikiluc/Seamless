from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
import spotipy
from song import Song
import random
import requests
import util
import logging


# set as environment variables
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
logger = logging.getLogger('examples.artist_recommendations')
logging.basicConfig(level='INFO')


# Creates a song object from Spotify song ID
def make_song_from_id(song_id):

    song_data = []
    track_data = sp.track(song_id)

    name = track_data['name']
    albumName = track_data['album']['name']
    year = track_data['album']['release_date'][:4]
    artist = track_data['artists'][0]['name']
    a_id = track_data['artists'][0]['id']
    popularity = track_data['popularity']
    availableMarkets = track_data['album']['available_markets']
    externalURL = track_data['external_urls']['spotify']
    imgURL = track_data['album']['images'][2]['url']

    if len(track_data['artists']) > 1 and util.second_artistFlag == False:
        util.second_artist.update({track_data['artists'][1]['name']: track_data['artists'][1]['id']})  
    util.second_artistFlag = True

    song_data.append(song_id)
    song_data.append(name)
    song_data.append(artist)
    song_data.append(a_id)
    song_data.append(year)
    song_data.append(albumName)
    song_data.append(popularity)
    song_data.append(availableMarkets)
    song_data.append(externalURL)
    song_data.append(imgURL)

    return get_song_info(song_data)


# Retrieves song ID from search string
def get_song_data(search_str):

    result = sp.search(search_str, limit=3)

    return result['tracks']['items'][0]['id']


# Obtains audio features from each track to then compose a complete song object
def get_song_info(song_stats):

    try:
        features = sp.audio_features('spotify:track:' + song_stats[0])
    except requests.exceptions.Timeout:
        logger.info('No data return for song.')

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
    gen_song = Song(song_stats[0], song_stats[1], song_stats[2],
    song_stats[3], song_stats[4], song_stats[5], song_stats[6],
    song_stats[7], song_stats[8], song_stats[9], tempo, loudness,
    danceability, energy, valence, acousticness, speechiness, mode)

    return gen_song


# Check to see if song is in tempo range (most important factor)
# If it is, then it'll be made into a song obect
def tempo_check(song_id, tempo_range):

    try:
        features = sp.audio_features('spotify:track:' + song_id)

    except requests.exceptions.Timeout:
        features = sp.audio_features('spotify:track:' + song_id)  
    # Cases where API does not return any data for song ID
    if features == [None]:
        tempo = 0

    else:
        tempo = features[0]['tempo']

        if int(tempo) not in tempo_range:
            return False
        else:
            print("In range...")
            util.in_range += 1
            return True


# Retrieves related artists of the artist for the user's song
# Returns dictionary of artist IDs and names
def related_artists(gen_song):

    artist_limit = 6
    json_data = sp.artist_related_artists(gen_song.a_id)

    if len(util.second_artist.keys()) > 0:

        second_artist = next(iter(util.second_artist))

        if artist_limit - len(util.artist_dict.keys()) >= 1:
            util.artist_dict.update({second_artist: util.second_artist[second_artist]})
        
    main_artist = sp.artist(gen_song.a_id)
    main_genres = main_artist['genres']
    num_artists = len(json_data['artists'])


    for i in range(num_artists):
        if len(util.artist_dict.keys()) >= artist_limit:
            break
        if any(genre in json_data['artists'][i]['genres'] for genre in main_genres):
            key = json_data['artists'][i]['name']
            value = json_data['artists'][i]['id']
            util.artist_dict.update({key: value})

    if len(util.artist_dict.keys()) < artist_limit:
        for i in range(artist_limit - len(util.artist_dict.keys())):
            key = json_data['artists'][i]['name']
            value = json_data['artists'][i]['id']
            util.artist_dict.update({key: value})

    print(util.artist_dict.keys())
    print("ALREADY CHECKED", util.checked_artists.keys())

    return util.artist_dict



def recommended_tracks(gen_song):

    tempo_range = util.calc_tempo_range(int(gen_song.tempo))

    pop_range = util.calc_popularity_range(gen_song.popularity)
    dance_range = util.calc_danceability_range(gen_song.danceability)
    energy_range = util.calc_energy_range(gen_song.energy)
    valence_range = util.calc_valence_range(gen_song.valence)
    acoustic_range = util.calc_acousticness_range(gen_song.acousticness)


    year_range = util.calc_year_range(gen_song.year)
    rec_list = list(util.artist_dict.values())
    song_id_list = []

    for song in util.album_tracks:
        song_id_list.append(song.id)
    
    if len(song_id_list) > 3:
        song_id_list = song_id_list[0:3]
        rec_list = [rec_list[0]]
    else:
        song_id_list = song_id_list[0:3]
        rec_list = []
    
    temp_rec_list = []

    results = sp.recommendations(seed_tracks=song_id_list, seed_artists=rec_list, country='US',
     limit=30, min_tempo=tempo_range[0] - 5, max_tempo=gen_song.tempo + 5, target_tempo=gen_song.tempo,
     min_popularity = int(pop_range[0]), max_popularity=int(pop_range[-1]),
     min_energy=energy_range[0], max_energy=energy_range[-1], target_energy=gen_song.energy,
     min_valence=valence_range[0], max_valence=valence_range[-1], target_valence=gen_song.valence,
     min_danceability=dance_range[0], max_danceability=dance_range[-1], target_danceability=gen_song.danceability,
     min_acousticness=acoustic_range[0], max_acousticness=acoustic_range[-1], target_acousticness=gen_song.acousticness)
    for track in results['tracks']:
        if int(track['album']['release_date'][:4]) in year_range:
            logger.info(' Recommendation: %s - %s', track['name'],
                        track['artists'][0]['name'])
            song_obj = make_song_from_id(track['id'])
            if song_obj not in util.album_tracks and len(util.album_tracks) != util.limit:
                temp_rec_list.append(song_obj)
    
    random.seed(datetime.now())
    
    if len(temp_rec_list) > 1:
        random.shuffle(temp_rec_list)
        for song_obj in temp_rec_list:
            remixFlag = False
            for track in util.album_tracks:
                if track.title.split("(")[0] == song_obj.title.split("(")[0] and track.artist == song_obj.artist:
                    remixFlag = True
            if len(util.album_tracks) < util.limit and remixFlag == False:
                util.album_tracks.append(song_obj)
            else:
                break


# Finds albums published within the correct time frame
def artist_albums(dictionary, gen_song):

    albumList = {}
    year_range = util.calc_year_range(gen_song.year)
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
            if int(album['release_date'][:4]) in year_range:
                if album['id'] not in util.checked_albums:
                    albumList.update({album['name']: album['id']})
    
    logger.info(f'Album titles: {albumList.keys()}')
    logger.info(f'Processed albums: {util.checked_albums}')

    return albumList

# Adds songs that satisfy the requirements to the final playlist
def get_tracks(albumList, gen_song, limit):

    # creates of range of values that songs must be in to be added to the playlist
    tempo_range = util.calc_tempo_range(int(gen_song.tempo))
    pop_range = util.calc_popularity_range(gen_song.popularity)
    dance_range = util.calc_danceability_range(gen_song.danceability)
    energy_range = util.calc_energy_range(gen_song.energy)
    valence_range = util.calc_valence_range(gen_song.valence)
    acoustic_range = util.calc_acousticness_range(gen_song.acousticness)

    albums = list(albumList.values())

    # Search for songs in each album that satisfy requirements
    for value in albums:

        result = sp.album_tracks(value)
        random.shuffle(result['items'])

        if result['items'][0]['artists'][0]['id'] not in util.checked_artists.values():
            for i in range(len(result['items'])):
                song_id = result['items'][i]['id']

                if (tempo_check(song_id, tempo_range) == True): # To implement: return tuple with second value being half of song Obj
                    try:
                        song_obj = make_song_from_id(song_id)
                    except requests.exceptions.Timeout:
                        song_obj = make_song_from_id(song_id)

                    popularity = float(song_obj.popularity)
                    danceability = float(song_obj.danceability)
                    energy = float(song_obj.energy)
                    valence = float(song_obj.valence)
                    acousticness = float(song_obj.acousticness)

                    if (popularity in pop_range
                        and danceability in dance_range and energy in energy_range and valence in valence_range
                        and acousticness in acoustic_range):

                        if song_obj in util.album_tracks:
                            print("Already in list, not adding...")
                        else:
                            # measure to prevent artists from appearing in the playlist too many times
                            artist_count = 0
                            for track in util.album_tracks:
                                if track.album == song_obj.album and track.artist == song_obj.artist:
                                    artist_count += 3
                                elif track.artist == song_obj.artist:
                                    artist_count += 2
                            
                            if artist_count > 3:
                                print("Artist/Song in list thrice, not adding...")
                                util.checked_artists.update({song_obj.artist: song_obj.a_id})
                            else:
                                if len(util.album_tracks) == util.limit:
                                    break
                                # only working with songs available in the US (for now)
                                if 'US' in song_obj.availableMarkets:
                                    song_obj.print_info()
                                    if track.title.split("(")[0] != song_obj.title.split("(")[0] and track.artist == song_obj.artist:
                                        util.album_tracks.append(song_obj)
                                else:
                                    continue
                
                    else:

                        if (energy in energy_range and danceability in dance_range and valence in valence_range
                        and acousticness in acoustic_range):
                            if song_obj in util.album_tracks:
                                print("Already in list, not adding...")
                            else:
                                util.tempo_tracks.append(song_obj)
                                print("Added to tempo tracks...")
                                if len(util.tempo_tracks) >= 5 and len(util.album_tracks) >= 3:
                                    random.shuffle(util.tempo_tracks)
                                    for track in util.tempo_tracks:
                                        artist_count = 0 
                                        if len(util.album_tracks) < util.limit:
                                            for song in util.album_tracks:
                                                if track.artist == song.artist:
                                                    artist_count += 1
                                                    if track.album == song.album:
                                                        artist_count += 1
                                        
                                            if track not in util.album_tracks and artist_count < 4 and track.a_id not in util.checked_artists.values():
                                                if 'US' in track.availableMarkets:
                                                    util.album_tracks.append(track)
                                            else:
                                                util.checked_artists.update({track.artist: track.a_id})

                else:

                    continue

                if len(util.album_tracks) == 1:
                    if util.in_range > 7 or len(util.album_tracks) + len(util.tempo_tracks) >= 3:
                        recommended_tracks(gen_song)
                        if len(util.album_tracks) >= 2:
                            recommended_tracks(util.album_tracks[1])
                                    
        # maximum amount of songs in a playlist                       
        if len(util.album_tracks) == util.limit:
            break
            
        util.checked_albums.append(value)

    if len(util.album_tracks) < util.limit:
        recommended_tracks(gen_song)

  
# Generates a playlist from the list of song objects 
def gen_playlist(tracks, title, artist, sp, user_id):

    track_list = []

    for track in tracks:
        track_list.append(track['id'])
        print(track['title'] + " " + str(track['tempo']))
    
    playlist_title = "Seamless: " + artist + " - " + title

    # Playlist creation on user's spotify account
    playlist_info = sp.user_playlist_create(user_id, playlist_title)

    # Adding tracks to newly created playlist
    sp.user_playlist_add_tracks(user_id, playlist_info['id'], track_list)


def main():

    random.seed(datetime.now())
    song_data = util.album_tracks[0]
    artists_dict = related_artists(song_data)
    valid_albums = artist_albums(artists_dict, song_data)
    get_tracks(valid_albums, song_data, util.limit)
    origin_song = util.album_tracks[0]

    origin_song.print_info()

    # Takes other songs on the list, and finds songs related to them
    while len(util.album_tracks) < util.limit:

        song_data = origin_song

        #Choosing which song to repeat the process with
        while song_data in util.already_chosen_sp:
            song_data = random.choice(util.album_tracks)
            
            # If there is only one song to choose from
            if len(util.album_tracks) == 1:
                break

        artists_dict = related_artists(song_data)
        valid_albums = artist_albums(artists_dict, origin_song)
        get_tracks(valid_albums, origin_song, util.limit)
        util.already_chosen_sp.append(song_data)

        # All the songs on the list have been chosen already 
        if len(util.already_chosen_sp) == len(util.album_tracks):
            print("Couldn't find more songs")

            random.shuffle(util.tempo_tracks)

            for track in util.tempo_tracks:
                artist_count = 0 
                if len(util.album_tracks) < util.limit:
                    for song in util.album_tracks:
                        if track.artist == song.artist:
                            artist_count += 1
                
                    if track not in util.album_tracks and artist_count < 3:
                        if 'US' in track.availableMarkets:
                            util.album_tracks.append(track)
                else:
                    break
            
            break
        

 




