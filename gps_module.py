from math import radians, cos, sin, asin, sqrt

class GPSModule:
    coordinate = (0, 0) # (latitude (N/S), longitude (E/W))

    def __init__(self):
        pass

    def update(self):
        #Update the coordinate of the drone
        pass

    def getCoordinate(self):
        #Return updated coordinate of the drone
        self.update()
        return self.coordinate

    def getDistance(self, coordinate):
        self.update()
        lat1 = self.getCoordinate()[0]
        lon1 = self.getCoordinate()[1]

        lat2 = coordinate[0]
        lon2 = coordinate[1]

        return (1000.0 * self.haversine(lon1,lat1,lon2,lat2)) #haversine returns in [Km], but I want meters

    def haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6367 * c
        return km