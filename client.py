import socket
import sys
import pickle
import random
import time
import queue
from concurrent.futures import ThreadPoolExecutor

# User-Defined Modules
from registration import registration_input_handling, deregistration_input_handling
from item_listing import list_item_input_handling
from bids import bid_input_handling

class Client:
    # Attributes
    SERVER_IP = 'localhost'
    SERVER_UDP_PORT = 5000
    SERVER_TCP_PORT = 6000
    registration_rq = None

    # Methods
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.ip_address = '0.0.0.0'
        self.udp_port = None
        self.tcp_port = None
        self.udp_socket = None
        self.tcp_socket = None
        self.message_queue = queue.Queue() 
        self.pending_negotiation = None

        self.pool = ThreadPoolExecutor(max_workers=10) #TEST IF WE CAN ADD MORE WORKERS

    def handle_negotiation_request(self, message):
                print("\nNegotiation request received:", message)
                negotiation_choice = input("Enter [1] to Accept or [2] to Reject: ")
                
                if negotiation_choice == "1":
                    negotiation_label = "ACCEPT"
                    new_price = input("Enter new price: ")
                else:
                    negotiation_label = "REFUSE"
                    new_price = None

                item_name = message["Item_Name"]
                rq = random.randint(100, 900)
                
                request_data = {
                    "Type": "NEGOTIATE_RESPONSE",
                    "Server Response": negotiation_label,
                    "RQ#": rq,
                    "Item_Name": item_name,
                    "New Price": new_price,         
                }
                
                print("Sending negotiation response:", request_data)
                message = pickle.dumps(request_data)
                self.udp_socket.sendto(message, (self.SERVER_IP, self.SERVER_UDP_PORT))

    # This method will bind and create the UDP and TCP sockets for the client
    def startClient(self):
        if self.udp_socket or self.tcp_socket:
            print("Client already started.")
            return

        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.bind((self.ip_address, 0))
            self.udp_port = self.udp_socket.getsockname()[1]
            print(f"UDP socket created and bound to {self.ip_address}:{self.udp_port}")

        except socket.error as e:
            print(f"UDP socket error: {str(e)}")
            sys.exit()

        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.bind((self.ip_address, 0))
            self.tcp_socket.listen(5)
            self.tcp_port = self.tcp_socket.getsockname()[1]
            print(f"TCP socket created, bound, and listening on {self.ip_address}:{self.tcp_port}")
        except socket.error as e:
            print(f"TCP socket error: {str(e)}")
            sys.exit()

        self.pool.submit(self.tcpMessageReceiver)
        self.pool.submit(self.udpMessageReceiver)
    # END startClient

    def udpMessageSender(self, message):
            try:
                data = pickle.dumps(message)
                print(f"Message sent to server", message)
            except pickle.PicklingError as e:
                print(f"Faulty message to be sent to server at.  Error Code: {str(e)} \n")
                
            self.udp_socket.sendto(data, (self.SERVER_IP, self.SERVER_UDP_PORT))

    def udpMessageReceiver(self):
        print("UDP receiver thread started...")
        while True:
            try:
                data, server_address = self.udp_socket.recvfrom(1024)
                print(f"Message received from server at {server_address[0]}:{str(server_address[1])}... \n")

                message = pickle.loads(data)
                print(f"Message received from server: {message} \n")

                if isinstance(message, dict):
                    request_type = message.get("Type")
                    if request_type == "NEGOTIATE_REQ":
                        self.pending_negotiation = message

                        print(f"Press Enter key and select option [5] in main menu to respond")
                    else:
                        print(message)
                        
                        
                elif isinstance(message, str):
                    
                    print(message)
                else:
                    print(f"Received message from server: {message}")

            except pickle.UnpicklingError as e:
                print(f"Faulty message received from server. Error Code: {str(e)} \n")
            except Exception as e:
                print(f"Error in UDP receiver: {str(e)}")

    def tcpMessageReceiver(self):
        print("TCP listener is running...")
        #need to implement TCP handling logic

    def closeClient(self):
        if self.udp_socket:
            self.udp_socket.close()
            print("UDP Socket closed.")

        if self.tcp_socket:
            self.tcp_socket.close()
            print("TCP Socket closed.")

    def menu_select(self):
        while True:
            print("What would you like to do?\n")
            print("[0] Exit\n")
            print("[1] Register with the server\n")
            
            if self.role == "Seller":
                print(f"[2] List an item for auction\n")
            elif self.role == "Buyer":
                print(f"[2] Browse items\n")
                print(f"[3] Make an offer on an item\n")
            elif self.registration_rq is not None:
                print(f"[4] Deregister from server\n")

            if self.pending_negotiation is not None:
                print(f"[5] Respond to Negotiation request")

            input_selection = input("Press enter key then Enter selection: ")

            if input_selection == "0":
                print(f"Exiting the system!\n")
                break
            elif input_selection == "1":
                registration_input_handling(self.registration_rq, self.name, self.role, self.ip_address, self.udp_port, self.tcp_port, self.udp_socket, (self.SERVER_IP, self.SERVER_UDP_PORT))

            elif input_selection == "2" and self.role == "Seller":
                    print("List Item Selected:\n")
                
                    RQ = random.randint(100, 900)
                    item_name = input("Enter item name (or type 'exit' to quit): ")
                    if item_name.lower() == "exit":
                        break
                    item_description = input("Enter item description: ")
                    start_price = input("Enter start price ($): ")
                    duration = input("Enter duration (minutes): ")
                    # list_item_input_handling(RQ, item_name, item_description, start_price, duration, self.udp_socket, (self.SERVER_IP, self.SERVER_UDP_PORT))
                    #request_data = f"LIST_ITEM|{RQ}|{item_name}|{item_description}|{start_price}|{duration}"
                    #print(f'"Type": "LIST_ITEM"| "RQ#": "{RQ}"| "Item_Name": "{item_name}"| "Item_Description": "{item_description}"| "Start_Price": "{start_price}"| "Duration": "{duration}"')
                    request_data = {
                        "Type": "LIST_ITEM",
                        "RQ#": RQ,
                        "Item_Name": item_name,
                        "Item_Description": item_description,
                        "Start_Price": start_price,
                        "Duration": duration,
                    }
                    client.udpMessageSender(request_data)  
                       
                    
            elif input_selection == "2" and self.role == "Buyer":
                print("Browse items here")
                message="ALL_LIST"
                client.udpMessageSender(message)
                
            elif input_selection == "3" and self.role == "Buyer":
                print("Make offer here")
            elif input_selection == "4" and self.registration_rq is not None:

                deregistration_input_handling(self.registration_rq, self.name, self.udp_socket, (self.SERVER_IP, self.SERVER_UDP_PORT))
            elif input_selection=="5" and self.pending_negotiation is not None:
                self.handle_negotiation_request(self.pending_negotiation)
                self.pending_negotiation=None

           
    ## TCP Handling
    # TODO: Implement TCP Handling when modules are available
