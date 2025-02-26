import socket
import sys

# server config
UDP_IP = "0.0.0.0"
UDP_PORT = 5000

# create UDP server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Socket Created")
except socket.error as msg:
    print("Failed to create socket: " + str(msg))
    sys.exit()

# bind server to port 5000
try:
    sock.bind((UDP_IP, UDP_PORT))
    print("Socket bind to port 5000 completed")
except socket.error as msg:
    print("Failed to bind to port 5000: " + str(msg))
    sys.exit()

# server loop
try:
    while True:
        try:
            data, addr = sock.recvfrom(1024)  # Buffer size: 1024 bytes
            if not data:
                continue
            print("Received data from client" + str(addr))
            sock.sendto(data, addr)
            reply = "Message received: " + data.decode()

            sock.sendto(reply.encode(), addr)

        except socket.error as msg:
            print("Socket error: " + str(msg))

except KeyboardInterrupt:
    print("\nServer shutting down...")

finally:
    print("Closing socket...")
    sock.close()