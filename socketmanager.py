import socket
import sys
import thread
import time
import os

ID='Drone2'
RESCUER_PORT = 9119                                                     # Rescuer's app's port of listening
RPI_PORT = 9119                                                         # RPI's port of listening for buried phone's connection
RESCUER_ADDRESSES = ['192.168.0.4', '192.168.0.5', '192.168.0.6', '192.168.0.7', '192.168.0.8', '192.168.0.9','192.168.0.10']
BURIED_ADDRESS = ''                                                     # UNKNOWN HOST
PACKET_DIM = 4096                                                       # Packet length for receiving data
HOST = ''                                                 # TODO: fix host addr

RESCUER = 'rescuer'
BURIED = 'buried'

class SocketManager:
    findrone = None
    rescuer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                    # RPI will be the client
    rescuer_socket.settimeout(10000)
    server_socket = socket.socket()                                     # RPI will be the server
    buried_socket = {'phone': None, 'addr':None}
    rescuer_socket_stop_connection = False                              # If we want to stop the connect
    buried_socket_stop_connection = False
    rescuer_socket_connection_status = False                            # Connection status: False means not connected, True means connected
    buried_socket_connection_status = False

    rescuer_message_handler = None
    buried_message_handler = None
    phone_handler = None

    def __init__(self, rescuer_handler, buried_handler, phone_connection_handler):
        #my_address = socket.gethostname()                        # My host address
        #print 'Address:', my_address
        self.server_socket.bind((HOST, RPI_PORT))                 # Binding port and address to this socket
        #self.findrone = findrone

        self.rescuer_message_handler = rescuer_handler
        self.buried_message_handler = buried_handler
        self.phone_handler = phone_connection_handler

    def set_findrone(self, findrone):
        self.findrone = findrone

    def message_handler(self, sender, msg):
        msg_array = msg.split(':')
        command = msg_array[0]
        data_array = None
        if len(msg_array) > 1:
            data_array = msg_array[1]

        if sender == RESCUER:
            self.rescuer_message_handler(command, data_array)
        elif sender == BURIED:
            self.buried_message_handler(command, data_array)



    def send_data_rescueapp(self, message):
        while not self.rescuer_socket_stop_connection and not self.rescuer_socket_connection_status:    # Wait that the connection becomes available (or it stop if someone stopped the connection)
            pass
        if not self.rescuer_socket_stop_connection and self.rescuer_socket_connection_status:           # Check if the socket can send data
            #print 'Sending: ',message
            self.rescuer_socket.send(message+'\n')                                                           # Send data

    def send_data_buriedapp(self, message):
        while not self.buried_socket_stop_connection and not self.buried_socket_connection_status:      # Wait that the connection becomes available (or it stop if someone stopped the connection)
            pass
        if not self.buried_socket_stop_connection and self.buried_socket_connection_status:             # Check if the socket can send data
            self.buried_socket['phone'].send(message)                                                   # Send data

    def stop_connection_rescueapp(self):
        self.rescuer_socket_stop_connection = True                                                      # Set the flag to stop the connection to True
        self.rescuer_socket_connection_status = False                                                   # Set the status flag of the connection to False (not connected)
        self.rescuer_socket.shutdown(socket.SHUT_WR)                                                    # Stops the waiting recv function

    def stop_connection_buriedapp(self):
        self.buried_socket_stop_connection = True                                                       # Set the flag to stop the connection to True
        self.buried_socket_connection_status = False                                                    # Set the status flag of the connection to False (not connected)
        self.buried_socket['phone'].shutdown(socket.SHUT_WR)                                            # Stops the waiting recv function

    def start_connect_rescueapp(self):
        print 'starting thread for rescuer app connection..'
        thread.start_new_thread(self.thread_connection_rescueapp, ())   # Start thread to talk with rescuer app

    def start_connect_buriedapp(self):
        print 'starting thread for buried app connection..'
        thread.start_new_thread(self.thread_connection_buriedapp, ())   # Start thread to talk with buried app

    def thread_connection_rescueapp(self):
        data=''
        number_empty_messages = 0                                       # If the client stop the connection, the receiver starts to receive empty messages
        error = False                                                   # Tells us if the connection was closed due to an error
        rescuer_host = self.get_rescuer_host()
        print 'TRESCUER: connecting..'
        while not self.rescuer_socket_connection_status and not self.rescuer_socket_stop_connection: # Will try repeatedly until it will connect to the rescuer's app (unless the user wants to stop the connection)
            try:
                #time.sleep(1)
                self.rescuer_socket.connect((rescuer_host, RESCUER_PORT))    # Tries to connect to rescuer app (it waits until a result)
                print 'TRESCUER: connected!'
                self.rescuer_socket_connection_status = True                    # Connected!
                self.send_data_rescueapp(ID)

            except:
                #print 'TRESCUER: can\'t connect'
                try:
                    self.rescuer_socket.close()
                    self.rescuer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                except:
                    pass

        while not self.rescuer_socket_stop_connection:                  # If we can keep alive the connection
            try:
                #data = self.rescuer_socket.recv(PACKET_DIM)             # Listen for incoming packets
                data += self.rescuer_socket.recv(PACKET_DIM)

                if data == '':                                          # Check if message is empty
                    number_empty_messages+=1                            # We received empty message!
                    if number_empty_messages > 2:                       # If we received 3 consecutive messages, then stop the connection
                        self.rescuer_socket_stop_connection = True
                else:
                    while '\n' in data:
                        mess = data[:data.index('\n')]
                        data = data[data.index('\n')+1:]
                        if mess != '':
                            self.message_handler(RESCUER, mess)
                    #print 'TRESCUER: received data = ', data
                    #self.message_handler(RESCUER, data)
                    number_empty_messages = 0

            except Exception, err:
                print Exception, err
                error = True
                self.rescuer_socket_stop_connection = True              # If there is an error on the connection (or the host closed it)
                print 'Connection resetted by the peer or connection error'

        print 'TRESCUER: closing connection..'
        if not error:
            self.rescuer_socket.close()                                 # Close connection with rescuer app
        print 'TRESCUER: connection closed!'

    def thread_connection_buriedapp(self):
        data=''
        number_empty_mess = 0                                           # If the client stop the connection, the receiver starts to receive empty messages
        error = False                                                   # Tells us if the connection was closed due to an error
        print 'TBURIED: listening..'
        self.server_socket.listen(1)                                                          # Listen up to 1 connection TODO: Increment number of connection
        self.buried_socket['phone'], self.buried_socket['addr'] = self.server_socket.accept() # Accept connection, it returns the client socket and its address
        print 'TBURIED: device connected with addr: ', self.buried_socket['addr']
        self.phone_handler()
        self.buried_socket_connection_status = True                      # Connected!


        while not self.buried_socket_stop_connection:                    # If we can keep alive the connection
            try:
                data += self.buried_socket['phone'].recv(PACKET_DIM)     # Listen for incoming packets
                if data == '':                                           # Check if message is empty
                    print 'WARNING: Received empty message'
                    number_empty_mess+=1                                 # We received empty message!
                    if number_empty_mess > 9:                            # If we received 3 consecutive messages, then stop the connection
                        self.buried_socket_stop_connection = True
                else:
                    #print 'TBURIED: received data = "', data , '"'
                    while '\n' in data:
                        mess = data[:data.index('\n')]
                        data = data[data.index('\n')+1:]
                        if mess != '':
                            self.message_handler(BURIED, mess)
                    number_empty_mess = 0                                # Reset of the counter of empty messages received
            except Exception, err:
                print Exception, err
                self.buried_socket_stop_connection = True                # If there is an error, stop the connection (maybe the host crashed)
                error = True                                             # Set error flag to True
                print 'Connection resetted by the peer or connection error'

        print 'TBURIED: closing connection'
        if not error:                                                    # If there was en error, then the socket should be ended
            self.buried_socket['phone'].close()
        print 'TBURIED: connection closed!'

    def get_rescuer_host(self):
        host = ''
        while host == '':
            for rescuer_addr in RESCUER_ADDRESSES:
                if self.ping(rescuer_addr) == 0:
                    host = rescuer_addr
                    return host
        return host

    def ping(self, host):
        return os.system("ping -c 1 "+host)