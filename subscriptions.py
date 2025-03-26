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
    rq = data["rq"]
    item_name = data["item_name"]
    client_name = data["client_name"] #does this exist in this data dictionary?

    if item_name not in subscriptons: 
        subscriptions[item_name] = []
    
    else: 
        subscriptions[item_name].append(name) # store list of name for users subscribed to item???