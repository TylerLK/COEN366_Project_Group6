# Pre-Existing Modules
import socket
import sys
import pickle
import threading
import time

# User-Defined Modules
from registration import registration_handling, deregistration_handling

from item_listing import ITEM_LISTED, LIST_DENIED
from subscriptions import subscription_handling, desubscription_handling


# Server Class
class Server:
    ### Attributes
    # A variable that will keep track of the different communication links between the server and clients
    rq = 1 
    
    # A dictionary containing the existing clients
    registered_clients = {
        # "client_name": {
        #     "rq": rq,
        #     "role": role,
        #     "ip_address": ip_address,
        #     "udp_port": udp_port,
        #     "tcp_port": tcp_port
        # },
        # ...
    } 
    
    # A dictionary containing the items that are up for auction
    listed_items = {
        # "item_name": {
        #     "item_description": item_description,
        #     "start_price": start_price,
        #     "duration": auction_duration,
        #     "seller_name": seller
        # },
        # ...
    }

    # A dictionary containing the clients that are subscribed to a given item
    item_subscriptions = {
        # "item_name": {
        #     "rq": rq,
        #     "subscribed_clients": [
        #          "client_name_1",
        #          "client_name_2",
        #          ...
        #     ]
        # },
        # ...
    }

    # A dictionary conatining the current auctions that are being conducted by the server
    active_auctions = {
        # "item_name": {
        #     "rq": rq,
        #     "item_description": description,
        #     "current_price": price,
        #     "time_left": time,
        # },
        # ...
    }

    # A dictionary containing the client bids for each item
    client_bids = {
        # "item_name": {
        #     "client_name_1" : bid_amount_1,
        #     "client_name_2" : bid_amount_2,
        #     ...
        #  },
        #  ...
    }

    # A dictionary containing the auctions that have been completed by the server
    completed_auctions = {
        # "item_name": {
        #     "rq": rq,
        #     "final_price": price,
        #     "buyer_name": buyer,
        #     "seller_name": seller,
        # },
        # ...
    }
    
    ### Methods
    def __init__(self):
        self.HOST = '0.0.0.0'
        self.UDP_PORT = 5000
        self.TCP_PORT = 6000
        self.UDP_SOCKET = None
        self.TCP_SOCKET = None

    def monitor_auctions(self, addr):

     while True:
        time.sleep(5)
        current_time = time.time()

        for item in self.listed_items:
            elapsed_time = current_time - item["Start_Time"]
            half_duration = (item["Duration"] * 60) / 2

            if elapsed_time > half_duration and item["Item_Name"] not in self.client_bids and not item["Prev_Negotiated"]:
                item["Prev_Negotiated"] = True
                print(f"Sending negotiation request for {item['Item_Name']}")
                response = {
                    "Server Response": "NEGOTIATE_REQ",
                    "Item_Name": item["Item_Name"],
                    "Current Price": item["Start_Price"],
                    "Time_Left": (item["Duration"] * 60) - elapsed_time
                }
                self.UDP_SOCKET.sendto(pickle.dumps(response), item["Client_Addr"])

        threading.Thread(target=self.monitor_auctions, daemon=True).start()

    def negotiation_response(self, request_data, addr):
   
     try:
        current_time = time.time()
        item_name = request_data.get("Item_Name")
        new_price = int(request_data.get("New Price"))
        request_id = request_data.get("RQ#")

        for item in self.listed_items:
            if item["Item_Name"] == item_name:
                item["Start_Price"] = new_price
                elapsed_time = current_time - item["Start_Time"]
                break
        else:
            print(f"Item not found: {item_name}")
            return

        print(f"Updated {item_name} price to {new_price}.")

        response = {
            "Server Response": "PRICE_ADJUSTMENT",
            "RQ#": request_id,
            "Item_Name": item_name,
            "New_Price": new_price,
            "Time Left": elapsed_time
        }
        self.UDP_SOCKET.sendto(pickle.dumps(response), addr)

     except Exception as e:
        print(f"Error processing negotiation: {e}")

    def list_item_response(self, request_data, addr):
   
     try:
        request_id = request_data.get("RQ#")
        item_name = request_data.get("Item_Name")
        item_description = request_data.get("Item_Description")
        start_price = request_data.get("Start_Price")
        duration = request_data.get("Duration")

        

        if not str(start_price).isdigit():
            response = {"Server Response": "LIST_DENIED", "RQ#": request_id, "Reason": "Invalid start price."}
            self.UDP_SOCKET.sendto(pickle.dumps(response), addr)
            return

        if not str(duration).isdigit():
            response = {"Server Response": "LIST_DENIED", "RQ#": request_id, "Reason": "Invalid duration."}
            self.UDP_SOCKET.sendto(pickle.dumps(response), addr)
            return

        if len(self.listed_items) >= 100:
            response = {"Server Response": "LIST_DENIED", "RQ#": request_id, "Reason": "Auction capacity reached"}
            self.UDP_SOCKET.sendto(pickle.dumps(response), addr)
            return

        start_price = int(start_price)
        duration = int(duration)
        start_time = time.time()
        self.listed_items[item_name]={
            "Item_Name": item_name,
            "Item_Description": item_description,
            "Start_Price": start_price,
            "Duration": duration,
            "Start_Time": start_time,
            "Client_Addr": addr,
            "Prev_Negotiated": False
        }
       

        response = {"Server Response": "ITEM_LISTED", "RQ#": request_id}
        self.UDP_SOCKET.sendto(pickle.dumps(response), addr)

     except Exception as e:
        print(f"Error processing request: {e}")
        error_response = {"Server Response": "LIST_DENIED", "RQ#": "N/A", "Reason": str(e)}
        self.UDP_SOCKET.sendto(pickle.dumps(error_response), addr)

    def startServer(self):
        # Create a UDP Datagram Socket
        try:
            self.UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"UDP Datagram Socket created... \n")
        except socket.error as e:
            print(f"Failed to create a UDP Datagram Socket.  Error: {str(e)} \n")
            sys.exit()
        # Bind the newly created UDP Datagram Sokcet to an IP Address and Port Number
        try:
            self.UDP_SOCKET.bind((self.HOST, self.UDP_PORT))
            print(f"UDP Datagram Socket binding to {self.HOST}:{self.UDP_PORT}... \n")
        except socket.error as e:
            print(f"Bind failed.  Error: {str(e)} \n")
            sys.exit()
        print(f"UDP Datagram Socket binding complete. \n")
        # Start a thread to handle incoming UDP messages
        udp_thread = threading.Thread(target=self.udpMessageReceiver, args=())
        udp_thread.start()

        # Create a TCP Socket
        try:
            self.TCP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print(f"Failed to create a TCP Socket. Error: {str(e)} \n")
            sys.exit()
        # Bind the newly created TCP Socket to an IP Address and Port Number
        try:
            self.TCP_SOCKET.bind((self.HOST, self.TCP_PORT))
            print(f"TCP Socket binding to {self.HOST}:{self.TCP_PORT}... \n")
        except socket.error as e:
            print(f"Bind failed.  Error: {str(e)} \n")
            sys.exit()
        print(f"TCP Socket binding complete. \n")
    
    ## UDP Handling
    def udpCommunicationHandling(self, request_data, client_address, udp_socket):
     try:
         print(f"A UDP Request has been received from {client_address[0]}:{str(client_address[1])}... \n")
         try:
          
            #request_data = pickle.loads(message)
            request_type = request_data.get("Type")
            # Determine the type of message that needs to be handled, and apply the appropriate method.


            if request_type == ("REGISTER"):
                self.registered_clients = registration_handling(request_data, self.registered_clients, udp_socket, client_address)
            elif request_type == ("DEREGISTER"):
                self.registered_clients = deregistration_handling(request_data, self.registered_clients, udp_socket, client_address)
            elif request_type == ("SUBSCRIBE"):
                self.item_subscriptions = subscription_handling(request_data, self.item_subscriptions, udp_socket, client_address)
            elif request_type == ("DESUBSCRIBE"):
                self.item_subscriptions = desubscription_handling(request_data, self.item_subscriptions, udp_socket, client_address)  
            elif request_type == ("NEGOTIATE_RESPONSE"):
                self.negotiation_response(request_data, client_address)
            elif request_type == ("LIST_ITEM"):
                self.list_item_response(request_data, client_address)

            else:
                    reply = f"Invalid UDP communication request type: {request_type} \n"
                    print(reply)
                    self.UDP_SOCKET.sendto(pickle.dumps(reply), client_address)
         except pickle.UnpicklingError as e:
                print(f"Error decoding UDP message: {e}")
                reply = "Error decoding your message."
                self.UDP_SOCKET.sendto(pickle.dumps(reply), client_address)
         except Exception as e:
                print(f"Error handling UDP request: {e}")
                reply = "Error processing your request."
                self.UDP_SOCKET.sendto(pickle.dumps(reply), client_address)

     except Exception as e:
            print(f"UDP Communication Handling failed.  Error: {str(e)} \n")

    # This method will handle incoming UDP messages from clients.
    def udpMessageReceiver(self):
        while True:
            try:
                data, client_address = self.UDP_SOCKET.recvfrom(1024)
                print(f"Message received from a client at {client_address[0]}:{str(client_address[1])}... \n")

                try:
                    # Attempt to deserialize the message sent by a client.
                    request_data = pickle.loads(data)
                except pickle.UnpicklingError as e:
                    print(f"Faulty message received from client at {client_address[0]}:{str(client_address[1])}.  Error Code: {str(e[0])}, Message: {e[1]} \n")
                    error_message = f"Error occured while processing your message... \n"
                    self.UDP_SOCKET.sendto(pickle.dumps(error_message), client_address)
                    continue
                self.udpCommunicationHandling(request_data, client_address, self.UDP_SOCKET)
                # Echo the received message back to the client
                # response = f"Echo: {message} \n"
                # self.UDP_SOCKET.sendto(pickle.dumps(response), client_address)

                # TODO: Change this behaviour to actually handle the message correctly.

            except Exception as e:
                print(f"Error: {e}")     

    ## TCP Handling
    def tcpCommunicationHandling(self):
        print(f"The server is handling TCP communication... \n") 
# End of Server Class

if __name__ == "__main__":
    server = Server()
    server.startServer()