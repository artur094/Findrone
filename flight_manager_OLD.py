import math, time
from gps_module import GPSModule
from wifi_signal import WifiSignal

DIRECTION_LEFT = 'left'
DIRECTION_RIGHT = 'right'
DIRECTION_UP = 'up'
DIRECTION_DOWN = 'down'
TIME_TO_WAIT_BEFORE_LAND = 60 # 1 Min

class Flight:
    phone_found_handler = None

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
    gps = GPSModule()
    wifi = None

    start_direction = 'left'

    #connected = False       # Says if a phone is connected to the drone through TCP connection

    # Width: Meters of the width of the rectangle
    # Length: Meters of the length of the rectangle
    # Position: Coordinates in meters of the position of the drone
    def __init__(self, width, length, position, wifi_manager, phone_handler):
        self.phone_found_handler = phone_handler
        self.width = width
        self.length = length
        self.wifi = wifi_manager

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
        print 'Starting the algorithm of search'
        if self.w[0] > self.l[1]:
            print 'Drone will start on bottom side'
            if self.start_direction == 'left':
                self.start_left()
            else:
                self.start_right()
        else:
            print 'Drone will start on left/righ side'
            if self.start_direction == 'left':
                self.start_left_on_length_side()
            else:
                self.start_right_on_length_side()

        # When I execute this code means:
        # No phone found --> I'm already at home --> land
        # Phone found --> start searching it
        # To check: enough to check the connected variable

        if self.wifi.connected == True:
            self.start_follow_wifi_signal()
            #Now I should be in the location of the buried person
            #Send notification
            #Wait one minute (or more)
            time.sleep(TIME_TO_WAIT_BEFORE_LAND)
        else:
            #Job done!
            pass

        #drone.land()
        #End... I hope for a good job!

    #TODO: write stop function
    def stop(self):
        pass

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
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
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
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
                return

            #Go down
            next_position = (self.drone_position[0], self.orig[0] + self.delta_l)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
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
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
                return

                #Scanned 5 * delta_w meters in width (assuming delta_w = 2, it's 10 meters)

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
        # TODO: fix last scan
        while self.drone_position[0] >= self.orig[0]:
            # Go upper
            next_position = (self.drone_position[0], self.l[1] - self.delta_l)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            found_wifi = self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
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
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
                return

            # Go down
            next_position = (self.drone_position[0], self.orig[0] + self.delta_l)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
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
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
                return

        # Need to check in detail if drone has covered all the area
        # If no WiFi connection has been found, then go home
        self.move(self.drone_position, self.initial_drone_position, self.height)  # TODO: avoid crash between drones!

    def start_left_on_length_side(self):
        print 'Drone position: ', self.drone_position[0], ', ', self.drone_position[1]
        # Starting position for the scan
        starting_point = (self.orig[0] + self.delta_w, self.orig[0]+self.delta_l)
        print 'Move to coordinate: ', starting_point[0], ', ', starting_point[1]

        # Move to the beginning
        self.move(self.drone_position, starting_point, self.height)

        # Start the scan
        # TODO: fix last scan
        while self.drone_position[1] < self.l[1]:
            # Go left
            next_position = (self.w[0] - self.delta_w, self.drone_position[1])
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            found_wifi = self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
                return

            up_movement = min(2 * self.delta_l, self.l[1] - self.drone_position[1])

            # Check if I can move up
            if self.drone_position[1] >= (self.l[1] - self.delta_l):
                break

            # Go up
            next_position = (self.drone_position[0], self.drone_position[1] + up_movement)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
                return

            # Go right
            next_position = (self.orig[0] + self.delta_w, self.drone_position[1])
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
                return

            up_movement = min(2 * self.delta_l, self.l[1] - self.delta_l)

            # Check if I can move up
            if self.drone_position[1] >= (self.l[1] - self.delta_l):
                break

            # Go up
            next_position = (self.drone_position[0], self.drone_position[1] + up_movement)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
                return

        # Need to check in detail if drone has covered all the area
        # If no WiFi connection has been found, then go home
        self.move(self.drone_position, self.initial_drone_position, self.height)  # TODO: avoid crash between drones!

    def start_right_on_length_side(self):
        print 'Drone position: ', self.drone_position[0], ', ', self.drone_position[1]
        # Starting position for the scan
        starting_point = (self.w[0] - self.delta_w, self.orig[0]+self.delta_l)
        print 'Move to coordinate: ', starting_point[0], ', ', starting_point[1]

        # Move to the beginning
        self.move(self.drone_position, starting_point, self.height)

        # Start the scan
        # TODO: fix last scan
        while self.drone_position[1] < self.l[1]:
            # Go right
            next_position = (self.orig[0] + self.delta_w, self.drone_position[1])
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            found_wifi = self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
                return

            up_movement = min(2 * self.delta_l, self.l[1] - self.drone_position[1])

            # Check if I can move up
            if self.drone_position[1] >= (self.l[1] - self.delta_l):
                break

            # Go up
            next_position = (self.drone_position[0], self.drone_position[1] + up_movement)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
                return

            # Go left
            next_position = (self.w[0] - self.delta_w, self.drone_position[1])
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
                return

            up_movement = min(2 * self.delta_l, self.l[1] - self.delta_l)

            # Check if I can move up
            if self.drone_position[1] >= (self.l[1] - self.delta_l):
                break

            # Go up
            next_position = (self.drone_position[0], self.drone_position[1] + up_movement)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.start_follow_wifi_signal()
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
            'line_position',linear_position,
            'gps_position', self.gps.getCoordinate(),
            'signal_strength', self.wifi.getDistance()
        }
        ss_pos_list.append(ss_pos)
        max_ss_pos = ss_pos

        #move forward
        while not decreasing:
            self.move_drone(direction, distance_movement, height, False)
            time.sleep(time_to_wait)
            linear_position = linear_position + distance_movement

            ss_pos = {
                'line_position', linear_position,
                'gps_position', self.gps.getCoordinate(),
                'signal_strength', self.wifi.getAVG2(time_to_wait)
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
                'line_position', linear_position,
                'gps_position', self.gps.getCoordinate(),
                'signal_strength', self.wifi.AVG2(time_to_wait)
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
        initial_position = self.gps.getCoordinate()
        # Check direction
        if direction == DIRECTION_LEFT:
            # Move left
            # drone.move_left()
            pass
        if direction == DIRECTION_RIGHT:
            # Move right
            # drone.move_right()
            pass
        if direction == DIRECTION_UP:
            # Move drone forward
            # drone.move_forward()
            pass
        if direction == DIRECTION_DOWN:
            # Move drone backward
            # drone.move_backward()
            pass

        # keeps checking until the distance is greater on the one inserted or the phone is connected
        while distance < self.gps.getDistance(initial_position):
            if stop_on_phone_connection and self.wifi.connected:
                return True
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
