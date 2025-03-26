# Pre-Existing Modules
import socket
import sys
import pickle
import threading

# User-Defined Modules
from registration import registration_handling, deregistration_handling, REGISTERED, REGISTER_DENIED
from item_listing import ITEM_LISTED, LIST_DENIED

# Server Class (PRELIMINARY) --> Server behaviour will be migrated into this class
class Server:
    # Attributes
    registered_clients = {} # A dictionary containing the existing clients
    listed_items = {} # A dictionary containing the items that are up for auction
    
    # Methods
    def __init__(self):
        self.HOST = '0.0.0.0'
        self.UDP_PORT = 5000
        self.TCP_PORT = 6000
    
    def startServer(self):
        # Create a UDP Datagram Socket
        try:
            UDP_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"UDP Datagram Socket created...")
        except socket.error as e:
            print(f"Failed to create a UDP Datagram Socket.  Error code: {str(e[0])}, Message: {str(e[1])}")
            sys.exit()
        # Bind the newly created UDP Datagram Sokcet to an IP Address and Port Number
        try:
            UDP_sock.bind((self.HOST, self.UDP_PORT))
            print(f"UDP Datagram Socket binding to {self.HOST}:{self.UDP_PORT}...")
        except socket.error as e:
            print(f"Bind failed.  Error Code: {str(e[0])}, Message: {str(e[1])}")
            sys.exit()
        print(f"UDP Datagram Socket binding complete.")

        # Create a TCP Socket
        try:
            TCP_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print(f"Failed to create a TCP Socket. Error code: {str(e[0])}, Message: {str(e[1])}")
            sys.exit()
        # Bind the newly created TCP Socket to an IP Address and Port Number
        try:
            TCP_sock.bind((self.HOST, self.TCP_PORT))
            print(f"TCP Socket binding to {self.HOST}:{self.TCP_PORT}...")
        except socket.error as e:
            print(f"Bind failed.  Error Code: {str(e[0])}, Message: {str(e[1])}")
            sys.exit()
        print(f"TCP Socket binding complete.")

    # TODO: Move UDP and TCP listening behaviour here.
        
# End of Server Class

# server config
UDP_IP = "0.0.0.0"
UDP_PORT = 5000

# user dictionary
registeredUsers = {}

# TODO: Replace with registration_handling
def register (details):
    parts = details.split(" ")

    _, rq, name, role, ipAddr, udpSocket, tcpSocket = parts

    if len(parts) != 7:
        return f"INVALID COMMAND {rq}"
    elif name in registeredUsers:
        return f"REGISTERED-DENIED {rq} name already in use"
    else:
        registeredUsers[name] = {"rq": rq, "name": name, "role": role, "ipAddr": ipAddr, "udpSocket": udpSocket, "tcpSocket": tcpSocket}
        return f"REGISTERED {rq}"

# TODO: Replace with deregistration_handling
def deregister(details):
    parts = details.split(" ")

    _, rq, name = parts

    if len(parts) != 3:
        return f"INVALID COMMAND {rq}"
    elif name in registeredUsers:
        del registeredUsers[name]

def startServer():
    # create UDP server
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket Created")
    except socket.error as msg:
        print("Failed to create socket: " + str(msg))
        sys.exit()

    # bind server to port 5000
    try:
        sock.bind((UDP_IP, UDP_PORT))
        print("Socket bind to port 5000 completed")
    except socket.error as msg:
        print("Failed to bind to port 5000: " + str(msg))
        sys.exit()

    # server loop
    try:
        while 1:
            try:
                data, addr = sock.recvfrom(1024)  # Buffer size: 1024 bytes
                if not data:
                    continue
                print("Received data from client" + str(addr))

                message = pickle.loads(data)

                # Determine type of message
                if message.startswith("REGISTER"):
                    reply = register(message)
                elif message.startswith("DEREGISTER"):
                    reply = deregister(message)
                else:
                    reply = "INVALID REQUEST"


                sock.sendto(pickle.dumps(reply), addr)

            except socket.error as msg:
                print("Socket error: " + str(msg))

    except KeyboardInterrupt:
        print("\nServer shutting down...")

    finally:
        print("Closing socket...")
        sock.close()

if __name__ == "__main__":
    startServer()