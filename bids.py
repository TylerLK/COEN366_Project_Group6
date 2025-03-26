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
handle_bid function to implement for the server side in server.py
def handle_bid(sock, addr, message):
    rq = message.get("rq")
    item_name = message.get("item_name")
    bid_amount = message.get("bid_amount")

    # Check if the auction exists and is active
    if item_name not in list_items or item_name("rq") != rq:
        BID_DENIED(sock, addr, rq, "No active auction for the requested item.")
        return

    # Check if the bid amount is valid
    current_price = list_items[item_name]["current_price"]
    if bid_amount <= current_price:
        BID_DENIED(sock, addr, rq, "Bid amount is too low.")
        return

    # Accept the bid
    list_items[item_name]["current_price"] = bid_amount
    BID_ACCEPTED(sock, addr, rq)
    '''