import pickle
import socket

# Server-side Functions
def SUBSCRIBED(sock, address, rq):
    response = {
        "status": "SUBSCRIBED",
        "rq": rq
    }
    serialized_response = pickle.dumps(response)
    sock.sendto(serialized_response, address)
    print(f"SUBSCRIBED sent to {address} for RQ#: {rq}")

def SUBSCRIBE_DENIED(sock ,address, rq, reason):
    response = {
        "status": "SUBSCRIBE_DENIED",
        "rq": rq,
        "reason": reason
    }
    serialized_response = pickle.dumps(response)
    sock.sendto(serialized_response, address)
    print(f"SUBSCRIBE_DENIED sent to {address} for RQ#: {rq}. Reason: {reason}")

# Client-side Functions
def SUBSCRIBE(rq, item):
    message = {
        "type": "SUBSCRIBE",
        "rq": rq,
        "item_name": item,
        
    }
    # Serialize the message using pickle
    serialized_message = pickle.dumps(message)
    return serialized_message

def DE_SUBSCRIBE():
    message = {
        "type": "DE_SUBSCRIBE",
    }
    serialized_message = pickle.dumps(message)
    return serialized_message
# handle_subscribe function to implement for the server side in server.py

subscriptions = {} # from item name contain list of users subscribed 
def handle_subscribe(sock, address, data):
    rq = data.get("rq")
    item_name = data.get("item_name")
    client_name = data.get("client_name") 

    # Validate the input data
    if not rq or not item_name or not client_name:
        SUBSCRIBE_DENIED(sock, address, rq, "Missing required fields (rq, item_name, or client_name)")
        return

    # Check if the item already exists in the subscriptions dictionary
    if item_name not in subscriptions:
        subscriptions[item_name] = []  # Initialize an empty list for this item

    # Check if the client is already subscribed
    if client_name not in subscriptions[item_name]:
        subscriptions[item_name].append(client_name)  # Add the client's name to the list
        SUBSCRIBED(sock, address, rq)  # Send a success response
    else:
        # If the client is already subscribed, deny the subscription
        SUBSCRIBE_DENIED(sock, address, rq, "Client is already subscribed to this item")