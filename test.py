class AuctionServer:
    def __init__(self):
        self.users = {}  # Dictionary to store registered users

    def register_user(self, rq_number, name, role, ip_address, udp_port, tcp_port):
        if name in self.users:
            return f"REGISTER-DENIED {rq_number} Name already in use"
        
        self.users[name] = {
            "RQ#": rq_number,
            "Role": role,
            "IP Address": ip_address,
            "UDP Socket#": udp_port,
            "TCP Socket#": tcp_port
        }
        return f"REGISTERED {rq_number}"

    def deregister_user(self, rq_number, name):
        if name in self.users:
            del self.users[name]
            return f"DE-REGISTERED {rq_number}"
        return ""

# Example usage
server = AuctionServer()
print(server.register_user(1, "Alice", "Buyer", "192.168.1.10", 5000, 6000))
print(server.register_user(1, "Alice", "Buyer", "192.168.1.10", 5000, 6000))
print(server.deregister_user(1, "Alice"))
