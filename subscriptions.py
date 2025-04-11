import pickle

## Server-Side Functions

# This method will allow the server to internally process an incoming subscription request from a client
def subscription_handling(subscription_request, subscriptions, server_socket, client_address):
    # Deconstruct the incoming subscription request message
    deconstructed_subscription_request = subscription_request.split("|")

    # Check if the subscription request contains the correct information (i.e., 4 segments of information)
    if len(deconstructed_subscription_request) != 4:
        # Call the SUBSCRIPTION_DENIED method to tell the client their subscription request was invalid.
        subscription_denial_message = f"SUBSCRIPTION_DENIED|{deconstructed_subscription_request[1]}|Invalid number of subscription parameters. {len(deconstructed_subscription_request)} sent, 4 expected... \n"       
        SUBSCRIPTION_DENIED(server_socket, client_address, subscription_denial_message)
        print(subscription_denial_message)
        return subscriptions
    
    else:
        # Create a variable for each piece of the subscription request
        message_type, rq, item_name, client_name = deconstructed_subscription_request
    
    # Check if the item is actually in the dictionary of subscriptions
    if item_name not in subscriptions:
        # Create a new key-value pair for this item in the dictionary of subscriptions
        subscriptions[item_name] = {
            "rq": rq,
            "subscribed_clients": []
        }

    # Check if the user already exists in the list of subscribed clients
    if client_name in subscriptions[item_name]['subscribed_clients']:
        # Call the SUBSCRIPTION_DENIED method to tell the client their subscription request was invalid.
        subscription_denial_message = f"SUBSCRIPTION_DENIED|{rq}|You have already subscribed to this item. \n"
        SUBSCRIPTION_DENIED(server_socket, client_address, subscription_denial_message)
        print(subscription_denial_message)
        return subscriptions
    
    else:
        # Add the user to the dictionary of subscriptions
        subscriptions[item_name]["subscribed_clients"].append(client_name)

        # Call the SUBSCRIBED method to acknowledge the client's subscription request
        subscription_confirmation_message = f"SUBSCRIBED|{rq} \n"
        SUBSCRIBED(server_socket, client_address, subscription_confirmation_message)
        print(subscription_confirmation_message)
        return subscriptions
# END subscription_handling

# This method will allow the server to internally process an incoming desubscription request from a client
def desubscription_handling(desubscription_request, subscriptions, server_socket, client_address):
    # Deconstruct the incoming desubscription request message
    deconstructed_desubscription_request = desubscription_request.split(" ")

    # Check if the desubscription request contains the correct information (i.e., 4 segments of information)
    if len(deconstructed_desubscription_request) != 4:
        desubscription_denial_message = f"DE_SUBSCRIBE_DENIED|{deconstructed_desubscription_request[1]}|Invalid number of desubscription parameters. {len(deconstructed_desubscription_request)} sent, 4 expected... \n"
        server_socket.sendto(pickle.dumps(desubscription_denial_message), client_address)
        print(desubscription_denial_message)
        return subscriptions
    
    else:
        # Create a variable for each piece of the subscription request
        message_type, rq, item_name, client_name = deconstructed_desubscription_request
    
    # Check if the item is actually in the dictionary of subscriptions
    if item_name not in subscriptions:
        desubscription_denial_message = f"DE_SUBSCRIBE_DENIED|{rq}|Item does not exist. \n"
        server_socket.sendto(pickle.dumps(desubscription_denial_message), client_address)
        print(desubscription_denial_message)
        return subscriptions
    
    # Delete the user from the dictionary of subscriptions, provided that the user exists
    if client_name in subscriptions[item_name]["subscribed_clients"]:
        desubscription_confirmation_message = f"DE_SUBSCRIBED|{rq} \n"
        server_socket.sendto(pickle.dumps(desubscription_confirmation_message), client_address)
        subscriptions[item_name]["subscribed_clients"].remove(client_name)
        print(desubscription_confirmation_message)
        return subscriptions
    
    else:
        desubscription_denial_message = f"DE_SUBSCRIBE_DENIED|{rq}|Client name does not exist. \n"
        server_socket.sendto(pickle.dumps(desubscription_denial_message), client_address)       
        print(desubscription_denial_message)
        return subscriptions
# END desubscription_handling

# This method will be used as a positive acknowledgement for a potential client's subscription request.
def SUBSCRIBED(server_sock, client_addr, message):
    print(f"Sending subscription confirmation to client at {client_addr[0]}:{str(client_addr[1])}... \n")
    server_sock.sendto(pickle.dumps(message), client_addr)
# END SUBSCRIBED

def SUBSCRIPTION_DENIED(server_sock, client_addr, message):
    print(f"Sending subscription denial to client at {client_addr[0]}:{str(client_addr[1])}... \n")
    server_sock.sendto(pickle.dumps(message), client_addr)
# END SUBSCRIPTION_DENIED

## Client-Side Functions

# This method will be used to handle user inputs for client-side subscription.
def subscription_input_handling(rq, item_name, name, client_socket, server_address):
    # Create the message that will be sent to the server for subscription
    subscription_request = f"SUBSCRIBE|{rq}|{item_name}|{name}"

    # Call the SUBSCRIBE method to send the subscription request to the server
    SUBSCRIBE(client_socket, server_address, subscription_request)
# END subscription_input_handling

# This method will be used to handle user inputs for client-side desubscription.
def desubscription_input_handling(rq, item_name, name, client_socket, server_address):
    # Create the message that will be sent to the server for desubscription
    desubscription_request = f"DESUBSCRIBE|{rq}|{item_name}|{name}"

    # Call the DE_SUBSCRIBE method to send the desubscription request to the server
    DE_SUBSCRIBE(client_socket, server_address, desubscription_request)
# END desubscription_input_handling

# This method will be used by the client to subscribe to the server.
def SUBSCRIBE(client_sock, server_addr, message):
    print(f"Sending subscription request to the server at {server_addr[0]}:{str(server_addr[1])}... \n")
    client_sock.sendto(pickle.dumps(message), server_addr)
# END SUBSCRIBE

# This method will be used by the client to desubscribe from the server.
def DE_SUBSCRIBE(client_sock, server_addr, message):
    print(f"Sending desubscription request to the server at {server_addr[0]}:{str(server_addr[1])}... \n")
    client_sock.sendto(pickle.dumps(message), server_addr)
# END DE_SUBSCRIBE