# Pre-Existing Modules
import socket
import sys
import pickle
import threading

# User-Defined Modules
from registration import registration_input_handling, deregistration_input_handling

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
            print(f"Failed to create a UDP Datagram Socket.  Error: {str(e)} \n")
            sys.exit()
        # Bind the newly created UDP Datagram Sokcet to an IP Address and Port Number
        try:
            self.udp_socket.bind((self.ip_address, 0)) # Putting 0 means that an avilable port will be found
            print(f"UDP Datagram Socket binding... \n")
        except socket.error as e:
            print(f"Bind failed.  Error: {str(e)} \n")
            sys.exit()
        # Set the client's UDP port number
        self.udp_port = self.udp_socket.getsockname()[1]
        print(f"UDP Datagram Socket binding complete.  Bound at {self.ip_address}:{self.udp_port} \n")
        # Start a thread to send UDP messages to the server
        udp_sender_thread = threading.Thread(target=self.udpMessageSender, args=())
        udp_sender_thread.start()
        # Start a thread to receive UDP messages from the server
        udp_receiver_thread = threading.Thread(target=self.udpMessageReceiver, args=())
        udp_receiver_thread.start()

        # Create a TCP Socket
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print(f"Failed to create a TCP Socket. Error: {str(e)} \n")
            sys.exit()
        # Bind the newly created TCP Socket to an IP Address and Port Number
        try:
            self.tcp_socket.bind((self.ip_address, 0)) # Putting 0 means that an avilable port will be found
            print(f"TCP Socket binding... \n")
        except socket.error as e:
            print(f"Bind failed.  Error: {str(e)} \n")
            sys.exit()
        self.tcp_port = self.tcp_socket.getsockname()[1]
        print(f"TCP Socket binding complete.  Bound at {self.ip_address}:{self.tcp_port} \n")
    
    ## UDP Handling
    # This method will allow clients to send messages to the server
    def udpMessageSender(self):
        while True:
            message = input("Your message to the server: ").strip()

            try:
                # Attempt to serialize the message to be sent to the server.
                data = pickle.dumps(message)
            except pickle.PicklingError as e:
                print(f"Faulty message to be sent to server at.  Error Code: {str(e)} \n")
                break

            self.udp_socket.sendto(data, (self.SERVER_IP, self.SERVER_UDP_PORT))

    # This method will a llow clients to receive messages from the server
    def udpMessageReceiver(self):
        while True:
            try:
                data, server_address = self.udp_socket.recvfrom(1024)
                print(f"Message received from a client at {server_address[0]}:{str(server_address[1])}... \n")

                try:
                    # Attempt to deserialize the message sent by a client.
                    message = pickle.loads(data)
                    print(f"Message received from server: {message} \n")
                except pickle.UnpicklingError as e:
                    print(f"Faulty message received from server at {server_address[0]}:{str(server_address[1])}.  Error Code: {str(e)} \n")
                    error_message = f"Error occured while processing your message... \n"
                    self.UDP_SOCKET.sendto(pickle.dumps(error_message), server_address)
                    continue

                # TODO: Change this behaviour to actually handle the message correctly.

            except Exception as e:
                print(f"Error: {e}") 

    ## TCP Handling
    # TODO: Implement TCP Handling when modules are available
# END Client Class


# This class will define behaviour specific to seller clients
class Seller (Client):
    def __init__(self, name):
        super().__init__(name, "Seller")
# END Seller Class

# This class will define behaviour specific to buyer clients
class Buyer (Client):
    def __init__(self, name):
        super().__init__(name, "Buyer")
# END Buyer Class

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
    print("\n")
    print("======================================================================================================")
    print(f"Network Configuration \n")
    client.startClient()
    print("======================================================================================================")
    
# TODO: Implement all the possibilities for the clients once all methods have been modulated and implemented.
    # # Selection menu for the client
    # while True:
    #     print("\n")
    #     print("======================================================================================================")
    #     print(f"{client.role} Selection Menu")
    #     print("======================================================================================================")
    #     print(f"What would like to do? \n")      
    #     print("[0] Exit the system. \n")
    #     print(f"[1] Register with the server. \n")
    #     if(client.registration_rq != None):
    #         print(f"[2] Deregister from the server. \n")
    #     print("\n")

    #     # Get the client's selection
    #     input_selection = input(f"Please enter the number corresponding to your selection: ").strip()
        
    #     if input_selection == "1":
    #         # Call the registration method to register with the server
    #         registration_input_handling(client)
    #     elif input_selection == "2":
    #         # Call the deregistration method to deregister from the server
    #         deregistration_input_handling(client)
    #     elif input_selection == "0":
    #         print(f"Exiting the Peer-to-Peer Auction System.  Have a nice day! \n")
    #         break
    #     else:
    #         print(f"Invalid selection! \n")