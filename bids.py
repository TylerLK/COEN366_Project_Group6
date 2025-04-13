import pickle

from announcements import AUCTION_ANNOUNCE, BID_UPDATE_ANNOUNCE
## Server-Side Functions

# This method will allow the server to internally process an incoming registration request from a client
def bid_handling(bid_request, bids, active_auctions, subscription_list, registered_users, item_list, server_socket, client_address):
    # Deconstruct the incoming bid request message
    deconstructed_bid_request = bid_request.split("|")

    # Update the global "rq" variable if the client's incoming rq value is null
    if deconstructed_bid_request[1] == "None":
        deconstructed_bid_request[1] = active_auctions[deconstructed_bid_request[2]]["rq"]

    # Check if the bid request contains the correct information (i.e., 5 segments of information)
    if len(deconstructed_bid_request) != 5:
        # Call the BID_REJECTED method to tell the client their registration request was invalid.
        bid_rejection_message = f"BID_REJECTED|{deconstructed_bid_request[1]}|Invalid number of bid parameters. {len(deconstructed_bid_request)} sent, 5 expected... \n"       
        BID_REJECTED(server_socket, client_address, bid_rejection_message)
        print(bid_rejection_message)
        return bids, active_auctions
    
    else:
        # Create a variable for each piece of the bid request
        message_type, rq, item_name, bid_amount, client_name = deconstructed_bid_request

    # Check if the potential bid is higher than the current bid price of the item
    if item_name not in active_auctions:
        # The item in question is not currently up for auction
        bid_rejection_message = f"BID_REJECTED|{rq}|The '{item_name}' item is not currently up for auction... \n"
        BID_REJECTED(server_socket, client_address, bid_rejection_message)
        print(bid_rejection_message)
        return bids,active_auctions
    else:
        current_price = active_auctions[item_name]["current_price"]
        if float(bid_amount) <= current_price:
            # The bid must be rejected by the server
            bid_rejection_message = f"BID_REJECTED|{rq}|The bid for {item_name} must be greater than the current price (i.e., {current_price})... \n"
            BID_REJECTED(server_socket, client_address, bid_rejection_message)
            print(bid_rejection_message)
            return bids,active_auctions

    # Check if the item already exists in the dictionary of pre-existing bids
    if item_name not in bids:
        if item_name in active_auctions: # Item is up for auction
            # Check the starting price of the item, since there are no current bids for this item
            starting_price = item_list[item_name]["Start_Price"]

            # Check if the bid amount is valid
            if int(bid_amount) <= starting_price:
                bid_rejection_message = f"BID_REJECTED|{rq}|The bid for {item_name} must be greater than the starting price (i.e., {starting_price})... \n"
                BID_REJECTED(server_socket, client_address, bid_rejection_message)
                print(bid_rejection_message)
                return bids,active_auctions

            else:
                # Create a new key-value pair for this item in the dictionary of bids
                bids[item_name] = {
                    client_name : bid_amount
                }
                active_auctions[item_name]["current_price"] = bid_amount

                # Call the REGISTERED method to acknowledge the client's registration request
                bid_acceptance_message = f"BID_ACCEPTED|{rq} \n"
                BID_ACCEPTED(item_name, active_auctions, subscription_list, item_list, registered_users, server_socket, bid_amount, client_name,  client_address, bid_acceptance_message)
                print(bid_acceptance_message)
                return bids,active_auctions

        else:
            # The item in question is not currently up for auction
            bid_rejection_message = f"BID_REJECTED|{rq}|The '{item_name}' item is not currently up for auction... \n"
            BID_REJECTED(server_socket, client_address, bid_rejection_message)
            print(bid_rejection_message)
            return bids,active_auctions
    # Check if the user has already made a bid for this item
    if client_name in bids[item_name]:
        # Update the client's bid on this item
        bids[item_name][client_name] = bid_amount

        # Call the REGISTERED method to acknowledge the client's registration request
        bid_acceptance_message = f"BID_ACCEPTED|{rq} \n"
        BID_ACCEPTED(item_name, active_auctions, subscription_list, item_list, registered_users, server_socket, bid_amount, client_name, client_address, bid_acceptance_message)
        print(bid_acceptance_message)
        
        return bids,active_auctions
    
    else:
        # Add the user to the dictionary of registered users
        bids[item_name][client_name] = bid_amount
        active_auctions[item_name]["current_price"] = bid_amount
        # Call the REGISTERED method to acknowledge the client's registration request
        bid_acceptance_message = f"BID_ACCEPTED|{rq} \n"
        BID_ACCEPTED(item_name, active_auctions, subscription_list, item_list, registered_users, server_socket, bid_amount, client_name,  client_address, bid_acceptance_message)
        print(bid_acceptance_message)
        
        return bids,active_auctions
# END bid_handling
                
# This method will be used as a positive acknowledgement for a client's bid request.
def BID_ACCEPTED(item_name, active_auctions, subscription_list, item_list, registered_users, server_socket, bid_amount, client_name, client_address, message):
    print(f"Sending bid acceptance to client at {client_address[0]}:{str(client_address[1])}... \n")

    server_socket.sendto(pickle.dumps(message), client_address)
    
    AUCTION_ANNOUNCE(active_auctions, item_list, subscription_list, registered_users, server_socket, client_address)
    BID_UPDATE_ANNOUNCE(item_name, active_auctions, subscription_list, item_list, registered_users, server_socket, bid_amount, client_name)
                
    
# END BID_ACCEPTED

# This method will be used as a negative acknowledgement for a client's bid request.
def BID_REJECTED(server_sock, client_addr, message):
    print(f"Sending bid rejection to client at {client_addr[0]}:{str(client_addr[1])}... \n")
    server_sock.sendto(pickle.dumps(message), client_addr)
# END BID_REJECTED

## Client-Side Functions

# This method will be used to handle user inputs for client-side deregistration.
def bid_input_handling(rq, item_name, bid_amount, client_name, client_socket, server_address):
    # Create the message that will be sent to the server for deregistration
    bid_request = f"BID|{rq}|{item_name}|{bid_amount}|{client_name}"

    # Call the BID method to send the bid request to the server
    BID(client_socket, server_address, bid_request)
# END deregistration_input_handling

# This method will be used by the client to register to the server.
def BID(client_sock, server_addr, message):
    print(f"Sending bid request to the server at {server_addr[0]}:{str(server_addr[1])}... \n")
    client_sock.sendto(pickle.dumps(message), server_addr)
# END BID