import pickle

## Server-Side Functions
def list_item_handling(listing_request, listed_items, server_socket, client_address):
    """
    Handles item listing requests from clients.
    """
    try:
        # Deserialize the listing request
        deconstructed_request = listing_request.split("|")

        # Validate the listing request format
        if len(deconstructed_request) != 6:
            response_message = f"LIST_DENIED: Invalid number of parameters. {len(deconstructed_request)} sent, 5 expected."
            LIST_DENIED(server_socket, client_address, response_message)
            print(response_message)
            return listed_items

        # Extract item details
        _, rq, item_name, start_price, duration = deconstructed_request

        # Validate start price and duration
        if not start_price.isdigit():
            response_message = f"LIST_DENIED {rq}: Start price must be an integer."
            LIST_DENIED(server_socket, client_address, response_message)
            print(response_message)
            return listed_items

        if not duration.isdigit():
            response_message = f"LIST_DENIED {rq}: Duration must be an integer."
            LIST_DENIED(server_socket, client_address, response_message)
            print(response_message)
            return listed_items

        start_price = int(start_price)
        duration = int(duration)

        # Check if the item is already listed
        if item_name in listed_items:
            response_message = f"LIST_DENIED {rq}: Item '{item_name}' is already listed."
            LIST_DENIED(server_socket, client_address, response_message)
            print(response_message)
            return listed_items

        # Check auction capacity
        if len(listed_items) >= 5:
            response_message = f"LIST_DENIED {rq}: Auction capacity reached."
            LIST_DENIED(server_socket, client_address, response_message)
            print(response_message)
            return listed_items

        # Add the item to the listed_items dictionary
        listed_items[item_name] = {
            "Seller": client_address,
            "Start_Price": start_price,
            "Current_Price": start_price,
            "Duration": duration
        }

        # Send a success response to the client
        response_message = f"ITEM_LISTED {rq}"
        ITEM_LISTED(server_socket, client_address, response_message)
        print(f"Item '{item_name}' listed successfully.")
        return listed_items

    except Exception as e:
        print(f"Error processing listing request: {e}")
        response_message = f"LIST_DENIED: {str(e)}"
        LIST_DENIED(server_socket, client_address, response_message)
        return listed_items


def ITEM_LISTED(server_sock, client_addr, message):
    """
    Sends a positive acknowledgment for a successful item listing.
    """
    print(f"Sending item listing success to client at {client_addr[0]}:{client_addr[1]}...")
    server_sock.sendto(pickle.dumps(message), client_addr)


def LIST_DENIED(server_sock, client_addr, message):
    """
    Sends a negative acknowledgment for a failed item listing.
    """
    print(f"Sending item listing failure to client at {client_addr[0]}:{client_addr[1]}...")
    server_sock.sendto(pickle.dumps(message), client_addr)

# END Server-Side Functions

## Client-Side Functions

def list_item_input_handling(rq, item_name, item_description, start_price, duration, client_socket, server_address):
    """
    Handles user input for listing an item.
    """
    # Create the message that will be sent to the server for item listing
    listing_request = f"LIST_ITEM {rq} {item_name} {start_price} {duration}"

    # Call the LIST_ITEM method to send the listing request to the server
    LIST_ITEM(client_socket, server_address, listing_request)


def LIST_ITEM(client_sock, server_addr, message):
    """
    Sends the item listing request to the server.
    """
    print(f"Sending item listing request to the server at {server_addr[0]}:{server_addr[1]}...")
    client_sock.sendto(pickle.dumps(message), server_addr)

# END Client-Side Functions