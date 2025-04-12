import pickle

## Server-Side Functions

# This method will be used to manage all relevant dictionaries and clients in the closure of an auction.
def auction_closure_handler(global_rq, item_name, completed_auctions, active_auctions, item_list, bids, registered_clients, server_socket):
    # Check if the item exists
    if item_name in item_list:
        # Check if the item was in an active auction
        if item_name in active_auctions:
            # Check if the auction has concluded
            if active_auctions[item_name]["time_left"] == 0:
                # Assign the rq for all auction closure messages
                rq = global_rq
                global_rq += 1
                
                # Check if the item has any bids
                if item_name in bids:
                    # Gather all important information
                    # The final price of the sold item
                    final_price = active_auctions[item_name]["current_price"]

                    # The name of the client who sold the item
                    seller_name = item_list[item_name]["seller_name"]
                    if seller_name not in registered_clients:
                        print(f"The seller '{seller_name}' does not exist...")
                        return completed_auctions, active_auctions, bids, item_list, global_rq

                    # The name of the client who bought the item, who has the highest bid
                    buyer_name = None
                    # Iterate through the "bids" dictionary to find the buyer name corresponding to the final_price (i.e., highest bid)
                    for client_name, bid in bids[item_name].items():
                        if bid == final_price:
                            buyer_name = client_name
                            break
                    if buyer_name is None:
                        print(f"The buyer '{buyer_name}' does not exist...")
                        return completed_auctions, active_auctions, bids, item_list, global_rq
                    
                    # Send the appropriate messages to the buyer and seller clients
                    # WINNER message to the appriopriate buyer client
                    winner_message = f"WINNER|{rq}|{item_name}|{final_price}|{seller_name}"
                    
                    # Get the buyer's IP address and TCP port number
                    buyer_client_address = (registered_clients[buyer_name]["ip_address"], registered_clients[buyer_name]["tcp_port"])
                    
                    # Send the WINNER message to the buyer client
                    WINNER(server_socket, buyer_client_address, winner_message)

                    # SOLD message to the appriopriate seller client
                    sold_message = f"SOLD|{rq}|{item_name}|{final_price}|{buyer_name}"
                    
                    # Get the seller's IP address and TCP port number
                    seller_client_address = (registered_clients[seller_name]["ip_address"], registered_clients[seller_name]["tcp_port"])
                    
                    # Send the SOLD message to the seller client
                    SOLD(server_socket, seller_client_address, sold_message)

                    # Make sure the auction is listed as completed
                    completed_auctions[item_name] = {
                        "rq": rq,
                        "final_price": final_price,
                        "buyer_name": buyer_name,
                        "seller_name": seller_name
                    }
                
                else:
                    # NON_OFFER message to the appriopriate seller client
                    non_offer_message = f"NON_OFFER|{rq}|{item_name}"
                    
                    # Get the seller's IP address and TCP port number
                    seller_client_address = (registered_clients[seller_name]["ip_address"], registered_clients[seller_name]["tcp_port"])
                    
                    # Send the NON_OFFER message to the seller client
                    NON_OFFER(server_socket, seller_client_address, non_offer_message)
                
                # Make all of the appropriate changes to all relevant dictionaries
                # Remove the item from the listed items
                item_list.pop(item_name, None)

                # Remove the item from the active auctions
                active_auctions.pop(item_name, None)

                # Remove the item from the bids
                bids.pop(item_name, None)
                
                return completed_auctions, active_auctions, bids, item_list, global_rq
            
            else:
                print(f"The auction for the '{item_name}' has not concluded yet...")
                return completed_auctions, active_auctions, bids, item_list, global_rq

        else:
            print(f"The '{item_name}' is not in an active auction...")
            return completed_auctions, active_auctions, bids, item_list, global_rq

    else:
        print(f"The '{item_name}' does not exist...")
        return completed_auctions, active_auctions, bids, item_list, global_rq
# END auction_closure_handler

# This method will be used to notify the buyer who placed the highest bid on an auctioned item.
def WINNER(server_sock, client_addr, message):
    print(f"Sending winning buyer client confirmation at {client_addr[0]}:{str(client_addr[1])}... \n")
    server_sock.sendto(pickle.dumps(message), client_addr)
# END WINNER

# This method will be used to notify the seller of an auctioned item that their item has been sold.
def SOLD(server_sock, client_addr, message):
    print(f"Sending seller client confirmation of sale at {client_addr[0]}:{str(client_addr[1])}... \n")
    server_sock.sendto(pickle.dumps(message), client_addr)
# END SOLD

# This method will be used to notify the seller of an auctioned item that their item has received no bids.
def NON_OFFER(server_sock, client_addr, message):
    print(f"Sending seller client confirmation of non-offer at {client_addr[0]}:{str(client_addr[1])}... \n")
    server_sock.sendto(pickle.dumps(message), client_addr)
# END NON_OFFER