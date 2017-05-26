from socketmanager import *
from flight_manager import *
import time

COMMAND_PHONE_FOUND = 'phone_found'
COMMAND_PHONE_CONNECTED = 'phone_connected'
COMMAND_PHONE_POSITION = 'phone_position'
DATA_LATITUDE = 'latitude'
DATA_LONGITUDE = 'longitude'

class Findrone:
    socket_manager = None
    flight_manager = None

    def __init__(self):
        pass
        self.socket_manager = SocketManager(self)
        self.socket_manager.start_connect_rescueapp()
        self.socket_manager.start_connect_buriedapp()

        #self.flight_manager = Flight()

    def buried_connected_handler(self):
        self.socket_manager.send_data_rescueapp(COMMAND_PHONE_CONNECTED)

    def buried_found_handler(self):
        self.socket_manager.send_data_rescueapp(COMMAND_PHONE_FOUND)


    def rescuer_socket_handler(self, command, data):
        if command == 'configure':
            data_array = data.split(';')
            width_array = data_array[0].split('=')
            width = int(width_array[1])
            length_array = data_array[1].split('=')
            length = int(length_array[1])
            position_array = data_array[2].split('=')
            position = int(position_array[1])

            self.flight_manager = Flight(width, length, (position, 0))
        if command == 'start':
            if self.flight_manager != None:
                self.flight_manager.start()
        if command == 'stop':
            if self.flight_manager != None:
                self.flight_manager.stop()


    def buried_socket_handler(self, command, data):
        if command == 'signal_strength':
            data_array = data.split(';')
            signal_array = data_array[0].split('=')
            signal = signal_array[1]

            if self.flight_manager != None:
                self.flight_manager.wifi.addSignal(float(signal), time.time())
        if command == 'position':
            data_array = data.split(';')
            longitute_array = data_array[0].split('=')
            longitude = longitute_array[1]
            latitude_array = data_array[1].split('=')
            latitude = latitude_array[1]

            self.socket_manager.send_data_rescueapp(COMMAND_PHONE_POSITION+':'+DATA_LONGITUDE+'='+longitude+';'+DATA_LATITUDE+'='+latitude)


