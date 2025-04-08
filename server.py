# Pre-Existing Modules
import socket
import sys
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor

# User-Defined Modules
from registration import registration_handling, deregistration_handling
from item_listing import ITEM_LISTED, LIST_DENIED


# Server Class
class Server:
    ### Attributes
    rq = 1  # A variable that will keep track of the different communication links between the server and clients
    registered_clients = {}  # A dictionary containing the existing clients
    listed_items = {}  # A dictionary containing the items that are up for auction
    client_bids = {}  # A dictionary containing the client bids for each item

    ### Methods
    def __init__(self):
        self.HOST = '0.0.0.0'
        self.UDP_PORT = 5000
        self.TCP_PORT = 6000
        self.UDP_SOCKET = None
        self.TCP_SOCKET = None
        self.pool = ThreadPoolExecutor(max_workers=10)

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

            # Determine the type of message that needs to be handled, and apply the appropriate method.
            if message.startswith("REGISTER"):
                registered_clients = registration_handling(message, self.registered_clients, udp_socket, client_address)
                # print dictionary of registered clients
                print(f"Registered Clients: {self.registered_clients} \n")
            elif message.startswith("DEREGISTER"):
                registered_clients = deregistration_handling(message, self.registered_clients, udp_socket,
                                                             client_address)
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

                try:
                    # Attempt to deserialize the message sent by a client.
                    message = pickle.loads(data)
                except pickle.UnpicklingError as e:
                    print(
                        f"Faulty message received from client at {client_address[0]}:{str(client_address[1])}.  Error Code: {str(e[0])}, Message: {e[1]} \n")
                    error_message = f"Error occured while processing your message... \n"
                    self.UDP_SOCKET.sendto(pickle.dumps(error_message), client_address)
                    continue

                self.udpCommunicationHandling(message, client_address, self.UDP_SOCKET)

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
            client_socket.send(pickle.dumps(response))

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