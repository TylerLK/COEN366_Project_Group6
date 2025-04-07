# Pre-Existing Modules
import socket
import sys
import pickle
import threading
import time

# User-Defined Modules
from registration import registration_handling, deregistration_handling
#from auction_update_server import list_item_response, monitor_auctions, negotiation_response

# Server Class
class Server:
    ### Attributes
    rq = 1 # A variable that will keep track of the different communication links between the server and clients
    registered_clients = {} # A dictionary containing the existing clients
    listed_items = {} # A dictionary containing the items that are up for auction
    client_bids = {} # A dictionary containing the client bids for each item
    
    ### Methods
    def __init__(self):
        self.HOST = '0.0.0.0'
        self.UDP_PORT = 5000
        self.TCP_PORT = 6000
        self.UDP_SOCKET = None
        self.TCP_SOCKET = None

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
            if request_type==("REGISTER"):
                self.registered_clients = registration_handling(request_data, self.registered_clients, udp_socket, client_address)
            elif request_type==("DEREGISTER"):
                self.registered_clients = deregistration_handling(request_data, self.registered_clients, udp_socket, client_address)
            elif request_type==("NEGOTIATE_RESPONSE"):
                self.negotiation_response(request_data, client_address)
            elif request_type==("LIST_ITEM"):
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