import random
import socket
import sys

from server import deregister

# Server Address
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

# Client ports
UDP_PORT = None
TCP_PORT = None


def connectToServer():
    # Create UDP Socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send a message
    message = "Hello, Auction Server!"
    client_socket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

    # Receive a response
    data, server_address = client_socket.recvfrom(1024)
    print(f"Server response: {data.decode()}")

    client_socket.close()

def sendUdpRequest(SERVER_IP, SERVER_PORT, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

    # Verify if connection is set
    if UDP_PORT is not None:
        print("UDP_PORT is not connected")
        return

    # Wait for response
    try:
        client_socket.settimeout(5)  # Avoid infinite waiting
        data, _ = client_socket.recvfrom(1024)
        print(f"Server response: {data.decode()}")
    except socket.timeout:
        print("No response from server.")

def register(name, role):
    rqNumber = random.randint(1, 9999999)
    ipAddr = '127.0.0.1'

    # Create UDP socket and bind it to an available port
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((ipAddr, 0))
    UDP_PORT = udp_socket.getsockname()[1]

    # Create TCP socket and bind it to an available port
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((ipAddr, 0))
    TCP_PORT = tcp_socket.getsockname()[1]

    message = f"REGISTER {rqNumber} {name} {role} {ipAddr} {UDP_PORT} {TCP_PORT}"
    sendUdpRequest(SERVER_IP, SERVER_PORT, message)

def deRegister(name):
    rqNumber = random.randint(1, 9999999)
    message = f"DEREGISTER {rqNumber} {name}"
    sendUdpRequest(SERVER_IP, SERVER_PORT, message)

if __name__ == "__main__":
    name = input("Please enter your name: ")

    while True:
        role = input("Please enter your role (buyer or seller): ").lower()
        if role in ["buyer", "seller"]:
            break
        print("Invalid role! Please enter 'buyer' or 'seller'.")
    register(name, role)

    while True:
        print("Chose a command:")
        print("1. Make a bid")
        print("2. DEREGISTER")
        print("3. Exit")
        command = input("Please enter your the corresponding number for the next command: ").lower()

        if command == "1":
            print("gg")
        elif command == "2":
            deRegister(name)
        elif command == "3":
            break
        else:
            print("Invalid command! Please enter '1' or '2' or '3'")