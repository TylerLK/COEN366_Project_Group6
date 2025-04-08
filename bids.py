import pickle

## Server-Side Functions

# This method will allow the server to internally process an incoming registration request from a client
def bid_handling(bid_request, bids, active_auctions, item_list, server_socket, client_address):
    # Deconstruct the incoming bid request message
    deconstructed_bid_request = bid_request.split(" ")

    # Check if the bid request contains the correct information (i.e., 5 segments of information)
    if len(deconstructed_bid_request) != 5:
        # Call the BID_REJECTED method to tell the client their registration request was invalid.
        bid_rejection_message = f"BID_REJECTED {deconstructed_bid_request[1]}: Invalid number of bid parameters. {len(deconstructed_bid_request)} sent, 5 expected... \n"       
        BID_REJECTED(server_socket, client_address, bid_rejection_message)
        print(bid_rejection_message)
        return bids
    
    else:
        # Create a variable for each piece of the bid request
        message_type, rq, item_name, bid_amount, client_name = deconstructed_bid_request

    # Check if the potential bid is higher than the current bid price of the item
    if item_name not in active_auctions:
        # The item in question is not currently up for auction
        bid_rejection_message = f"BID_REJECTED {rq}: The '{item_name}' item is not currently up for auction... \n"
        BID_REJECTED(server_socket, client_address, bid_rejection_message)
        print(bid_rejection_message)
        return bids
    else:
        current_price = active_auctions[item_name]["current_price"]
        if float(bid_amount) <= current_price:
            # The bid must be rejected by the server
            bid_rejection_message = f"BID_REJECTED {rq}: The bid for {item_name} must be greater than the current price (i.e., {current_price})... \n"
            BID_REJECTED(server_socket, client_address, bid_rejection_message)
            print(bid_rejection_message)
            return bids

    # Check if the item already exists in the dictionary of pre-existing bids
    if item_name not in bids:
        if item_name in active_auctions: # Item is up for auction
            # Check the starting price of the item, since there are no current bids for this item
            starting_price = item_list[item_name]["start_price"]

            # Check if the bid amount is valid
            if float(bid_amount) <= starting_price:
                bid_rejection_message = f"BID_REJECTED {rq}: The bid for {item_name} must be greater than the starting price (i.e., {starting_price})... \n"
                BID_REJECTED(server_socket, client_address, bid_rejection_message)
                print(bid_rejection_message)
                return bids

            else:
                # Create a new key-value pair for this item in the dictionary of bids
                bids[item_name] = {
                    client_name : bid_amount
                }

                # Call the REGISTERED method to acknowledge the client's registration request
                bid_acceptance_message = f"BID_ACCEPTED {rq} \n"
                BID_ACCEPTED(server_socket, client_address, bid_acceptance_message)
                print(bid_acceptance_message)
                return bids
        else:
            # The item in question is not currently up for auction
            bid_rejection_message = f"BID_REJECTED {rq}: The '{item_name}' item is not currently up for auction... \n"
            BID_REJECTED(server_socket, client_address, bid_rejection_message)
            print(bid_rejection_message)
            return bids

    # Check if the user has already made a bid for this item
    if client_name in bids[item_name]:
        # Update the client's bid on this item
        bids[item_name][client_name] = bid_amount

        # Call the REGISTERED method to acknowledge the client's registration request
        bid_acceptance_message = f"BID_ACCEPTED {rq} \n"
        BID_ACCEPTED(server_socket, client_address, bid_acceptance_message)
        print(bid_acceptance_message)
        return bids
    
    else:
        # Add the user to the dictionary of registered users
        bids[item_name][client_name] = bid_amount

        # Call the REGISTERED method to acknowledge the client's registration request
        bid_acceptance_message = f"BID_ACCEPTED {rq} \n"
        BID_ACCEPTED(server_socket, client_address, bid_acceptance_message)
        print(bid_acceptance_message)
        return bids
# END bid_handling

# This method will be used as a positive acknowledgement for a client's bid request.
def BID_ACCEPTED(server_sock, client_addr, message):
    print(f"Sending bid acceptance to client at {client_addr[0]}:{str(client_addr[1])}... \n")
    server_sock.sendto(pickle.dumps(message), client_addr)
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
    bid_request = f"BID {rq} {item_name} {bid_amount} {client_name}"

    # Call the DE_REGISTER method to send the deregistration request to the server
    BID(client_socket, server_address, bid_request)
# END deregistration_input_handling

# This method will be used by the client to register to the server.
def BID(client_sock, server_addr, message):
    print(f"Sending bid request to the server at {server_addr[0]}:{str(server_addr[1])}... \n")
    client_sock.sendto(pickle.dumps(message), server_addr)
# END BID