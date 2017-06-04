from socketmanager import *
from flight_manager import *
from wifi_signal import *
import time

COMMAND_PHONE_FOUND = 'phone_found'
COMMAND_PHONE_CONNECTED = 'phone_connected'
COMMAND_PHONE_POSITION = 'phone_position'
DATA_LATITUDE = 'latitude'
DATA_LONGITUDE = 'longitude'
DATA_ACCURACY = 'accuracy'
DATA_WIDTH = 'width'
DATA_LENGTH = 'length'
DATA_POSITION = 'position'


class Findrone:
    socket_manager = None
    flight_manager = None
    wifi_manager = None
    finished = False

    def __init__(self):
        self.wifi_manager = WifiSignal()
        self.socket_manager = SocketManager(self.rescuer_socket_handler, self.buried_socket_handler)
        self.socket_manager.start_connect_rescueapp()
        self.socket_manager.start_connect_buriedapp()

        #self.flight_manager = Flight()

    def buried_connected_handler(self):
        self.wifi_manager.connected = True
        self.socket_manager.send_data_rescueapp(COMMAND_PHONE_CONNECTED)

    def buried_found_handler(self):
        self.socket_manager.send_data_rescueapp(COMMAND_PHONE_FOUND)

    def rescuer_socket_handler(self, command, data):
        print 'From rescuer: ', command, ': ', data
        if command == 'configure':
            data_array = data.split(';')

            data_dict = {
                DATA_WIDTH: '',
                DATA_LENGTH: '',
                DATA_POSITION: ''
            }

            for item in data_array:
                item_array = item.split('=')
                if item_array[0] == DATA_WIDTH:
                    data_dict[DATA_WIDTH] = item_array[1]
                if item_array[0] == DATA_LENGTH:
                    data_dict[DATA_LENGTH] = item_array[1]
                if item_array[0] == DATA_POSITION:
                    data_dict[DATA_POSITION] = item_array[1]

            self.flight_manager = Flight(data_dict[DATA_WIDTH], data_dict[DATA_LENGTH], (data_dict[DATA_POSITION], 0), self.wifi_manager, self.buried_found_handler)
        if command == 'start':
            if self.flight_manager != None:
                self.flight_manager.start()
        if command == 'stop':
            if self.flight_manager != None:
                self.flight_manager.stop()


    # 'signal_strength:value=-40'
    # 'position:longitude=20.00000;latitude=20.00000;accuracy=14.0'
    def buried_socket_handler(self, command, data):
        #print 'From buried: ', command, ': ', data
        if command == 'signal_strength':
            data_array = data.split(';')
            signal_array = data_array[0].split('=')
            signal = signal_array[1]

            #print 'Signal Strength received: ',signal

            try:
                float(signal)
            except:
                print 'ERROR converting this signal: "',signal,'"'
                print 'Full data here:\n"',data,'"\n'
                return

            self.wifi_manager.addSignal(float(signal), time.time())
            #if self.flight_manager != None:
            #    self.flight_manager.wifi.addSignal(float(signal), time.time())

        if command == 'position':
            data_dict = {
                DATA_ACCURACY: '',
                DATA_LATITUDE: '',
                DATA_LONGITUDE: ''
            }

            data_array = data.split(';')

            for item in data_array:
                item_array = item.split('=')
                if item_array[0] == DATA_LONGITUDE:
                    data_dict[DATA_LONGITUDE] = item_array[1]
                if item_array[0] == DATA_LATITUDE:
                    data_dict[DATA_LATITUDE] = item_array[1]
                if item_array[0] == DATA_ACCURACY:
                    data_dict[DATA_ACCURACY] = item_array[1]

            self.socket_manager.send_data_rescueapp(COMMAND_PHONE_POSITION+':'+DATA_LONGITUDE+'='+data_dict[DATA_LONGITUDE]+';'+DATA_LATITUDE+'='+data_dict[DATA_LATITUDE]+';'+ DATA_ACCURACY+'='+data_dict[DATA_ACCURACY])


findrone = Findrone()
tsleep = 2

while(not findrone.finished):
    time.sleep(tsleep)
    print 'Signal AVG: ',findrone.wifi_manager.getAVG2(tsleep)
    print 'Length of Signal List: ', len(findrone.wifi_manager.signal_list)