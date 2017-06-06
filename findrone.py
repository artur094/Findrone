from socketmanager import *
from flight_manager import *
from wifi_signal import *
import time
import thread

COMMAND_PHONE_FOUND = 'phone_found'
COMMAND_PHONE_CONNECTED = 'phone_connected'
COMMAND_PHONE_POSITION = 'phone_position'
COMMAND_DRONE_POSITION = ''
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
    start = False

    def __init__(self):
        self.wifi_manager = WifiSignal()
        self.socket_manager = SocketManager(self.rescuer_socket_handler, self.buried_socket_handler, self.buried_connected_handler)
        self.socket_manager.start_connect_rescueapp()
        self.socket_manager.start_connect_buriedapp()

        while not self.start:
            pass

        self.flight_manager.start()
        self.finished = True
        #TODO: handle end of search

        #self.flight_manager = Flight()

    def send_gps_position_to_rescuers(self):
        while not self.finished:
            self.socket_manager.send_data_rescueapp(COMMAND_DRONE_POSITION+':'+DATA_LONGITUDE+'='+str(self.flight_manager.gps.getCoordinate()[1])+';'+DATA_LATITUDE+'='+str(self.flight_manager.gps.getCoordinate()[0]))
            time.sleep(0.5)

    def buried_connected_handler(self):
        print 'Setting wifi connected to True'
        self.wifi_manager.connected = True
        print 'Sending data to rescuers'
        self.socket_manager.send_data_rescueapp(COMMAND_PHONE_CONNECTED)

    def buried_found_handler(self):
        print 'Phone found!'
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
                    data_dict[DATA_WIDTH] = int(item_array[1])
                if item_array[0] == DATA_LENGTH:
                    data_dict[DATA_LENGTH] = int(item_array[1])
                if item_array[0] == DATA_POSITION:
                    data_dict[DATA_POSITION] = int(item_array[1])

            self.flight_manager = Flight(data_dict[DATA_WIDTH], data_dict[DATA_LENGTH], (data_dict[DATA_POSITION], 0), self.wifi_manager, self.buried_found_handler)
        if command == 'start':
            print 'Received start'
            if self.flight_manager != None:
                print 'Setting flag to start'
                thread.start_new_thread(self.send_gps_position_to_rescuers, ())
                self.start = True
                #self.flight_manager.start()
        if command == 'stop':
            print 'Received stop'
            if self.flight_manager != None:
                print 'Stopping the search'
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
                DATA_ACCURACY: '0',
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
                if item_array[0] == DATA_ACCURACY and len(item_array)>1:
                    if item_array[0] == DATA_ACCURACY:
                        data_dict[DATA_ACCURACY] = item_array[1]


            self.socket_manager.send_data_rescueapp(COMMAND_PHONE_POSITION+':'+DATA_LONGITUDE+'='+data_dict[DATA_LONGITUDE]+';'+DATA_LATITUDE+'='+data_dict[DATA_LATITUDE]+';'+ DATA_ACCURACY+'='+data_dict[DATA_ACCURACY])

    def test(self):
        print 'Starting test case: BURIED INTEGRATION'
        print 'Initializing flight manager...'
        self.flight_manager = Flight(0,0,(0,0), self.wifi_manager, self.buried_found_handler)
        print 'Done!'
        print 'Sending move action to drone...'
        found = self.flight_manager.move_drone(DIRECTION_UP, 5, 1, True)

        if found:
            'Phone Connected!'
        else:
            'Phone not found...'
        print 'END TEST CASE'


findrone = Findrone()

while not findrone.finished:
    pass
#tsleep = 2
#
#while(not findrone.finished):
#    time.sleep(tsleep)
#    print 'Signal AVG: ',findrone.wifi_manager.getAVG2(tsleep)
#    print 'Length of Signal List: ', len(findrone.wifi_manager.signal_list)