import math
import time

class WifiSignal:
    connected = False
    signal_list = []
    max_size_signal_list = 10000
    strength = 0 # dBm (the formula requires the number in dBm)
    frequency = 2412  #2412MHz (the formula requires the number in MHz)
    best_position_found = ((0,0), 0) #First element: coordinates, second element: signal strength in that point

    def getDistance(self):
        return self.getDistanceBySignalStrength(self.signal_list[0])

    def getDistanceBySignalStrength(self, strength):
        exp = (27.55 - ( 20 * math.log(self.frequency, 10)) + math.fabs(strength)) / 20.0
        dist_m = math.pow(10.0, exp)
        return ( dist_m )

    def addSignal(self, signal_strength, time_received):
        self.signal_list.insert(0, {
            'strength':signal_strength,
            'time':time_received
        })
        if len(self.signal_list) > self.max_size_signal_list:
            self.signal_list = self.signal_list[::self.max_size_signal_list]

    def getLastSignalStrength(self):
        if len(self.signal_list) < 1:
            return 0
        return self.signal_list[0]

    def getAVG(self, samples_number): #TODO: check if samples_number > signal_list length
        avg = 0.0
        for count in range(0, samples_number):
            avg += self.signal_list[count]['strength']
        return (avg/samples_number)

    def getAVG2(self, interval_time): #Interval_time is in [s]
        avg = 0.0
        count = 0
        now = time.time()
        for signal in self.signal_list:
            if (now - signal['time']) < interval_time:
                avg += signal['strength']
                count+=1

        if count == 0:
            return 0.0
        return (avg/count)