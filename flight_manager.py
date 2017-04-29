import math

class Rectangle:
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
    drone_position = (0,0)

    start_direction = 'left'

    # Width: Meters of the width of the rectangle
    # Length: Meters of the length of the rectangle
    # Position: Coordinates in meters of the position of the drone
    def __init__(self, width, length, position):
        self.width = width
        self.length = length

        self.w = (width, 0)
        self.l = (0, length)
        self.wl = (width, length)

        self.drone_position = position
        self.initial_drone_position = (position[0], position[1])

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
                self.search_wifi()
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
                self.search_wifi()
                return

            #Go down
            next_position = (self.drone_position[0], self.orig[0] + self.delta_l)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.search_wifi()
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
                self.search_wifi()
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
                self.search_wifi()
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
                self.search_wifi()
                return

            # Go down
            next_position = (self.drone_position[0], self.orig[0] + self.delta_l)
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.search_wifi()
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
                self.search_wifi()
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
                self.search_wifi()
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
                self.search_wifi()
                return

            # Go right
            next_position = (self.orig[0] + self.delta_w, self.drone_position[1])
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.search_wifi()
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
                self.search_wifi()
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
                self.search_wifi()
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
                self.search_wifi()
                return

            # Go left
            next_position = (self.w[0] - self.delta_w, self.drone_position[1])
            print 'Scan to coordinate: ', next_position[0], ', ', next_position[1]
            self.scan_line(self.drone_position, next_position, self.height)

            # If the drone has found a TCP connection, the start to search the wifi signal
            if found_wifi == True:
                # Start specific algorithm of search
                self.search_wifi()
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
                self.search_wifi()
                return

        # Need to check in detail if drone has covered all the area
        # If no WiFi connection has been found, then go home
        self.move(self.drone_position, self.initial_drone_position, self.height)  # TODO: avoid crash between drones!

    def scan_line(self, start_position, final_position, height):
        self.move(start_position, final_position, height)
        return False

    def search_wifi(self):
        pass

    def move(self, start_position, final_position, height):
        self.drone_position = final_position


print 'Starting everything...'
rect = Rectangle(100, 200, (60,0))
rect.start()
