import flight_manager
import thread
import time
import wifi_signal

def safe_land_drone(drone):
    time.sleep(4)
    drone.land()
    print 'WARNING: security landing'

def wifi_handler():
    print 'Wifi connection found'

def phone_handler():
    print 'Phone found'


wifi_man = wifi_signal.WifiSignal()
flight_man = flight_manager.Flight(0,0,(0,0),wifi_man,phone_handler)
thread.start_new_thread(safe_land_drone, (flight_man.drone,))
flight_man.drone.takeoff()
flight_man.move_drone(flight_manager.DIRECTION_UP, 5, 1, True)
flight_man.drone.land()
flight_man.drone.halt()