# Server-Side Functions
# TODO: Implement these functions and add descriptions to all of them

# This method will allow the server to internally process an incoming reigstration request from a client
def registration_handling(registration_request, registered_users):
    # Deconstruct the incoming registration request message
    deconstructed_registration_request = registration_request.split(" ")

    # Check if the registration request contains the correct information (i.e., 7 segments of information)
    if len(deconstructed_registration_request) != 7:
        return f"INVALID COMMAND: {deconstructed_registration_request[1]}"
    else:
        # Create a variable for each piece of the registration request
        message_type, rq, name, role, ip_address, udp_socket, tcp_socket = deconstructed_registration_request

    # Check if the user already exists in the dictionary of pre-existing users
    if name in registered_users:
        return f"{message_type} request denied: {rq}.  Client name already in use."
    else:
        # Add the user to the dictionary of registered users
        registered_users[name] = {"rq": rq, "name": name, "role": role, "ip_address": ip_address, "udp_socket": udp_socket, "tcp_socket": tcp_socket}
        return f"REGISTERED: {rq}"

# This method will allow the server to internally process an incoming deregistration request from a client
def deregistration_handling(deregistration_request, registered_users):
    # Deconstruct the incoming deregistration request message
    deconstructed_deregistration_request = deregistration_request.split(" ")

    # Check if the registration request contains the correct information (i.e., 7 segments of information)
    if len(deconstructed_deregistration_request) != 3:
        return f"INVALID COMMAND: {deconstructed_deregistration_request[1]}"
    else:
        # Create a variable for each piece of the registration request
        message_type, rq, name = deconstructed_deregistration_request
    
    # Delete the user from the dictionary of registered users, provided that the user exists
    if name in registered_users:
        del registered_users[name]
    else:
        return f"{message_type} request denied: {rq}. Client name does not exist."

def REGISTERED():
    print("Registered")

def REGISTER_DENIED():
    print("Registered Denied")

# Client-Side Functions
# TODO: Move all client-side functions for registration into this module
def REGISTER():
    print("Registering")

def DE_REGISTER():
    print("Deregistering")