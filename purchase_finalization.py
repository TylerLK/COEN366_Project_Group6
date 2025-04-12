import pickle

def purchase_finalization_handling(global_rq, item_name, completed_auctions, registered_clients, server_socket):
    """
    Handles the purchase finalization process on the server side.

    Args:
        global_rq (int): The global request number.
        item_name (str): The name of the item being finalized.
        completed_auctions (dict): The dictionary of completed auctions.
        buyer_address (tuple): The buyer's address (IP, port).
        seller_address (tuple): The seller's address (IP, port).
        server_socket (socket): The server's TCP socket.
    """
    # Check if the item exists in the completed auctions
    if item_name not in completed_auctions:
        print(f"Item '{item_name}' not found in completed auctions.")
        return

    # Retrieve the auction details
    auction_details = completed_auctions[item_name]
    final_price = auction_details["final_price"]
    buyer_name = auction_details["buyer_name"]
    seller_name = auction_details["seller_name"]
    buyer_address = registered_clients[buyer_name]["ip address"], registered_clients[buyer_name]["tcp_port"]
    seller_address = registered_clients[seller_name]["ip address"], registered_clients[seller_name]["tcp_port"]
    rq = str(global_rq)
    global_rq += 1

    # Create the INFORM_Req message
    inform_req_message = f"INFORM_Req|{rq}|{item_name}|{final_price}"

    # Send INFORM_Req to the buyer
    send_inform_req(server_socket, buyer_address, inform_req_message)
    print(f"Sent INFORM_Req to buyer at {buyer_address}: {inform_req_message}")

    # Receive INFORM_Res from the buyer
    buyer_response = receive_response(server_socket)
    buyer_info = parse_inform_res(buyer_response)
    if not buyer_info:
        print("Failed to process buyer's response.")
        return

    # Send INFORM_Req to the seller
    send_inform_req(server_socket, seller_address, inform_req_message)
    print(f"Sent INFORM_Req to seller at {seller_address}: {inform_req_message}")

    # Receive INFORM_Res from the seller
    seller_response = receive_response(server_socket)
    seller_info = parse_inform_res(seller_response)
    if not seller_info:
        print("Failed to process seller's response.")
        return

    # Process payment
    payment_success, reason = process_payment(buyer_info, seller_info, final_price)

    if not payment_success:
        # Send CANCEL message to both buyer and seller
        cancel_message = f"CANCEL|{rq}|{reason}"
        send_cancel_message(server_socket, buyer_address, cancel_message)
        send_cancel_message(server_socket, seller_address, cancel_message)
        print(f"Transaction canceled: {reason}")
    else:
        # Send Shipping_Info to the seller
        shipping_info_message = f"Shipping_Info|{rq}|{buyer_info['Name']}|{buyer_info['Address']}"
        send_shipping_info(server_socket, seller_address, shipping_info_message)
        print(f"Transaction completed. Sent Shipping_Info to seller at {seller_address}.")

    return global_rq


# Helper Functions

def send_inform_req(server_socket, client_address, message):
    """
    Sends an INFORM_Req message to the client.

    Args:
        server_socket (socket): The server's TCP socket.
        client_address (tuple): The client's address (IP, port).
        message (str): The INFORM_Req message to send.
    """
    print(f"Sending INFORM_Req to client at {client_address[0]}:{client_address[1]}...")
    server_socket.sendto(pickle.dumps(message), client_address)


def receive_response(server_socket):
    """
    Receives a response from a client.

    Args:
        server_socket (socket): The server's TCP socket.

    Returns:
        str: The received response message.
    """
    try:
        data, _ = server_socket.recvfrom(1024)
        return pickle.loads(data)
    except Exception as e:
        print(f"Error receiving response: {e}")
        return None


def parse_inform_res(response):
    """
    Parses the INFORM_Res message.

    Args:
        response (str): The INFORM_Res message.

    Returns:
        dict: A dictionary containing the parsed information.
    """
    try:
        parts = response.split("|")
        if parts[0] != "INFORM_Res" or len(parts) != 6:
            raise ValueError("Invalid INFORM_Res format")
        return {
            "RQ#": parts[1],
            "Name": parts[2],
            "CC#": parts[3],
            "CC_Exp_Date": parts[4],
            "Address": parts[5]
        }
    except Exception as e:
        print(f"Error parsing INFORM_Res: {e}")
        return None


def process_payment(buyer_info, seller_info, final_price):
    """
    Processes the payment between the buyer and seller.

    Args:
        buyer_info (dict): The buyer's information.
        seller_info (dict): The seller's information.
        final_price (float): The final agreed-upon price.

    Returns:
        tuple: (bool, str) indicating success and a reason if failed.
    """
    try:
        # Simulate charging the buyer's credit card
        print(f"Charging {buyer_info['CC#']} for ${final_price}...")
        buyer_charged = True  # Simulate success

        if not buyer_charged:
            return False, "Failed to charge buyer's credit card."

        # Simulate crediting the seller's account (90% of the price)
        seller_credit = final_price * 0.9
        print(f"Crediting {seller_info['CC#']} with ${seller_credit}...")
        seller_credited = True  # Simulate success

        if not seller_credited:
            return False, "Failed to credit seller's account."

        return True, "Payment successful."
    except Exception as e:
        print(f"Error processing payment: {e}")
        return False, str(e)


def send_cancel_message(server_socket, client_address, message):
    """
    Sends a CANCEL message to the client.

    Args:
        server_socket (socket): The server's TCP socket.
        client_address (tuple): The client's address (IP, port).
        message (str): The CANCEL message to send.
    """
    print(f"Sending CANCEL message to client at {client_address[0]}:{client_address[1]}...")
    server_socket.sendto(pickle.dumps(message), client_address)


def send_shipping_info(server_socket, client_address, message):
    """
    Sends a Shipping_Info message to the seller.

    Args:
        server_socket (socket): The server's TCP socket.
        client_address (tuple): The seller's address (IP, port).
        message (str): The Shipping_Info message to send.
    """
    print(f"Sending Shipping_Info to seller at {client_address[0]}:{client_address[1]}...")
    server_socket.sendto(pickle.dumps(message), client_address)