import socket
import sys

# server config
UDP_IP = "0.0.0.0"
UDP_PORT = 5000

# user dictionary
registeredUsers = {}

def register (details):
    parts = details.split(" ")

    _, rq, name, role, ipAddr, udpSocket, tcpSocket = parts

    if len(parts) != 7:
        return f"INVALID COMMAND {rq}"
    elif name in registeredUsers:
        return f"REGISTERED-DENIED {rq} name already in use"
    else:
        registeredUsers[name] = {"rq": rq, "name": name, "role": role, "ipAddr": ipAddr, "udpSocket": udpSocket, "tcpSocket": tcpSocket}
        return f"REGISTERED {rq}"

def deregister(details):
    parts = details.split(" ")

    _, rq, name = parts

    if len(parts) != 3:
        return f"INVALID COMMAND {rq}"
    elif name in registeredUsers:
        del registeredUsers[name]


def startServer():
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

                message = data.decode()

                # Determine type of message
                if message.startswith("REGISTER"):
                    reply = register (message)
                elif message.startswith("DEREGISTER"):
                    reply = deregister(message)
                else:
                    reply = "INVALID REQUEST"


                sock.sendto(reply.encode(), addr)

            except socket.error as msg:
                print("Socket error: " + str(msg))

    except KeyboardInterrupt:
        print("\nServer shutting down...")

    finally:
        print("Closing socket...")
        sock.close()

if __name__ == "__main__":
    startServer()