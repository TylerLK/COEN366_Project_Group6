import pickle
import socket

# Server-side Functions
def BID_ACCEPTED(sock, address, rq):
    response = {
        "status": "BID_ACCEPTED",
        "rq": rq
    }
    serialized_response = pickle.dumps(response)
    sock.sendto(serialized_response, address)
    print(f"BID_ACCEPTED sent to {address} for RQ#: {rq}")

def BID_DENIED(sock, address, rq, reason):
    response = {
        "status": "BID_REJECTED",
        "rq": rq,
        "reason": reason
    }
    serialized_response = pickle.dumps(response)
    sock.sendto(serialized_response, address)
    print(f"BID_REJECTED sent to {address} for RQ#: {rq}. Reason: {reason}")

# Client-side Functions
def BID(rq, item, bid_amount):
    # Construct the BID message as a dictionary
    message = {
        "type": "BID",
        "rq": rq,
        "item_name": item,
        "bid_amount": bid_amount
    }

    # Serialize the message using pickle
    serialized_message = pickle.dumps(message)
    return serialized_message

'''
handle_bid function to implement for the server side in server.py'
'''
def handle_bid(sock, addr, message):
    rq = message.get("rq")
    item_name = message.get("item_name")
    bid_amount = message.get("bid_amount")

    # Check if the auction exists and is active
    if item_name not in listed_items or item_name("rq") != rq:
        BID_DENIED(sock, addr, rq, "No active auction for the requested item.")
        return

    # Check if the bid amount is valid
    current_price = listed_items[item_name]["current_price"]
    if bid_amount <= current_price:
        BID_DENIED(sock, addr, rq, "Bid amount is too low.")
        return

    # Accept the bid
    listed_items[item_name]["current_price"] = bid_amount
    BID_ACCEPTED(sock, addr, rq)

def send_bid(sock, server_address, rq, item, bid_amount):
    """
    Sends a bid request to the server and handles the response.

    Args:
        sock (socket.socket): The client's socket.
        server_address (tuple): The server's address (IP and port).
        rq (str): Request number.
        item (str): Name of the item being bid on.
        bid_amount (float): The amount being bid.
    """
    try:
        # Construct the bid request
        serialized_message = BID(rq, item, bid_amount)

        # Send the bid request to the server
        sock.sendto(serialized_message, server_address)
        print(f"Sent BID request for item '{item}' with amount {bid_amount} to {server_address}")

        # Wait for the server's response
        data, _ = sock.recvfrom(1024)  # Buffer size: 1024 bytes

        # Deserialize the server's response
        response = pickle.loads(data)

        # Handle the server's response
        if response.get("status") == "BID_ACCEPTED":
            print(f"BID ACCEPTED for RQ#: {response.get('rq')}")
        elif response.get("status") == "BID_REJECTED":
            print(f"BID REJECTED for RQ#: {response.get('rq')}. Reason: {response.get('reason')}")
        else:
            print("Invalid response from server")

    except Exception as e:
        print(f"Error during bid: {e}")