import numpy as np

# Initializes global variables 
def init():

    global albumtracks
    global tempotracks
    global alreadyChosenFM
    global alreadyChosenSP
    global checkedAlbums
    global artistDict
    global checkedArtists
    global limit
    global year
    global secondArtist
    global secondArtistFlag

    albumtracks = []
    tempotracks = []
    alreadyChosenFM = []
    alreadyChosenSP = []
    checkedAlbums = []
    secondArtist = {}
    secondArtistFlag = False
    artistDict = {}
    checkedArtists = {}
    limit = 10
    year = 0


def calcLoudnessRange(value):

    loudRange = list(np.arange(float(value) - 3, float(value) + 3, 1))

    roundedLoud = [round(x, 3) for x in loudRange]

    return roundedLoud

def calcAcousticnessRange(value):

    acousticRange = list(np.arange(float(value) - .25, float(value) + .35, .001))

    roundedAcoustic = [round(x, 3) for x in acousticRange]

    return roundedAcoustic


def calcPopularityRange(value):

    if value >= 75:

        popRange = list(np.arange(float(value) - 40, float(value) + 35, 1))
    
    else:

        popRange = list(np.arange(float(value) - 25, float(value) + 35, 1))

    roundedPopularity = [round(x, 3) for x in popRange]

    return roundedPopularity

def calcEnergyRange(value):

    energyRange = list(np.arange(float(value) - .25, float(value) + .25, .001))

    roundedEnergy = [round(x, 3) for x in energyRange]

    return roundedEnergy

def calcDanceabilityRange(value):

    danceRange = list(np.arange(float(value) - .25, float(value) + .25, .001))

    roundedDance = [round(x, 3) for x in danceRange]

    return roundedDance

def calcTempoRange(value):

    rangeVal = 6

    halfBPM = int(value/2)

    doubleBPM = int(value * 2)

    tempoRangeFull = [*range(value - rangeVal, value + rangeVal, 1)]

    tempoRangeHalf = [*range(halfBPM - rangeVal, halfBPM + rangeVal, 1)]

    tempoRangeDouble = [*range(doubleBPM - rangeVal, doubleBPM + rangeVal, 1)]

    tempoRange = tempoRangeFull + tempoRangeHalf + tempoRangeDouble


    return tempoRange

def calcValenceRange(value):

    valenceRange = list(np.arange(float(value) - .3, float(value) + .3, .001))

    roundedValence = [round(x, 3) for x in valenceRange]

    return roundedValence

def calcSpeechRange(value):

    speechRange = list(np.arange(float(value) - .33, float(value) + .33, .0001))

    roundedSpeech = [round(x, 3) for x in speechRange]

    return roundedSpeech

def calcYearRange(value):

    songYear = int(value)

    if songYear in [2019, 2020, 2021]:
        songYRange1 = songYear - 2
        songYRange2 = songYear + 2
    
    else:

        songYRange1 = songYear - 2
        songYRange2 = songYear + 3

    return list(range(songYRange1, songYRange2))


