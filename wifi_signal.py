import math

class WifiSignal:
    strength = 0 # dBm (the formula requires the number in dBm)
    frequency = 2412  #2412MHz (the formula requires the number in MHz)

    def getDistance(self):
        exp = (27.55 - ( 20 * math.log(self.frequency, 10)) + math.fabs(self.strength)) / 20.0
        dist_m = math.pow(10.0, exp)
        return ( dist_m )