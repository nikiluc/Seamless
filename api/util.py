import numpy as np

# Initializes global variables 
def init():

    global albumtracks
    global alreadyChosenFM
    global alreadyChosenSP
    global checkedAlbums
    global artistDict
    global limit

    albumtracks = []
    alreadyChosenFM = []
    alreadyChosenSP = []
    checkedAlbums = []
    artistDict = {}
    limit = 10


def calcLoudnessRange(value):

    loudRange = list(np.arange(float(value) - 3, float(value) + 3, .001))

    roundedLoud = [round(x, 3) for x in loudRange]

    return roundedLoud

def calcEnergyRange(value):

    energyRange = list(np.arange(float(value) - .3, float(value) + .3, .001))

    roundedEnergy = [round(x, 3) for x in energyRange]

    return roundedEnergy

def calcDanceabilityRange(value):

    danceRange = list(np.arange(float(value) - .4, float(value) + .4, .001))

    roundedDance = [round(x, 3) for x in danceRange]

    return roundedDance

def calcTempoRange(value):

    rangeVal = 5

    halfBPM = int(value/2)

    doubleBPM = int(value * 2)

    tempoRangeFull = [*range(value - rangeVal, value + rangeVal, 1)]

    tempoRangeHalf = [*range(halfBPM - rangeVal, halfBPM + rangeVal, 1)]

    tempoRangeDouble = [*range(doubleBPM - rangeVal, doubleBPM + rangeVal, 1)]

    tempoRange = tempoRangeFull + tempoRangeHalf + tempoRangeDouble

    return tempoRange

def calcValenceRange(value):

    valenceRange = list(np.arange(float(value) - .35, float(value) + .35, .001))

    roundedValence = [round(x, 3) for x in valenceRange]

    return roundedValence

def calcSpeechRange(value):

    speechRange = list(np.arange(float(value) - .5, float(value) + .5, .0001))

    roundedSpeech = [round(x, 3) for x in speechRange]

    return roundedSpeech

def calcYearRange(value):

    songYear = int(value)
    songYRange1 = songYear - 2
    songYRange2 = songYear + 4

    return list(range(songYRange1, songYRange2))


