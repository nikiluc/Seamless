import os
from os.path import join, dirname
import requests
import pylast
import seamless
import util
import random
from dotenv import load_dotenv
from song import Song
import logging


dp = join(dirname(__file__), '.env')
load_dotenv(dotenv_path=dp)

# Authentication for LastFM API
USER_AGENT = os.getenv('USER_AGENT')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

username = os.getenv('username')
password = os.getenv('password')
password_hash = pylast.md5(password)

logger = logging.getLogger('lastfm.reccomendations')
logging.basicConfig(level='INFO')

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
def valid_tracks(gen_song, song_obj):

    valid = []

    r = lastfm_get({'artist': song_obj.artist, 'track': song_obj.title})
    util.artist_dict.update(({song_obj.artist: song_obj.a_id}))
    new_data = r.json()
    gen_song.print_info()

    for i in range(len(new_data['similartracks']['track'])):

        song_info = new_data['similartracks']['track'][i]['name'] + \
            ' ' + new_data['similartracks']['track'][i]['artist']['name']
        match_data = float(new_data['similartracks']['track'][i]['match'])

        try:
            # LastFM match value
            if match_data > 0.6:
                matched_song_data = seamless.get_song_data(song_info)
                matched_song_obj = seamless.make_song_from_id(matched_song_data)
                matched_song_obj.print_info()
                if matched_song_obj not in util.album_tracks:
                    valid.append(matched_song_obj)

        except:
            pass

    tempo_range = util.calc_tempo_range(int(gen_song.tempo))
    energy_range = util.calc_energy_range(float(gen_song.energy))
    year_range = util.calc_year_range(int(util.year))

    # Songs that satisfy the requirements
    valid_req = [song for song in valid if int(song.tempo) in tempo_range
                and float(song.energy) in energy_range
                and int(song.year) in year_range]

    # Songs that at least match the tempo (last resort)
    util.tempo_tracks = [
        song for song in valid if int(song.tempo) in tempo_range]

    for track in valid_req:
        if len(util.album_tracks) < util.limit:
            util.album_tracks.append(track)

    logger.info([song.title for song in util.album_tracks])

# Uses search string to find similar songs
def launch(search_str, auth=None, final_songs=None):

    # initialization of global variables
    util.init()

    # Authentication only occurs when user adds playlist
    if (search_str == "True"):
        sp_user = auth
        user_id = sp_user.me()['id']
        seamless.gen_playlist(
            final_songs, final_songs[0]['title'], final_songs[0]['artist'], sp_user, user_id)
        return True

    # creation of song object
    song_obj = seamless.make_song_from_id(search_str)
    util.year = song_obj.year
    util.album_tracks.append(song_obj)
    valid_tracks(song_obj, song_obj)

    # Songs that went through LastFM API
    util.already_chosen_fm.append(song_obj)

    logger.info(f'Number of tracks: {len(util.album_tracks)}')
    # Filter through reccomended songs first
    seamless.recommended_tracks(song_obj)

    # finds similar songs of tracks that have already satisfied the requirements
    while len(util.album_tracks) < util.limit:

        # choosing songs from the LastFM list
        song_data = random.sample(util.album_tracks, 1)[0]
        seamless.main()

        valid_tracks(song_data, song_obj)
        seamless.recommended_tracks(song_data)
        util.already_chosen_fm.append(song_data)

    songsChosen = util.album_tracks
    return songsChosen


if __name__ == "__main__":
    launch(search_str="starving zedd")
