class Song():

     def __init__(self, id, title, artist, a_id, year, album, availableMarkets, tempo, loudness, danceability, energy, valence, speechiness, mode):
         self.title = title
         self.id = id
         self.artist = artist
         self.a_id = a_id
         self.year = year
         self.album = album
         self.availableMarkets = availableMarkets
         self.tempo = tempo
         self.loudness = loudness
         self.danceability = danceability
         self.energy = energy
         self.valence = valence
         self.speechiness = speechiness
         self.mode = mode

    
     def printInfo(self):
        for attr, item in vars(self).items():
            print(attr + ": " + str(item))

     def __eq__(self, other): 
        if self.id == other.id: 
            return True
        else:
            return False