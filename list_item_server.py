import socket
import pickle
import sqlite3


host = "0.0.0.0"
port = 8888


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print("Server is listening for list items...")
except socket.error as msg:
    print(f"Socket error: {msg}")
    exit()


conn = sqlite3.connect("listed_items.db", check_same_thread=False)
cursor = conn.cursor()
#cursor.execute("DELETE FROM listed_items")


cursor.execute("""
CREATE TABLE IF NOT EXISTS listed_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    item_description TEXT,
    start_price INTEGER,
    duration INTEGER
)
""")
conn.commit()


list_items = []

while True:
    try:
        
        data, addr = s.recvfrom(1024)
        request_data = pickle.loads(data)

       
        request_id = request_data.get("RQ#")
        item_name = request_data.get("Item_Name")
        item_description = request_data.get("Item_Description")
        start_price = request_data.get("Start_Price")
        duration = request_data.get("Duration")

        
        if not str(start_price).isdigit():
            response = { "Server Response ": "LIST_DENIED", "RQ#": request_id,"Reason": "Start price must be an integer"}
            s.sendto(pickle.dumps(response), addr)
            continue  

        if not str(duration).isdigit():
            response = { "Server Response": "LIST_DENIED","RQ#": request_id, "Reason": "Duration must be an integer"}
            s.sendto(pickle.dumps(response), addr)
            continue  
       
        start_price = int(start_price)
        duration = int(duration)

        
        cursor.execute("SELECT COUNT(*) FROM listed_items")
        item_count = cursor.fetchone()[0]

        if item_count >= 5:
            response = { "Server Response": "LIST_DENIED", "RQ#": request_id,"Reason": "Auction capacity reached"}
            s.sendto(pickle.dumps(response), addr)
            continue 

        
        cursor.execute(
            "INSERT INTO listed_items (item_name, item_description, start_price, duration) VALUES (?, ?, ?, ?)",
            (item_name, item_description, start_price, duration)
        )
        conn.commit()

       
        list_items.append({
            "Item_Name": item_name,
            "Item_Description": item_description,
            "Start_Price": start_price,
            "Duration": duration
        })

       
        response = {"Server Response": "ITEM_LISTED", "RQ#": request_id}
        s.sendto(pickle.dumps(response), addr)

    except Exception as e:
        print(f"Error processing request: {e}")
        error_response = {"Server Response": "LIST-DENIED","RQ#": "N/A", "Reason": str(e)}
        s.sendto(pickle.dumps(error_response), addr)


s.close()
conn.close()
