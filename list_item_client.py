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

while True:
    RQ = random.randint(100, 900)  
    
    item_name = input("Enter item name (or type 'exit' to quit): ")
    if item_name.lower() == "exit":
        break

    item_description = input("Enter item description: ")
    start_price = input("Enter start price ($): ")
    duration = input("Enter duration (minutes): ")

 
    request_data = {
        "RQ#": RQ,
        "Item_Name": item_name,
        "Item_Description": item_description,
        "Start_Price": start_price,  
        "Duration": duration,        
    }

    
    print(request_data)
    message = pickle.dumps(request_data)
    s.sendto(message, (SERVER_HOST, SERVER_PORT))

    try:
        
        response, _ = s.recvfrom(1024)  
        response_data = pickle.loads(response) 

        
        print(response_data)

    except Exception as e:
        print(f"Error receiving server response: {e}")


s.close()
