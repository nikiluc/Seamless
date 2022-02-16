import numpy as np

# Initializes global variables 
def init():

    global album_tracks
    global tempo_tracks
    global already_chosen_fm
    global already_chosen_sp
    global checked_albums
    global artist_dict
    global checked_artists
    global limit
    global year
    global second_artist
    global second_artistFlag
    global in_range

    album_tracks = []
    tempo_tracks = []
    already_chosen_fm = []
    already_chosen_sp = []
    checked_albums = []
    second_artist = {}
    second_artistFlag = False
    artist_dict = {}
    checked_artists = {}
    limit = 10
    year = 0
    in_range = 0


def calc_loudness_range(value):

    loud_range = list(np.arange(float(value) - 3, float(value) + 3, 1))
    rounded_loud = [round(x, 3) for x in loud_range]

    return rounded_loud

def calc_acousticness_range(value):

    acoustic_range = list(np.arange(float(value) - .22, float(value) + .22, .001))
    rounded_acoustic = [round(x, 3) for x in acoustic_range]

    return rounded_acoustic


def calc_popularity_range(value):

    if value >= 75:
        pop_range = list(np.arange(float(value) - 40, float(value) + 35, 1))
    else:
        pop_range = list(np.arange(float(value) - 30, float(value) + 35, 1))
    roundedPopularity = [round(x, 3) for x in pop_range]

    return roundedPopularity

def calc_energy_range(value):

    energy_range = list(np.arange(float(value) - .2, float(value) + .2, .001))
    rounded_energy = [round(x, 3) for x in energy_range]

    return rounded_energy

def calc_danceability_range(value):

    dance_range = list(np.arange(float(value) - .23, float(value) + .23, .001))
    rounded_dance = [round(x, 3) for x in dance_range]

    return rounded_dance

def calc_tempo_range(value):

    range_val = 6
    half_bpm = int(value/2)
    double_bpm = int(value * 2)

    tempo_range_full = [*range(value - range_val, value + range_val, 1)]
    tempo_range_half = [*range(half_bpm - range_val, half_bpm + range_val, 1)]
    tempo_range_double = [*range(double_bpm - range_val, double_bpm + range_val, 1)]
    tempo_range = tempo_range_full + tempo_range_half + tempo_range_double

    return tempo_range

def calc_valence_range(value):

    valence_range = list(np.arange(float(value) - .23, float(value) + .23, .001))
    rounded_valence = [round(x, 3) for x in valence_range]

    return rounded_valence

def calc_speech_range(value):

    speech_range = list(np.arange(float(value) - .25, float(value) + .25, .0001))
    rounded_speech = [round(x, 3) for x in speech_range]

    return rounded_speech

def calc_year_range(value):

    song_year_lower = int(value) - 2
    song_year_upper = int(value) + 3

    return list(range(song_year_lower, song_year_upper))


