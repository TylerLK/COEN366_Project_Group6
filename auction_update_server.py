import socket
import pickle
import time
import threading

host = "0.0.0.0"
port = 8888

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print("Server is listening for messages...")
except socket.error as msg:
    print(f"Socket error: {msg}")
    exit()

listed_items = []
client_bids = {}

def monitor_auctions():
    """Monitor auctions and send negotiation requests if needed"""
    while True:
        time.sleep(5)
        current_time = time.time()

        for item in listed_items:
            elapsed_time = current_time - item["Start_Time"]
            half_duration = (item["Duration"] * 60) / 2

            if elapsed_time > half_duration and item["Item_Name"] not in client_bids and not item["Prev_Negotiated"]:
                item["Prev_Negotiated"] = True
                print(f"Sending negotiation request for {item['Item_Name']}")
                response = {
                    "Server Response": "NEGOTIATE_REQ",
                    "Item_Name": item["Item_Name"],
                    "Current Price": item["Start_Price"],
                    "Time_Left": (item["Duration"] * 60) - elapsed_time
                }
                s.sendto(pickle.dumps(response), item["Client_Addr"])

threading.Thread(target=monitor_auctions, daemon=True).start()

def negotiation_response(request_data, addr):
    """Handles negotiation acceptance and updates price"""
    try:
        current_time = time.time()
        item_name = request_data.get("Item_Name")
        new_price = int(request_data.get("New Price"))
        request_id = request_data.get("RQ#")

        for item in listed_items:
            if item["Item_Name"] == item_name:
                item["Start_Price"] = new_price
                elapsed_time = current_time - item["Start_Time"]
                break
        else:
            print(f"Item not found: {item_name}")
            return

        print(f"Updated {item_name} price to {new_price}.")

        response = {
            "Server Response": "PRICE_ADJUSTMENT",
            "RQ#": request_id,
            "Item_Name": item_name,
            "New_Price": new_price,
            "Time Left": elapsed_time
        }
        s.sendto(pickle.dumps(response), addr)

    except Exception as e:
        print(f"Error processing negotiation: {e}")

def list_item_response(request_data, addr):
    """Handles new item listings."""
    try:
        request_id = request_data.get("RQ#")
        item_name = request_data.get("Item_Name")
        item_description = request_data.get("Item_Description")
        start_price = request_data.get("Start_Price")
        duration = request_data.get("Duration")

        if not str(start_price).isdigit():
            response = {"Server Response": "LIST_DENIED", "RQ#": request_id, "Reason": "Invalid start price."}
            s.sendto(pickle.dumps(response), addr)
            return

        if not str(duration).isdigit():
            response = {"Server Response": "LIST_DENIED", "RQ#": request_id, "Reason": "Invalid duration."}
            s.sendto(pickle.dumps(response), addr)
            return

        if len(listed_items) >= 100:
            response = {"Server Response": "LIST_DENIED", "RQ#": request_id, "Reason": "Auction capacity reached"}
            s.sendto(pickle.dumps(response), addr)
            return

        start_price = int(start_price)
        duration = int(duration)
        start_time = time.time()

        listed_items.append({
            "Item_Name": item_name,
            "Item_Description": item_description,
            "Start_Price": start_price,
            "Duration": duration,
            "Start_Time": start_time,
            "Client_Addr": addr,
            "Prev_Negotiated": False
        })

        response = {"Server Response": "ITEM_LISTED", "RQ#": request_id}
        s.sendto(pickle.dumps(response), addr)

    except Exception as e:
        print(f"Error processing request: {e}")
        error_response = {"Server Response": "LIST_DENIED", "RQ#": "N/A", "Reason": str(e)}
        s.sendto(pickle.dumps(error_response), addr)

def receive_messages():
    """Continuously listens for incoming messages and processes them."""
    while True:
        try:
            data, addr = s.recvfrom(1024)
            request_data = pickle.loads(data)

            if "ACCEPT" in request_data.values():
                threading.Thread(target=negotiation_response, args=(request_data, addr), daemon=True).start()
            elif "LIST_ITEM" in request_data.values():
                threading.Thread(target=list_item_response, args=(request_data, addr), daemon=True).start()
            else:
                print("Unknown message received:", request_data)

        except Exception as e:
            print(f"Error receiving message: {e}")

# Messenger receiver
threading.Thread(target=receive_messages, daemon=True).start()

while True:
    time.sleep(1)