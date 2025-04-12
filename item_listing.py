import pickle
import time

## Server-Side Functions

# This method will allow the server to internally handle incoming requests for item listing requests.
def list_item_handling(global_rq, listing_request, listed_items, server_socket, client_address):
    try:
        # Deserialize the listing request
        deconstructed_item_listing_request = listing_request.split("|")

        # Update the global "rq" variable if the client's incoming rq value is null
        if deconstructed_item_listing_request[1] == "None":
            deconstructed_item_listing_request[1] = str(global_rq)
            global_rq += 1

        # Validate the listing request format
        if len(deconstructed_item_listing_request) != 6:
            item_listing_denial_message = f"LIST_DENIED|{deconstructed_item_listing_request[1]}|Invalid number of parameters. {len(deconstructed_item_listing_request)} sent, 6 expected. \n"
            LIST_DENIED(server_socket, client_address, item_listing_denial_message)
            print(item_listing_denial_message)
            return listed_items, global_rq

        # Extract item details
        message_type, rq, item_name, item_description, start_price, duration = deconstructed_item_listing_request

        # Check if the item description is not empty
        if item_description == "":
            item_listing_denial_message = f"LIST_DENIED|{rq}|Item description cannot be empty. \n"
            LIST_DENIED(server_socket, client_address, item_listing_denial_message)
            print(item_listing_denial_message)
            return listed_items, global_rq

        # Validate start price and duration
        if not start_price.strip().isdigit():
            item_listing_denial_message = f"LIST_DENIED|{rq}|Start price must be an integer. \n"
            LIST_DENIED(server_socket, client_address, item_listing_denial_message)
            print(item_listing_denial_message)
            return listed_items, global_rq

        if not duration.strip().isdigit():
            item_listing_denial_message = f"LIST_DENIED|{rq}|Duration must be an integer. \n"
            LIST_DENIED(server_socket, client_address, item_listing_denial_message)
            print(item_listing_denial_message)
            return listed_items, global_rq

        start_price = int(start_price)
        duration = int(duration)

        # Check if the item is already listed
        if item_name in listed_items:
            item_listing_denial_message = f"LIST_DENIED|{rq}|Item '{item_name}' is already listed."
            LIST_DENIED(server_socket, client_address, item_listing_denial_message)
            print(item_listing_denial_message)
            return listed_items, global_rq

        # Check auction capacity
        if len(listed_items) >= 200:
            item_listing_denial_message = f"LIST_DENIED|{rq}|Auction capacity reached."
            LIST_DENIED(server_socket, client_address, item_listing_denial_message)
            print(item_listing_denial_message)
            return listed_items, global_rq

        # Add the item to the listed_items dictionary

        start_time = time.time()
        listed_items[item_name]={
            "Item_Name": item_name,
            "Item_Description": item_description,
            "Start_Price": start_price,
            "Duration": duration,
            "Start_Time": start_time,
            "Seller": client_address,
            "Prev_Negotiated": False
        }

        # Send a success response to the client
        item_listing_confirmation_message = f"ITEM_LISTED {rq}"
        ITEM_LISTED(server_socket, client_address, item_listing_confirmation_message)
        print(f"Item '{item_name}' listed successfully.")
        return listed_items, global_rq

    except Exception as e:
        print(f"Error processing listing request: {e}")
        item_listing_denial_message = f"LIST_DENIED|{str(e)}"
        LIST_DENIED(server_socket, client_address, item_listing_denial_message)
        return listed_items, global_rq
# END list_item_handling

# This method will be used as a positive acknowledgement for a seller's listing request.
def ITEM_LISTED(server_sock, client_addr, message):
    print(f"Sending item listing success to client at {client_addr[0]}:{client_addr[1]}...")
    server_sock.sendto(pickle.dumps(message), client_addr)
# END ITEM_LISTED

# This method will be used as a negative acknowledgement for a seller's listing request.
def LIST_DENIED(server_sock, client_addr, message):
    print(f"Sending item listing failure to client at {client_addr[0]}:{client_addr[1]}...")
    server_sock.sendto(pickle.dumps(message), client_addr)
# END LIST_DENIED


## Client-Side Functions

# This method will be used to handle the user input for client-side item listing.
def list_item_input_handling(rq, item_name, item_description, start_price, duration, client_socket, server_address):
    # Create the message that will be sent to the server for item listing
    listing_request = f"LIST_ITEM|{rq}|{item_name}|{item_description}|{start_price}|{duration}"

    # Call the LIST_ITEM method to send the listing request to the server
    LIST_ITEM(client_socket, server_address, listing_request)
# END list_item_input_handling

# This method will be used by a seller to list an item to the server.
def LIST_ITEM(client_sock, server_addr, message):
    print(f"Sending item listing request to the server at {server_addr[0]}:{server_addr[1]}...")
    client_sock.sendto(pickle.dumps(message), server_addr)
# END LIST_ITEM