# END Client Class


# This class will define behaviour specific to seller clients
class Seller (Client):
    def __init__(self, name):
        super().__init__(name, "Seller")

class Buyer(Client):
    def __init__(self, name):
        super().__init__(name, "Buyer")

if __name__ == "__main__":
    print(f"Welcome to the Peer-to-Peer Auction System! \n")

    while True:
        name = input("Please enter your name: ").strip()
        if len(name) == 0:
            print(f"Invalid name! Name cannot be empty... \n")
        else:
            while True:
                name_confirmation = input(f"Are you sure you would like to be called {name}? [y/n] ").lower()
                if name_confirmation == "y":
                    break
                elif name_confirmation == "n":
                    break
                else:
                    print(f"Invalid selection! \n")
            if name_confirmation == "y":
                break

    while True:
        role = input("Are you a seller or a buyer? [s/b] ").lower()
        if role == "s":
            while True:
                role_confirmation = input(f"Are you sure you would like to be a seller? [y/n] ").lower()
                if role_confirmation == "y":
                    client = Seller(name)
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
                    client = Buyer(name)
                    break
                elif role_confirmation == "n":
                    break
                else:
                    print(f"Invalid selection! \n")
            if role_confirmation == "y":
                break
        else:
            print(f"Invalid role!  You should enter 's' to be a Seller or 'b' to be a Buyer... \n")

    client.startClient()
    client.menu_select()