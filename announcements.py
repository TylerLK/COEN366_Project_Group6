import pickle

# Server-Side Functions

# This method will be used to send auction announcements for all items that are up for auction.
# Call this method when: New bid is placed or another update is made to the auction (ie negotation)
def AUCTION_ANNOUNCE(auction_item, active_auctions, listed_items, subscription_list, registered_users, server_socket, client_address):
    # Check if the current item is still actively being auctioned.
    if auction_item in active_auctions:
        # Get the specific item name that is up for auction.
        item_name = auction_item

        # Get specific item details for the auction announcement
        rq = active_auctions[item_name].get("rq")
        item_description = active_auctions[item_name].get("item_description")
        current_price = active_auctions[item_name].get("current_price")
        time_left = active_auctions[item_name].get("duration")

        # Create the auction announcement message
        message = f"AUCTION_ANNOUNCE {rq} {item_name} {item_description} {current_price} {time_left}"

        # Send all the auction announcement to all subscribed clients
        if item_name in subscription_list:
            for client in subscription_list[item_name]:
                # Check if the client is in registered_users
                if client in registered_users:
                    # Get the client's address
                    client_address = registered_users[client].get("address")
                    # Send the message to the client
                    server_socket.sendto(message.encode(), client_address)
                    print(f"AUCTION_ANNOUNCE sent to {client} ({client_address}) for item: {item_name}")
                
                else:
                    print(f"Client {client} not found in registered users. Skipping...")
        # Send the announcement to the seller
        seller_name = listed_items[item_name].get("seller_name")
        if seller_name and seller_name in registered_users:
            seller_address = registered_users[seller_name].get("address")
            server_socket.sendto(message.encode(), seller_address)
            print(f"AUCTION_ANNOUNCE sent to seller {seller_name} ({seller_address}) for item: {item_name}")
        else:
            print(f"Seller {seller_name} not found in registered users.")
        
    else:
        print(f"No clients subscribed to {item_name}. No announcement sent.")
        
# END AUCTION_ANNOUNCE