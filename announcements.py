import pickle

# Server-side Functions
def AUCTION_ANNOUNCE(sock, subscriptions, auction_data, address): #including address?
    """
    Sends auction announcements to subscribed buyers for their selected items.

    Args:
        sock (socket.socket): The server's socket.
        subscriptions (dict): A dictionary mapping item names to lists of subscribed client names.
        auction_data (list): A list of dictionaries containing auction details.
    """
    for auction in auction_data:
        rq = auction.get("rq")  # Request number for the auction
        item_name = auction.get("item_name")
        item_description = auction.get("item_description")
        current_price = auction.get("current_price", auction.get("start_price"))
        time_left = auction.get("duration")

        # Check if there are subscribers for this item
        if item_name in subscriptions:
            for client_name in subscriptions[item_name]:
                # Construct the announcement message
                message = {
                    "type": "AUCTION_ANNOUNCE",
                    "rq": rq,
                    "item_name": item_name,
                    "item_description": item_description,
                    "current_price": current_price,
                    "time_left": time_left
                }

                # Serialize and send the message
                serialized_message = pickle.dumps(message)
                
                #client_address = registered_clients[client_name].get("address") #using format from server.py/ not necessary if passing address
                if address:
                    sock.sendto(serialized_message, address)
                    print(f"AUCTION_ANNOUNCE sent to {client_name} ({address}) for item: {item_name}")