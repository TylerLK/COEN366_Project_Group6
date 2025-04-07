# Pre-Existing Modules
import socket
import sys
import pickle
import threading
import random
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
            print(f"Failed to create a UDP Datagram Socket.  Error: {str(e)} \n")
            sys.exit()
        # Bind the newly created UDP Datagram Sokcet to an IP Address and Port Number
        try:
            self.udp_socket.bind((self.ip_address, 0)) # Putting 0 means that an avilable port will be found
            print(f"UDP Datagram Socket binding... \n")
        except socket.error as e:
            print(f"Bind failed.  Error: {str(e)} \n")
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
            print(f"Failed to create a TCP Socket. Error: {str(e)} \n")
            sys.exit()
        # Bind the newly created TCP Socket to an IP Address and Port Number
        try:
            self.tcp_socket.bind((self.ip_address, 0)) # Putting 0 means that an avilable port will be found
            print(f"TCP Socket binding... \n")
        except socket.error as e:
            print(f"Bind failed.  Error: {str(e)} \n")
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
                    if isinstance(message, dict) and message.get("Type") == "NEGOTIATE_REQ":
                        self.handle_negotiation_request(message)

                except pickle.UnpicklingError as e:
                    print(f"Faulty message received from server at {server_address[0]}:{str(server_address[1])}.  Error Code: {str(e)} \n")
                    error_message = f"Error occured while processing your message... \n"
                    self.UDP_SOCKET.sendto(pickle.dumps(error_message), server_address)
                    continue

                # TODO: Change this behaviour to actually handle the message correctly.

            except Exception as e:
                print(f"Error: {e}") 



    def list_item():
     while True:
        RQ = random.randint(100, 900) 
        item_name = input("Enter item name (or type 'exit' to quit): ")
        if item_name.lower() == "exit":
            break

        item_description = input("Enter item description: ")

    
        start_price = input("Enter start price ($): ")
        
        
   
        duration = input("Enter duration (minutes): ")
        type="LIST_ITEM"
        

        request_data = {
        "Type": type,
        "RQ#": RQ,
        "Item_Name": item_name,
        "Item_Description": item_description,
        "Start_Price": start_price,  
        "Duration": duration,        
        }

        print("Sending listing request:", request_data)
        message = pickle.dumps(request_data)
        self.udp_socket.sendto(message, (self.SERVER_IP, self.SERVER_UDP_PORT))

   
        response, _ = s.recvfrom(1024)  
        response_data = pickle.loads(response) 
        print("Server Response:", response_data)

        if "ITEM_LISTED" in response_data.values():
         item_listed_response = input("Select [1] to list another item or [2] to wait for negotiations: ")
         if item_listed_response == "1":
                continue
         else:
                break

        elif "LIST_DENIED" in response_data.values():
            continue  

    # ---- Wait for a possible negotiation request ----
   
    def handle_negotiation(self, response_data):
        
        print("\nNegotiation request recieved:", response_data)

        negotiation_choice = input("Enter [1] to Accept or [2] to Reject: ")
        if negotiation_choice == "1":
                negotiation_label = "ACCEPT"
                new_price = input("Enter new price: ")
        else:
                negotiation_label = "REFUSE"
                new_price = "REJECT"

                item_name = response_data["Item_Name"]
                rq = response_data.get("RQ#", random.randint(100, 900))
                request_data_au = {
                "Server Response": negotiation_label,
                "RQ#": rq,
                "Item_Name": item_name,
                "New Price": new_price,         
            }

                print("Sending negotiation response:", request_data_au)
                message = pickle.dumps(request_data_au)
                self.udp_socket.sendto(message, (self.SERVER_IP, self.SERVER_UDP_PORT))
        try: 
            response, _ = s.recvfrom(1024)
            response_data = pickle.loads(response)  
            print("Server Response:", response_data)

        except Exception as e:
            print(f"Error receiving negotiation request: {e}")

    def menu_select(self):
     while True:
            print("What would you like o do?\n")
            print("[0] Exit\n")
            print("[1] Register with the server\n")
            if self.registration_rq is not None:
                print(f"[2] deregister from server\n")

            if self.role=="Seller":
                print(f"[3] List an item for auction\n")
            elif self.role=="Buyer":
                print(f"[3] Browse items\n")
                print(f"[4] Make an offer on an item\n")

            input_selection=input("Enter selection: ")

            if input_selection=="0":
                print(f"Exiting the system!\n")
                break

            elif input_selection=="1":
                registration_handling(self)
            elif input_selection=="2" and self.registration_rq is not None:
                deregistration_handling(self)
            elif input_selection=="3" and self.role=="Seller":
                client.list_item()
            elif input_selection=="3" and self.role=="Buyer":
                print("Browse items here")
            elif input_selection=="4" and self.role=="Buyer":
                print("make offer here")

    ## TCP Handling
    # TODO: Implement TCP Handling when modules are available
# END Client Class


# This class will define behaviour specific to seller clients
class Seller (Client):
    def __init__(self, name):
        super().__init__(name, "Seller")
# END Seller Class
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
                client=Seller(name)
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
                client=Buyer(name)
                break
        else:
            print(f"Invalid role!  You should enter 's' to be a Seller or 'b' to be a Buyer... \n")
    
    # Create the client object
    if(role == "s"):
        client = Seller(name)
      
    elif(role == "b"):
        client = Buyer(name)

    client.startClient()
    client.menu_select()


            

    











    # Create the UDP and TCP sockets for the client object
    # print("\n")
    # print("======================================================================================================")
    # print(f"Network Configuration \n")
    # client.startClient()
    # print("======================================================================================================")
    
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