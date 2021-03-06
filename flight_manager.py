import math, time
from gps_module import GPSModule
from wifi_signal import WifiSignal
from ardrone.libardrone import ARDrone


DIRECTION_LEFT = 'left'
DIRECTION_RIGHT = 'right'
DIRECTION_UP = 'up'
DIRECTION_DOWN = 'down'
TIME_TO_WAIT_BEFORE_LAND = 60 # TODO: change to 60 sec

class Flight:
    drone = None
    phone_found_handler = None
    stop_search = False

    width = 0               # Meters
    length = 0              # Meters
    height = 2              # Meters

    delta_w = 2             # Range of WiFi coverage
    delta_l = 2             # Range of WiFi coverage

    orig = (0,0)            # Origin of the rectangle
    w = (0,0)               # Coordinate of the rectangle (where the length is 0 and W is width
    l = (0,0)
    wl = (0,0)
    initial_drone_position = (0,0)
    initial_drone_coordinate = (0,0)
    drone_position = (0,0)
    #gps = GPSModule()
    wifi = None
    gps = None
    start_direction = 'left'

    #connected = False       # Says if a phone is connected to the drone through TCP connection

    # Width: Meters of the width of the rectangle
    # Length: Meters of the length of the rectangle
    # Position: Coordinates in meters of the position of the drone
    def __init__(self, width, length, position, wifi_manager, phone_handler, gps_module):
        self.drone = ARDrone()
        print 'configured drone'
        self.drone.trim()
        self.phone_found_handler = phone_handler
        self.width = width
        self.length = length
        #self.gps = GPSModule()
        self.gps = gps_module
        print 'configured gps'
        self.wifi = WifiSignal()
        print 'configured wifi'
        self.w = (width, 0)
        self.l = (0, length)
        self.wl = (width, length)

        self.drone_position = position
        self.initial_drone_position = (position[0], position[1])
        self.initial_drone_coordinate = self.gps.getCoordinate()

        if math.fabs( self.drone_position[0] - self.orig[0] ) < math.fabs(self.wl[0] - self.drone_position[0] ):
            self.start_direction = 'left'
        else:
            self.start_direction = 'right'

    def start(self):
        #gps = GPSModule()
        while self.gps.getCoordinate()[0] == 0.0 or self.gps.getCoordinate()[1] == 0:
            print 'Waiting gps...'
            time.sleep(0.5)
        self.drone.takeoff() #TODO: remove comment on takeoff
        if self.start_direction == 'left':
            print 'Starting on left side of the area'
            self.start_left()
        else:
            print 'Starting on right side of the area'
            self.start_right()

        print 'Static scan ended'

        # When I execute this code means:
        # No phone found --> I'm already at home --> land
        # Phone found --> start searching it
        # To check: enough to check the connected variable

        if self.wifi.connected:
            print 'Starting to search the phone using wifi signal strength'
            self.start_follow_wifi_signal(DIRECTION_UP, self.opposite_direction(self.start_direction), self.height)
            #Now I should be in the location of the buried person
            #Send notification
            #Wait one minute (or more)
            time.sleep(TIME_TO_WAIT_BEFORE_LAND)
        else:
            #Job done!
            pass

        self.drone.land()
        print 'Landing'
        #End... I hope for a good job!

    #TODO: fix stop function
    def stop(self):
        self.stop_search = True

    def start_left(self):
        print 'Drone position: ', self.drone_position[0], ', ', self.drone_position[1]
        # Starting position for the scan
        starting_point = (self.orig[0] + self.delta_w, self.orig[0] +self.delta_l)
        print 'Move to coordinate: ', starting_point[0], ', ', starting_point[1]

        # Move to the beginning
        self.move(self.drone_position, starting_point, self.height)

        # Start the scan
        while self.drone_position[0] < self.w[0]:
            #Go upper
            next_position = (self.drone_position[0], self.l[1] - self.delta_l)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            found_wifi = self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if self.wifi.connected == True:
                # Start specific algorithm of search
                print 'Phone connected, exiting from static search'
                #self.start_follow_wifi_signal()
                return

            if self.stop_search:
                self.move(self.drone_position, self.initial_drone_position,
                          self.height)  # TODO: avoid crash between drones!
                return

            right_movement = min(2*self.delta_w, self.w[0] - self.drone_position[0])

            #Check if I can move on the right
            if self.drone_position[0] >= ( self.w[0] - self.delta_w ):
                break

            #Go right
            next_position = (self.drone_position[0] + right_movement, self.drone_position[1])
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if self.wifi.connected == True:
                # Start specific algorithm of search
                print 'Phone connected, exiting from static search'
                #self.start_follow_wifi_signal()
                return

            if self.stop_search:
                self.move(self.drone_position, self.initial_drone_position,
                          self.height)  # TODO: avoid crash between drones!
                return

            #Go down
            next_position = (self.drone_position[0], self.orig[0] + self.delta_l)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if self.wifi.connected == True:
                # Start specific algorithm of search
                print 'Phone connected, exiting from static search'
                #self.start_follow_wifi_signal()
                return

            if self.stop_search:
                self.move(self.drone_position, self.initial_drone_position,
                          self.height)  # TODO: avoid crash between drones!
                return

            right_movement = min(2 * self.delta_w, self.w[0] - self.drone_position[0])

            # Check if I can move on the right
            if self.drone_position[0] >= ( self.w[0] - self.delta_w ):
                break

            #Go right
            next_position = (self.drone_position[0] + right_movement, self.drone_position[1])
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if self.wifi.connected == True:
                # Start specific algorithm of search
                print 'Phone connected, exiting from static search'
                #self.start_follow_wifi_signal()
                return

                #Scanned 5 * delta_w meters in width (assuming delta_w = 2, it's 10 meters)

            if self.stop_search:
                self.move(self.drone_position, self.initial_drone_position,
                          self.height)  # TODO: avoid crash between drones!
                return

        # Need to check in detail if drone has covered all the area
        # If no WiFi connection has been found, then go home
        self.move(self.drone_position, self.initial_drone_position, self.height) #TODO: avoid crash between drones!

    def start_right(self):
        print 'Drone position: ', self.drone_position[0], ', ', self.drone_position[1]
        # Starting position for the scan
        starting_point = (self.w[0] - self.delta_w, self.delta_l)
        print 'Move to coordinate: ', starting_point[0], ', ', starting_point[1]

        # Move to the beginning
        self.move(self.drone_position, starting_point, self.height)

        # Start the scan
        while self.drone_position[0] >= self.orig[0]:
            # Go upper
            next_position = (self.drone_position[0], self.l[1] - self.delta_l)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            found_wifi = self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if self.wifi.connected == True:
                # Start specific algorithm of search
                print 'Phone connected, exiting from static search'
                #self.start_follow_wifi_signal()
                return

            if self.stop_search:
                self.move(self.drone_position, self.initial_drone_position,
                          self.height)  # TODO: avoid crash between drones!
                return

            left_movement = -1 * min(2 * self.delta_w, self.drone_position[0] - self.orig[0])

            # Check if I can move on the left
            if self.drone_position[0] <= (self.orig[0] + self.delta_w):
                break

            # Go left
            next_position = (self.drone_position[0] + left_movement, self.drone_position[1])
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if self.wifi.connected == True:
                # Start specific algorithm of search
                print 'Phone connected, exiting from static search'
                #self.start_follow_wifi_signal()
                return

            if self.stop_search:
                self.move(self.drone_position, self.initial_drone_position,
                          self.height)  # TODO: avoid crash between drones!
                return

            # Go down
            next_position = (self.drone_position[0], self.orig[0] + self.delta_l)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if self.wifi.connected == True:
                # Start specific algorithm of search
                print 'Phone connected, exiting from static search'
                #self.start_follow_wifi_signal()
                return

            if self.stop_search:
                self.move(self.drone_position, self.initial_drone_position,
                          self.height)  # TODO: avoid crash between drones!
                return

            left_movement = -1* min(2 * self.delta_w, self.drone_position[0] - self.orig[0])

            # Check if I can move on the right
            if self.drone_position[0] <= (self.orig[0] + self.delta_w):
                break

            # Go left
            next_position = (self.drone_position[0] + left_movement, self.drone_position[1])
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if self.wifi.connected == True:
                # Start specific algorithm of search
                print 'Phone connected, exiting from static search'
                #self.start_follow_wifi_signal()
                return

            if self.stop_search:
                self.move(self.drone_position, self.initial_drone_position,
                          self.height)  # TODO: avoid crash between drones!
                return

        # Need to check in detail if drone has covered all the area
        # If no WiFi connection has been found, then go home
        self.move(self.drone_position, self.initial_drone_position, self.height)  # TODO: avoid crash between drones!

    '''
        direction --> actual direction of the drone 
        secondary_direction --> if direction is UP/DOWN, secondary_direction is the best direction between LEFT/RIGHT to check
    '''
    def start_follow_wifi_signal(self, direction,secondary_direction, height):
        delta_s = 0.5
        number_step_below_signal = 3
        self.follow_wifi_signal_direction(direction, delta_s, number_step_below_signal, height)
        self.follow_wifi_signal_direction(secondary_direction, delta_s, number_step_below_signal, height)

        #TODO: TO CHECK

        delta_s = 0.25
        number_step_below_signal = 3
        self.follow_wifi_signal_direction(direction, delta_s, number_step_below_signal, height)
        self.follow_wifi_signal_direction(secondary_direction, delta_s, number_step_below_signal, height)
        #Notify that we've found the phone
        self.phone_found_handler()

    def follow_wifi_signal_direction(self, direction,distance_movement,limit_step_below_signal_strength, height):
        time_to_wait = 1
        decreasing = False
        negative_direction = self.opposite_direction(direction)
        linear_position = 0
        number_step_below_signal_strength = 0
        ss_pos_list = []

        ss_pos = {
            'line_position': linear_position,
            'gps_position': self.gps.getCoordinate(),
            'signal_strength': self.wifi.getAVG2(time_to_wait)
        }
        ss_pos_list.append(ss_pos)
        max_ss_pos = ss_pos

        #move forward
        while not decreasing:
            self.move_drone(direction, distance_movement, height, False)
            time.sleep(time_to_wait)
            linear_position = linear_position + distance_movement

            ss_pos = {
                'line_position': linear_position,
                'gps_position': self.gps.getCoordinate(),
                'signal_strength': self.wifi.getAVG2(time_to_wait)
            }
            ss_pos_list.append(ss_pos)

            if ss_pos['signal_strength'] > max_ss_pos['signal_strength']:
                max_ss_pos = ss_pos
                number_step_below_signal_strength = 0
            else:
                number_step_below_signal_strength += 1

            if number_step_below_signal_strength > limit_step_below_signal_strength:
                decreasing = True

        # move to the position with the highest signal strength
        distance = linear_position - max_ss_pos['line_position']
        self.move_drone(negative_direction, distance, height, False)

        # reset data
        decreasing = False
        number_step_below_signal_strength = 0
        linear_position = max_ss_pos['line_position']

        #move back
        while not decreasing:
            self.move_drone(negative_direction, distance_movement, height, False)
            time.sleep(time_to_wait)

            linear_position = linear_position - distance_movement

            ss_pos = {
                'line_position': linear_position,
                'gps_position': self.gps.getCoordinate(),
                'signal_strength': self.wifi.getAVG2(time_to_wait)
            }

            ss_pos_list.append(ss_pos)

            if ss_pos['signal_strength'] > max_ss_pos['signal_strength']:
                max_ss_pos = ss_pos
                number_step_below_signal_strength = 0
            else:
                number_step_below_signal_strength+=1

            if number_step_below_signal_strength > limit_step_below_signal_strength:
                decreasing = True


        # move to the position with the highest signal strength
        distance = max_ss_pos['line_position'] - linear_position
        self.move_drone(direction, distance, height, False)

    def scan_line(self, start_position, final_position, height):
        # Stop the scan if the phone is connected to the drone
        return self.move_and_scan(start_position, final_position, height, True)

    # Does not check for possible connections from phone.
    # Used only to move to the initial point for the search
    # And to return to the starting point when the search is done
    def move(self, start_position, final_position, height):
        self.move_and_scan(start_position,final_position,height,False)

    # Returns True if the MOVE method has been stopped due to phone connection (on request)
    # Returns False otherwise
    def move_and_scan(self, start_position, final_position, height, stop_on_phone_connection):
        #Move left/right to reach the right X coordinate
        if start_position[0] > final_position[0]:
            # Final position is on left side of the drone
            distance = start_position[0] - final_position[0]
            self.move_drone(DIRECTION_LEFT, distance, height, stop_on_phone_connection)
        elif start_position[0] < final_position[0]:
            # Final position is on right side of the drone
            distance = final_position[0] - start_position[0]
            self.move_drone(DIRECTION_RIGHT, distance, height, stop_on_phone_connection)

        # Check if I have to stop due to connection
        if stop_on_phone_connection and self.wifi.connected:
            return True

        #Move forward/backward to reach the right Y coordinate
        if start_position[1] > final_position[1]:
            # Final position is on the back side
            distance = start_position[1] - final_position[1]
            self.move_drone(DIRECTION_DOWN, distance, height, stop_on_phone_connection)
        elif start_position[1] < final_position[1]:
            # Final position is on front side
            distance = final_position[1] - start_position[1]
            self.move_drone(DIRECTION_UP, distance, height, stop_on_phone_connection)

        self.drone_position = final_position

        # Check if I have to stop due to connection
        if stop_on_phone_connection and self.wifi.connected:
            return True
        return False


    # Returns True if the MOVE method has been stopped due to phone connection (on request)
    # Returns False otherwise
    def move_drone(self, direction, distance, height, stop_on_phone_connection):
        print 'Request of movement of ', distance, ' in direction ',direction
        self.drone.hover()
        initial_position = self.gps.getCoordinate()
        # Check direction
        if direction == DIRECTION_LEFT:
            # Move left
            self.drone.move_left()
        if direction == DIRECTION_RIGHT:
            # Move right
            self.drone.move_right()
        if direction == DIRECTION_UP:
            # Move drone forward
            self.drone.move_forward()
        if direction == DIRECTION_DOWN:
            # Move drone backward
            self.drone.move_backward()
        print 'Moving...'
        #print 'Distance done: ',self.gps.getDistance(initial_position), 'from ', initial_position, ' to ', self.gps.getCoordinate()
        # keeps checking until the distance is greater on the one inserted or the phone is connected
        #if not stop_on_phone_connection:
        #    distance = -1 #TODO REMOVE TEST CASE distance=-1
        while distance > self.gps.getDistance(initial_position):
            time.sleep(1)
            #print stop_on_phone_connection, self.wifi.connected
            #print 'Distance done: ', self.gps.getDistance(initial_position)
            #if self.stop_search and not self.wifi.connected:
            #    print 'Stop moving'
            #    self.drone.hover()
            #    return False
            if stop_on_phone_connection and self.wifi.connected:
                print 'Phone connected to the raspberry!'
                self.drone.hover()
                return True
        print 'Reached Destination'
        self.drone.hover()
        return False

        # Stop the drone
        # drone.hover

    def opposite_direction(self, direction):
        if direction == DIRECTION_DOWN:
            return DIRECTION_UP
        elif direction == DIRECTION_UP:
            return DIRECTION_DOWN
        elif direction == DIRECTION_RIGHT:
            return DIRECTION_LEFT
        elif direction == DIRECTION_LEFT:
            return DIRECTION_RIGHT
        return None


#print 'Starting everything...'
#rect = Rectangle(100, 200, (60,0))
#rect.start()
