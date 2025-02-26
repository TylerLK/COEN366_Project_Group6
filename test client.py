import socket
import sys

# Server Address
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

# Create UDP Socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send a message
message = "Hello, Auction Server!"
client_socket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

# Receive a response
data, server_address = client_socket.recvfrom(1024)
print(f"Server response: {data.decode()}")

client_socket.close()
