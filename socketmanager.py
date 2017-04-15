import socket
import sys
import thread

RESCUER_PORT = 9119                                                     # Rescuer's app's port of listening
RPI_PORT = 9119                                                         # RPI's port of listening for buried phone's connection
RESCUER_ADDRESS = '192.168.1.8'                                         # TODO: fix to 192.168.0.250
BURIED_ADDRESS = ''                                                     # UNKNOWN HOST
PACKET_DIM = 1024                                                       # Packet length for receiving data

class SocketManager:
    rescuer_socket = socket.socket()                                    # RPI will be the client
    server_socket = socket.socket()                                     # RPI will be the server
    buried_socket = {'phone': None, 'addr':None}
    rescuer_socket_stop_connection = False                              # If we want to stop the connect
    buried_socket_stop_connection = False
    rescuer_socket_connection_status = False                            # Connection status: False means not connected, True means connected
    buried_socket_connection_status = False

    def __init__(self):
        my_address = socket.gethostname()                               # My host address
        self.server_socket.bind((my_address, RPI_PORT))                 # Binding port and address to this socket
        pass

    def send_data_rescueapp(self, message):
        while not self.rescuer_socket_stop_connection and not self.rescuer_socket_connection_status:    # Wait that the connection becomes available (or it stop if someone stopped the connection)
            pass
        if not self.rescuer_socket_stop_connection and self.rescuer_socket_connection_status:           # Check if the socket can send data
            self.rescuer_socket.send(message)                                                           # Send data

    def send_data_buriedapp(self, message):
        while not self.buried_socket_stop_connection and not self.buried_socket_connection_status:      # Wait that the connection becomes available (or it stop if someone stopped the connection)
            pass
        if not self.buried_socket_stop_connection and self.buried_socket_connection_status:             # Check if the socket can send data
            self.buried_socket['phone'].send(message)                                                    # Send data

    def stop_connection_rescueapp(self):
        self.rescuer_socket_stop_connection = True
        self.rescuer_socket_connection_status = False
        self.rescuer_socket.shutdown(socket.SHUT_WR)

    def stop_connection_buriedapp(self):
        self.buried_socket_stop_connection = True
        self.buried_socket_connection_status = False
        self.buried_socket['phone'].shutdown(socket.SHUT_WR)

    def start_connect_rescueapp(self):
        print 'starting thread for rescuer app connection..'
        thread.start_new_thread(self.thread_connection_rescueapp, ())   # Start thread to talk with rescuer app

    def start_connect_buriedapp(self):
        print 'starting thread for buried app connection..'
        thread.start_new_thread(self.thread_connection_buriedapp, ())   # Start thread to talk with buried app

    def thread_connection_rescueapp(self):
        number_empty_messages = 0                                       # If the client stop the connection, the receiver starts to receive empty messages
        error = False                                                   # Tells us if the connection was closed due to an error
        print 'TRESCUER: connecting..'
        # TODO: check better if it crashes when can't find the server
        self.rescuer_socket.connect((RESCUER_ADDRESS, RESCUER_PORT))    # Tries to connect to rescuer app (it waits until a result)
        print 'TRESCUER: connected!'
        self.rescuer_socket_connection_status = True

        while not self.rescuer_socket_stop_connection:                  # If we can keep alive the connection
            try:
                data = self.rescuer_socket.recv(PACKET_DIM)             # Listen for incoming packets

                if data == '':                                          # Check if message is empty
                    number_empty_messages+=1                            # We received empty message!
                    if number_empty_messages > 2:                       # If we received 3 consecutive messages, then stop the connection
                        self.rescuer_socket_stop_connection = True
                else:
                    print 'TRESCUER: received data = ', data
                    number_empty_messages = 0
            except:
                self.rescuer_socket_stop_connection = True              # If there is an error on the connection (or the host closed it)
                print 'Connection resetted by the peer or connection error'

        print 'TRESCUER: closing connection..'
        if not error:
            self.rescuer_socket.close()                                 # Close connection with rescuer app
        print 'TRESCUER: connection closed!'

    def thread_connection_buriedapp(self):
        number_empty_mess = 0                                           # If the client stop the connection, the receiver starts to receive empty messages
        error = False                                                   # Tells us if the connection was closed due to an error
        print 'TBURIED: listening..'
        self.server_socket.listen(1)                                                          # Listen up to 1 connection TODO: Increment number of connection
        self.buried_socket['phone'], self.buried_socket['addr'] = self.server_socket.accept() # Accept connection, it returns the client socket and its address
        print 'TBURIED: device connected with addr: ', self.buried_socket['addr']
        self.buried_socket_connection_status = True

        while not self.buried_socket_stop_connection:                    # If we can keep alive the connection
            try:
                data = self.buried_socket['phone'].recv(PACKET_DIM)      # Listen for incoming packets
                if data == '':                                           # Check if message is empty
                    number_empty_mess+=1                                 # We received empty message!
                    if number_empty_mess > 2:                            # If we received 3 consecutive messages, then stop the connection
                        self.buried_socket_stop_connection = True
                else:
                    print 'TRESCUER: received data = ', data
                    number_empty_mess = 0
            except:
                self.buried_socket_stop_connection = True
                error = True
                print 'Connection resetted by the peer or connection error'

        print 'TBURIED: closing connection'
        if not error:
            self.buried_socket.close()
        print 'TBURIED: connection closed!'



socket_manager = SocketManager()
#socket_manager.start_connect_rescueapp()
socket_manager.start_connect_buriedapp()
socket_manager.send_data_buriedapp('Where are you charlie?')


while(True):pass