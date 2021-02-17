class Song():

     def __init__(self, id, title, artist, a_id, year, album, popularity, availableMarkets, externalURL, imgURL, tempo, loudness, danceability, energy, valence, acousticness, speechiness, mode):
         self.title = title
         self.id = id
         self.artist = artist
         self.a_id = a_id
         self.year = year
         self.album = album
         self.popularity = popularity
         self.availableMarkets = availableMarkets
         self.externalURL = externalURL
         self.imgURL = imgURL
         self.tempo = tempo
         self.loudness = loudness
         self.danceability = danceability
         self.energy = energy
         self.valence = valence
         self.acousticness = acousticness
         self.speechiness = speechiness
         self.mode = mode

    
     def printInfo(self):
        for attr, item in vars(self).items():
            print(attr + ": " + str(item))

     def __eq__(self, other): 
        if self.id == other.id:
            return True
        if self.title == other.title and self.artist == other.artist:
            return True
        else:
            return False