# Pre-Existing Modules
import os
import socket
import sys
import pickle
import threading
import time
import json
from concurrent.futures import ThreadPoolExecutor

#from auction_update_server import listed_items
from bids import bid_handling
# User-Defined Modules
from registration import registration_handling, deregistration_handling
from item_listing import ITEM_LISTED, LIST_DENIED, list_item_handling
from subscriptions import subscription_handling, desubscription_handling


# Server Class
class Server:
    ### Attributes
    rq = 1  # A variable that will keep track of the different communication links between the server and clients

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
        self.load_data_from_files()
        self.pool = ThreadPoolExecutor(max_workers=10)


    def createLogs(self):
        """This function will run in a loop, writing logs every 10 seconds."""
        while True:
            try:
                with open("registered_clients.json", "w") as f:
                    json.dump(self.registered_clients, f, indent=4)
            except IOError as e:
                print(f"Error writing to file: {e}")

            try:
                with open("listed_items.json", "w") as f:
                    json.dump(self.listed_items, f, indent=4)
            except IOError as e:
                print(f"Error writing to file: {e}")

            try:
                with open("item_subscriptions.json", "w") as f:
                    json.dump(self.item_subscriptions, f, indent=4)
            except IOError as e:
                print(f"Error writing to file: {e}")

            try:
                with open("active_auctions.json", "w") as f:
                    json.dump(self.active_auctions, f, indent=4)
            except IOError as e:
                print(f"Error writing to file: {e}")

            try:
                with open("client_bids.json", "w") as f:
                    json.dump(self.client_bids, f, indent=4)
            except IOError as e:
                print(f"Error writing to file: {e}")

            try:
                with open("completed_auctions.json", "w") as f:
                    json.dump(self.completed_auctions, f, indent=4)
            except IOError as e:
                print(f"Error writing to file: {e}")

            # Wait for 10 seconds before writing again
            time.sleep(10)

    def start_periodic_task(self):
        # Start the periodic task in a separate thread
        self.pool.submit(self.createLogs)

    def load_data_from_files(self):
        self.registered_clients = self.load_json_file("registered_clients.json")
        self.listed_items = self.load_json_file("listed_items.json")
        self.client_bids = self.load_json_file("client_bids.json")
        self.item_subscriptions = self.load_json_file("item_subscriptions.json")
        self.active_auctions = self.load_json_file("active_auctions.json")
        self.completed_auctions = self.load_json_file("completed_auctions.json")
        print("Data successfully loaded from files")

    def load_json_file(self, filename):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        return {}  # Return empty dict if file is empty
                    return json.loads(content)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                return {}
        return {}




    def monitor_auctions(self):
     while True:
        time.sleep(5)
        current_time = time.time()

        for item_name, item in list(self.listed_items.items()):
            elapsed_time = current_time - item["Start_Time"]
            half_duration = (item["Duration"] * 60) / 2

            if elapsed_time > half_duration and item_name not in self.client_bids and not item["Prev_Negotiated"]:
                item["Prev_Negotiated"] = True
                print(f"Sending negotiation request for {item['Item_Name']}")
                response = {
                    "Type": "NEGOTIATE_REQ",
                    "Item_Name": item["Item_Name"],
                    "Current_Price": item["Start_Price"],
                    "Time_Left": (item["Duration"] * 60) - elapsed_time
                }
                self.UDP_SOCKET.sendto(pickle.dumps(response), item["Seller"])

    def monitor_bids(self):
        previous_highest_bids = {}
        while True:
            for item, bids in self.client_bids.items():
                if not bids:
                    continue

                highest_bidder = None
                highest_bid = -1

                for bidder, bid in bids.items():
                    if bid > highest_bid:
                        highest_bid = bid
                        highest_bidder = bidder

                if item not in previous_highest_bids or highest_bid > previous_highest_bids[item]['bid']:
                    if item in previous_highest_bids:
                        old_highest_bidder = previous_highest_bids[item]['bidder']
                        old_highest_bid = previous_highest_bids[item]['bid']
                        message = f"New highest bid for '{item}': {highest_bidder} bid ${highest_bid} (previous highest was ${old_highest_bid} by {old_highest_bidder})."
                    else:
                        message = f"New highest bid for '{item}': {highest_bidder} bid ${highest_bid}."
                    
                    self.UDP_SOCKET.sendto(pickle.dumps(message), self.listed_items[item]["Seller"])

                previous_highest_bids[item] = {'bidder': highest_bidder, 'bid': highest_bid}
            
            time.sleep(5)
    def negotiation_response(self, request_data, addr):
   
     try:
        current_time = time.time()
        item_name = request_data.get("Item_Name")
        new_price = int(request_data.get("New Price"))
        request_id = request_data.get("RQ#")

        for item in self.listed_items:
                item=self.listed_items[item_name]
                item["Start_Price"] = new_price
                elapsed_time = current_time - item["Start_Time"]
                
                break
        else:
            print(f"Item not found: {item_name}")
            return

        print(f"Updated {item_name} price to {new_price}.")

        response = {
            "Type": "PRICE_ADJUSTMENT",
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
        
        if item_name in self.listed_items:
            response = {"Server Response": "LIST_DENIED", "RQ#": request_id, "Reason": "Item Name already exists"}
            self.UDP_SOCKET.sendto(pickle.dumps(response), addr)
            return
        if item_name==" ":
            response = {"Server Response": "LIST_DENIED", "RQ#": request_id, "Reason": "Item Name must be filled"}
            self.UDP_SOCKET.sendto(pickle.dumps(response), addr)
            return
        
        if not item_description.strip():
            response = {"Server Response": "LIST_DENIED", "RQ#": request_id, "Reason": "Item description must be filled"}
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
            "Seller": addr,
            "Prev_Negotiated": False
        }
    
        self.active_auctions[item_name] = {
        "item_name": item_name,
        "item_description": item_description,
        "duration": duration,
        "current_price": start_price,  
        "seller": addr,
        }
       

        response = {"Server Response": "ITEM_LISTED", "RQ#": request_id}
        self.UDP_SOCKET.sendto(pickle.dumps(response), addr)

     except Exception as e:
        print(f"Error processing request: {e}")
        error_response = {"Server Response": "LIST_DENIED", "RQ#": "N/A", "Reason": str(e)}
        self.UDP_SOCKET.sendto(pickle.dumps(error_response), addr)



    def startServer(self):
        # Create a UDP Datagram Socket
        self.pool.submit(self.monitor_bids)
        self.pool.submit(self.monitor_auctions) ###copilot flagged saying () is unneeded
        # auction_monitor_thread = threading.Thread(target=self.monitor_auctions, daemon=True)
        # auction_monitor_thread.start()
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
        self.pool.submit(self.udpMessageReceiver)
        # Start a thread to handle incoming TCP messages
        self.pool.submit(self.tcpCommunicationHandling)

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
    def udpCommunicationHandling(self, message, client_address, udp_socket):
        try:
            print(f"A UDP Request has been received from {client_address[0]}:{str(client_address[1])}... \n")

            if isinstance(message, dict):
                request_type = message.get("Type")

                if request_type == ("NEGOTIATE_RESPONSE"):
                    self.negotiation_response(message, client_address)

                elif request_type == ("LIST_ITEM"):
                    self.list_item_response(message, client_address)

                    # elif message.startswith("LIST_ITEM"):
                    # self.listed_items = list_item_handling(message, self.listed_items, udp_socket, client_address)
                    # # print dictionary of listed items
                    # print(f"Listed Items: {self.listed_items} \n")

            elif isinstance(message, str):
                # Determine the type of message that needs to be handled, and apply the appropriate method.
                if message.startswith("REGISTER"):
                    self.registered_clients, self.rq = registration_handling(self.rq, message, self.registered_clients, udp_socket, client_address)

                elif message.startswith("DEREGISTER"):
                    self.registered_clients, self.rq = deregistration_handling(self.rq, message, self.registered_clients, udp_socket, client_address)

                elif message.startswith("DE_SUBSCRIBE"):
                    self.item_subscriptions, self.rq = desubscription_handling(self.rq, message, self.item_subscriptions, udp_socket, client_address)

                elif "SUBSCRIBE" in message:
                    
                    self.item_subscriptions, self.rq = subscription_handling(self.rq, message, self.listed_items, self.item_subscriptions, udp_socket, client_address)

                
                elif message.startswith("BID"):
                    
                    self.client_bids, self.active_auctions= bid_handling(message, self.client_bids, self.active_auctions, self.item_subscriptions, self.registered_clients, self.listed_items, udp_socket, client_address)

                elif message.startswith("LIST_ITEM"):
                    self.listed_items = list_item_handling(self.rq, message, self.listed_items, udp_socket, client_address)

                # elif message.startswith("BID_UPDATE"):
                #     self.active_auctions = AUCTION_ANNOUNCE(message, self.active_auctions, self.client_bids, self.registered_clients , udp_socket, client_address)

                elif message.startswith("ALL_LIST"):
                    message = f"Listed Items: {self.listed_items}"
                    print(message)
                    self.UDP_SOCKET.sendto(pickle.dumps(message), client_address)

                

            else:
                reply = f"Invalid UDP communication request: {message} \n"
                print(reply)
                self.UDP_SOCKET.sendto(pickle.dumps(reply), client_address)
        except Exception as e:
            print(f"UDP Communication Handling failed.  Error: {str(e)} \n")


    # This method will handle incoming UDP messages from clients.
    def udpMessageReceiver(self):
        while True:
            try:
                data, client_address = self.UDP_SOCKET.recvfrom(1024)
                print(f"Message received from a client at {client_address[0]}:{str(client_address[1])}... \n")
                print(f"Message: ", pickle.loads(data))

                try:
                    # Attempt to deserialize the message sent by a client.
                    message = pickle.loads(data)
                except pickle.UnpicklingError as e:
                    print(f"Faulty message received from client at {client_address[0]}:{str(client_address[1])}.  Error: {str(e)} \n")
                    error_message = f"Error occurred while processing your message... \n"
                    self.UDP_SOCKET.sendto(pickle.dumps(error_message), client_address)
                    continue

                # Submit the UDP message handling to the thread pool
                self.pool.submit(self.udpCommunicationHandling, message, client_address, self.UDP_SOCKET)

                # Echo the received message back to the client
                response = f"Echo: {message} \n"
                self.UDP_SOCKET.sendto(pickle.dumps(response), client_address)

                print(f"Registered Clients: {self.registered_clients} \n")

                # TODO: Change this behaviour to actually handle the message correctly.

            except Exception as e:
                print(f"Error: {e}")

                ## TCP Handling

    def handle_tcp_client(self, client_socket, client_address):
        try:
            data = client_socket.recv(1024)
            if not data:
                print(f"TCP Client {client_address} disconnected.")
                client_socket.close()
                return
            message = pickle.loads(data)
            print(f"Received TCP message from {client_address}: {message}")

            # TODO: Add logic here to handle messages

            # Echo for now:
            response = f"Server received your message: {message}"
            client_socket.send(pickle.dumps(response)) #test

        except Exception as e:
            print(f"Error handling TCP client {client_address}: {e}")
        finally:
            client_socket.close()

    def tcpCommunicationHandling(self):
        self.TCP_SOCKET.listen()
        print("TCP Server listening for connections...\n")
        while True:
            client_socket, client_address = self.TCP_SOCKET.accept()
            print(f"TCP Connection established with {client_address}")
            self.pool.submit(self.handle_tcp_client, client_socket, client_address)

# End of Server Class

if __name__ == "__main__":
    server = Server()
    server.startServer()
    server.start_periodic_task()

    try:
        # Keep server running or add a condition for shutdown
        while True:
            pass
    except KeyboardInterrupt:
        server.shutdownServer()
