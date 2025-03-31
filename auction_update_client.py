import socket
import pickle
import random

SERVER_HOST = "localhost"  
SERVER_PORT = 8888


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Socket created")
except socket.error as msg:
    print(f"Failed to create socket. Error: {msg}")
    exit()

# list item from client
while True:
    RQ = random.randint(100, 900) 
    item_name = input("Enter item name (or type 'exit' to quit): ")
    if item_name.lower() == "exit":
        break

    item_description = input("Enter item description: ")

    
    start_price = input("Enter start price ($): ")
        
        
   
    duration = input("Enter duration (minutes): ")
    type="LIST_ITEM"
        

    request_data = {
        "Type": type,
        "RQ#": RQ,
        "Item_Name": item_name,
        "Item_Description": item_description,
        "Start_Price": start_price,  
        "Duration": duration,        
    }

    print("Sending listing request:", request_data)
    message = pickle.dumps(request_data)
    s.sendto(message, (SERVER_HOST, SERVER_PORT))

   
    response, _ = s.recvfrom(1024)  
    response_data = pickle.loads(response) 
    print("Server Response:", response_data)

    if "ITEM_LISTED" in response_data.values():
        item_listed_response = input("Select [1] to list another item or [2] to wait for negotiations: ")
        if item_listed_response == "1":
            continue

    elif "LIST_DENIED" in response_data.values():
        continue  

    # ---- Wait for a possible negotiation request ----
    try:
        response, _ = s.recvfrom(1024)
        response_data = pickle.loads(response)  
        print("Server Response:", response_data)

        if "NEGOTIATE_REQ" in response_data.values():
            negotiation_choice = input("Enter [1] to Accept or [2] to Reject: ")
            if negotiation_choice == "1":
                negotiation_label = "ACCEPT"
                new_price = input("Enter new price: ")
            else:
                negotiation_label = "REFUSE"
                new_price = "REJECT"

            item_name = response_data["Item_Name"]

            request_data_au = {
                "Server Response": negotiation_label,
                "RQ#": RQ,
                "Item_Name": item_name,
                "New Price": new_price,         
            }

            print("Sending negotiation response:", request_data_au)
            message = pickle.dumps(request_data_au)
            s.sendto(message, (SERVER_HOST, SERVER_PORT))
            
            response, _ = s.recvfrom(1024)
            response_data = pickle.loads(response)  
            print("Server Response:", response_data)

            after_request_response = input("Select [1] to list another item or [2] to wait for a respons: ")
            if after_request_response == "2":
                response, _ = s.recvfrom(1024)
                response_data = pickle.loads(response)  
            print("Server Response:", response_data)
            if after_request_response == "1":
                continue
            

    except Exception as e:
        print(f"Error receiving negotiation request: {e}")

s.close()
