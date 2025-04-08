import socket
import sys
import pickle
import random
from concurrent.futures import ThreadPoolExecutor

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# User-Defined Modules
from registration import registration_input_handling, deregistration_input_handling

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
 self.pool = ThreadPoolExecutor(max_workers=10) #TEST IF WE CAN ADD MORE WORKERS
    def handle_negotiation_request(self, message):
                print("\nNegotiation request received:", message)
                negotiation_choice = input("Enter [1] to Accept or [2] to Reject: ")
                
                if negotiation_choice == "1":
                    negotiation_label = "ACCEPT"
                    new_price = input("Enter new price: ")
                else:
                    negotiation_label = "REFUSE"
                    new_price = "REJECT"

                item_name = message["Item_Name"]
                rq = message.get("RQ#", random.randint(100, 900))
                
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

    def udpMessageSender(self):
        while True:
            message = input("Your message to the server: ").strip()
            try:
                data = pickle.dumps(message)
            except pickle.PicklingError as e:
                print(f"Faulty message to be sent to server at.  Error Code: {str(e)} \n")
                break
            self.udp_socket.sendto(data, (self.SERVER_IP, self.SERVER_UDP_PORT))

    def udpMessageReceiver(self):
        while True:
            try:
                data, server_address = self.udp_socket.recvfrom(1024)
                print(f"Message received from a client at {server_address[0]}:{str(server_address[1])}... \n")
                try:
                    message = pickle.loads(data)
                    print(f"Message received from server: {message} \n")
                    if isinstance(message, dict) and message.get("Type") == "NEGOTIATE_REQ":
                       self.handle_negotiation_request(message)
                except pickle.UnpicklingError as e:
                    print(f"Faulty message received from server at {server_address[0]}:{str(server_address[1])}.  Error Code: {str(e)} \n")
                    error_message = f"Error occurred while processing your message... \n"
                    self.udp_socket.sendto(pickle.dumps(error_message), server_address)
            except Exception as e:
                print(f"Error: {e}")

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

    # def handle_negotiation(self, response_data):
    #     print("\nNegotiation request recieved:", response_data)
    #     negotiation_choice = input("Enter [1] to Accept or [2] to Reject: ")
    #     if negotiation_choice == "1":
    #         negotiation_label = "ACCEPT"
    #         new_price = input("Enter new price: ")
    #     else:
    #         negotiation_label = "REFUSE"
    #         new_price = "REJECT"
    #
    #     item_name = response_data["Item_Name"]
    #     rq = response_data.get("RQ#", random.randint(100, 900))
    #     request_data_au = {
    #         "Server Response": negotiation_label,
    #         "RQ#": rq,
    #         "Item_Name": item_name,
    #         "New Price": new_price,
    #     }
    #
    #     print("Sending negotiation response:", request_data_au)
    #     message = pickle.dumps(request_data_au)
    #     self.udp_socket.sendto(message, (self.SERVER_IP, self.SERVER_UDP_PORT))
    #
    #     try:
    #         response, _ = s.recvfrom(1024)
    #         response_data = pickle.loads(response)
    #         print("Server Response:", response_data)
    #     except Exception as e:
    #         print(f"Error receiving negotiation request: {e}")

    def menu_select(self, response_data=None):
        while True:
            print("What would you like to do?\n")
            print("[0] Exit\n")
            print("[1] Register with the server\n")
            if self.registration_rq is not None:
                print(f"[2] deregister from server\n")
            if self.role == "Seller":
                print(f"[3] List an item for auction\n")
            elif self.role == "Buyer":
                print(f"[3] Browse items\n")
                print(f"[4] Make an offer on an item\n")

            input_selection = input("Enter selection: ")

            if input_selection == "0":
                print(f"Exiting the system!\n")
                break
            elif input_selection == "1":
                registration_input_handling(self.registration_rq, self.name, self.role, self.ip_address, self.udp_port, self.tcp_port, self.udp_socket, (self.SERVER_IP, self.SERVER_UDP_PORT))
            elif input_selection == "2" and self.registration_rq is not None:
                deregistration_input_handling(self)
            elif input_selection == "3" and self.role == "Seller":
                print("In List ITEM!")
                while True:
                    RQ = random.randint(100, 900)
                    item_name = input("Enter item name (or type 'exit' to quit): ")
                    if item_name.lower() == "exit":
                        break
                    item_description = input("Enter item description: ")
                    start_price = input("Enter start price ($): ")
                    duration = input("Enter duration (minutes): ")
                    request_data = {
                        "Type": "LIST_ITEM",
                        "RQ#": RQ,
                        "Item_Name": item_name,
                        "Item_Description": item_description,
                        "Start_Price": start_price,
                        "Duration": duration,
                    }
                    client.startClient()
                    if response_data and "ITEM_LISTED" in response_data.values():
                        item_listed_response = input("Select [1] to list another item or [2] to wait for negotiations: ")
                        if item_listed_response == "1":
                            continue
                        else:
                            break
                if response_data and "LIST_DENIED" in response_data.values():
                    continue
            elif input_selection == "3" and self.role == "Buyer":
                print("Browse items here")
            elif input_selection == "4" and self.role == "Buyer":
                print("make offer here")


                    print("Sending listing request:", request_data)
                    message = pickle.dumps(request_data)
                    self.udp_socket.sendto(message, (self.SERVER_IP, self.SERVER_UDP_PORT))
                    
                    data = self.udpMessageReceiver()
                
                    # Attempt to deserialize the message sent by a client.
                    response = pickle.loads(data)
                    print("\nNegotiation request received:", response)
                    negotiation_choice = input("Enter [1] to Accept or [2] to Reject: ")
                    if negotiation_choice == "1":
                                negotiation_label = "ACCEPT"
                                new_price = input("Enter new price: ")
                    else:
                                negotiation_label = "REFUSE"
                                new_price = "REJECT"

                    #             item_name = response["Item_Name"]
                    #             rq = response.get("RQ#", random.randint(100, 900))
                    #             request_data = {
                    #             "Server Response": negotiation_label,
                    #             "RQ#": rq,
                    #             "Item_Name": item_name,
                    #             "New Price": new_price,         
                    #                     }
                    #             client.startClient()

                    #             print("Sending listing request:", request_data)
                    #             message = pickle.dumps(request_data)
                    #             self.udp_socket.sendto(message, (self.SERVER_IP, self.SERVER_UDP_PORT))
            
            elif input_selection=="3" and self.role=="Buyer":
                            print("Browse items here")
            elif input_selection=="4" and self.role=="Buyer":
                            print("make offer here")
            elif input_selection=="4" and self.role=="Seller":
                 
                data = self.udpMessageReceiver()
                
                    # Attempt to deserialize the message sent by a client.
                response = pickle.loads(data)
                print("\nNegotiation request received:", response)
                negotiation_choice = input("Enter [1] to Accept or [2] to Reject: ")
                
                if negotiation_choice == "1":
                    negotiation_label = "ACCEPT"
                    new_price = input("Enter new price: ")
                else:
                    negotiation_label = "REFUSE"
                    new_price = "REJECT"

                item_name = message["Item_Name"]
                rq = message.get("RQ#", random.randint(100, 900))
                
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