# Pre-Existing Modules
import socket
import sys
import pickle
import threading

# User-Defined Modules
from registration import REGISTER, DE_REGISTER

class Client:
    # Attributes
    SERVER_IP = 'localhost' # The IP address of the server
    SERVER_UDP_PORT = 5000 # The UDP port number of the server
    SERVER_TCP_PORT = 6000 # The TCP port number of the server

    registration_rq = None # A variable that will keep track of registration-related communications, set by the server.

    # Methods
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.ip_address = '0.0.0.0'
        self.udp_port = None
        self.tcp_port = None
        self.udp_socket = None
        self.tcp_socket = None
    
    def startClient(self):
        # Create a UDP Datagram Socket
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"UDP Datagram Socket created... \n")
        except socket.error as e:
            print(f"Failed to create a UDP Datagram Socket.  Error code: {str(e[0])}, Message: {str(e[1])} \n")
            sys.exit()
        # Bind the newly created UDP Datagram Sokcet to an IP Address and Port Number
        try:
            self.udp_socket.bind((self.ip_address, 0)) # Putting 0 means that an avilable port will be found
            print(f"UDP Datagram Socket binding... \n")
        except socket.error as e:
            print(f"Bind failed.  Error Code: {str(e[0])}, Message: {str(e[1])} \n")
            sys.exit()
        # Set the client's UDP port number
        self.udp_port = self.udp_socket.getsockname()[1]
        print(f"UDP Datagram Socket binding complete.  Bound at {self.ip_address}:{self.udp_port} \n")

        # Create a TCP Socket
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print(f"Failed to create a TCP Socket. Error code: {str(e[0])}, Message: {str(e[1])} \n")
            sys.exit()
        # Bind the newly created TCP Socket to an IP Address and Port Number
        try:
            self.tcp_socket.bind((self.ip_address, 0)) # Putting 0 means that an avilable port will be found
            print(f"TCP Socket binding... \n")
        except socket.error as e:
            print(f"Bind failed.  Error Code: {str(e[0])}, Message: {str(e[1])} \n")
            sys.exit()
        self.tcp_port = self.tcp_socket.getsockname()[1]
        print(f"TCP Socket binding complete.  Bound at {self.ip_address}:{self.tcp_port} \n")


# This class will define behaviour specific to seller clients
class Seller (Client):
    def __init__(self, name):
        super().__init__(name, "Seller")

# This class will define behaviour specific to buyer clients
class Buyer (Client):
    def __init__(self, name):
        super().__init__(name, "Buyer")

if __name__ == "__main__":
    print(f"Welcome to the Peer-to-Peer Auction System! \n")

    # Gather the client's name and role
    while True:
        name = input("Please enter your name: ").strip()
        if len(name) == 0:
            print(f"Invalid name! Name cannot be empty... \n")
        else:
            while True:
                name_confirmation = input(f"Are you sure you would like to be called {name}? [y/n]").lower()
                if name_confirmation == "y":
                    break
                elif name_confirmation == "n":
                    break
                else:
                    print(f"Invalid selection! \n")
            if name_confirmation == "y":
                break
    
    while True:
        role = input("Are you a seller or a buyer? [s/b]").lower()
        if role == "s":
            while True:
                role_confirmation = input(f"Are you sure you would like to be a seller? [y/n]").lower()
                if role_confirmation == "y":
                    break
                elif role_confirmation == "n":
                    break
                else:
                    print(f"Invalid selection! \n")
            if role_confirmation == "y":
                break
        elif role == "b":
            while True:
                role_confirmation = input(f"Are you sure you would like to be a buyer? [y/n]").lower()
                if role_confirmation == "y":
                    break
                elif role_confirmation == "n":
                    break
                else:
                    print(f"Invalid selection! \n")
            if role_confirmation == "y":
                break
        else:
            print(f"Invalid role!  You should enter 's' to be a Seller or 'b' to be a Buyer... \n")
    
    # Create the client object
    if(role == "s"):
        client = Seller(name)
    elif(role == "b"):
        client = Buyer(name)
    
    # Create the UDP and TCP sockets for the client object
    client.startClient()