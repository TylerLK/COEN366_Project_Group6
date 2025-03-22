# Pre-Existing Modules
import socket
import sys
import pickle

# User-defined functions
from registration import registration_handling, deregistration_handling, REGISTERED, REGISTER_DENIED

# Server Class (PRELIMINARY) --> Server behaviour will be migrated into this class
class Server:
    # Attributes
    registered_clients = {}
    
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

        while True:
            # TODO: Move UDP listening behaviour here.
            print(f"Receiving messages from clients...")
        
        # TODO: Create a TCP socket, bind the socket, and create listening behaviour
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
        while True:
            try:
                data, addr = sock.recvfrom(1024)  # Buffer size: 1024 bytes
                if not data:
                    continue
                print("Received data from client" + str(addr))

                message = data.decode()

                # Determine type of message
                if message.startswith("REGISTER"):
                    reply = register (message)
                elif message.startswith("DEREGISTER"):
                    reply = deregister(message)
                else:
                    reply = "INVALID REQUEST"


                sock.sendto(reply.encode(), addr)

            except socket.error as msg:
                print("Socket error: " + str(msg))

    except KeyboardInterrupt:
        print("\nServer shutting down...")

    finally:
        print("Closing socket...")
        sock.close()

if __name__ == "__main__":
    startServer()