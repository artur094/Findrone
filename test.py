from ardrone.libardrone import ARDrone
import time


drone = ARDrone()
drone.speed = 0.5
drone.takeoff()
time.sleep(5)
drone.turn_left()
time.sleep(2)
drone.turn_right()
time.sleep(2)
#drone.move_forward()
#time.sleep(3)
#drone.move_backward()
#time.sleep(3)
drone.land()

