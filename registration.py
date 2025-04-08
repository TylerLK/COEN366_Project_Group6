import pickle


## Server-Side Functions

# This method will allow the server to internally process an incoming reigstration request from a client
def registration_handling(global_rq, registration_request, registered_users, server_socket, client_address):
    # Deconstruct the incoming registration request message
    deconstructed_registration_request = registration_request.split(" ")

    # Update the global "rq" variable if the client's incoming rq value is null
    if deconstructed_registration_request[1] == None:
        deconstructed_registration_request[1] = global_rq
        global_rq += 1

    # Check if the registration request contains the correct information (i.e., 7 segments of information)
    if len(deconstructed_registration_request) != 7:
        # Call the REGISTER_DENIED method to tell the client their registration request was invalid.
        registration_denial_message = f"REGISTER_DENIED {deconstructed_registration_request[1]}: Invalid number of registration parameters. {len(deconstructed_registration_request)} sent, 7 expected... \n"
        REGISTER_DENIED(server_socket, client_address, registration_denial_message)
        print(registration_denial_message)
        return registered_users, global_rq

    else:
        # Create a variable for each piece of the registration request
        message_type, rq, name, role, ip_address, udp_socket, tcp_socket = deconstructed_registration_request

    # Check if the user already exists in the dictionary of pre-existing users
    if name in registered_users:
        # Call the REGISTER_DENIED method to tell the client their registration request was invalid.
        registration_denial_message = f"REGISTER_DENIED {rq}: Client name already in use. \n"
        REGISTER_DENIED(server_socket, client_address, registration_denial_message)
        print(registration_denial_message)
        return registered_users, global_rq

    else:
        # Add the user to the dictionary of registered users
        registered_users[name] = {"rq": rq, "name": name, "role": role, "ip_address": ip_address, "udp_socket": udp_socket, "tcp_socket": tcp_socket}
        
        # print dictionary of registered users
        print(f"Registered Clients: {registered_users} \n")

        # Call the REGISTERED method to acknowledge the client's registration request
        registration_confirmation_message = f"REGISTERED {rq} \n"
        REGISTERED(server_socket, client_address, registration_confirmation_message)
        print(registration_confirmation_message)
        return registered_users, global_rq
# END registration_handling

# This method will allow the server to internally process an incoming deregistration request from a client
def deregistration_handling(global_rq, deregistration_request, registered_users, server_socket, client_address):
    # Deconstruct the incoming deregistration request message
    deconstructed_deregistration_request = deregistration_request.split(" ")

    # Update the global "rq" variable if the client's incoming rq value is null
    if deconstructed_deregistration_request[1] == None:
        deconstructed_deregistration_request[1] = global_rq
        global_rq += 1

    # Check if the registration request contains the correct information (i.e., 3 segments of information)
    if len(deconstructed_deregistration_request) != 3:
        deregistration_denial_message = f"DE_REGISTER_DENIED {deconstructed_deregistration_request[1]}: Invalid number of deregistration parameters. {len(deconstructed_deregistration_request)} sent, 3 expected... \n"
        server_socket.sendto(pickle.dumps(deregistration_denial_message), client_address)
        print(deregistration_denial_message)
        return registered_users, global_rq

    else:
        # Create a variable for each piece of the registration request
        message_type, rq, name = deconstructed_deregistration_request

    # Delete the user from the dictionary of registered users, provided that the user exists
    if name in registered_users:
        deregistration_confirmation_message = f"DE_REGISTERED {rq} \n"
        server_socket.sendto(pickle.dumps(deregistration_confirmation_message), client_address)
        del registered_users[name]
        print(deregistration_confirmation_message)
        return registered_users, global_rq

    else:
        deregistration_denial_message = f"DE_REGISTER_DENIED {rq}: Client name does not exist. \n"
        server_socket.sendto(pickle.dumps(deregistration_denial_message), client_address)
        print(deregistration_denial_message)
        return registered_users, global_rq
# END deregistration_handling

# This method will be used as a positive acknowledgement for a potential client's registration request.
def REGISTERED(server_sock, client_addr, message):
    print(f"Sending registration confirmation to client at {client_addr[0]}:{str(client_addr[1])}... \n")
    server_sock.sendto(pickle.dumps(message), client_addr)
# END REGISTERED

def REGISTER_DENIED(server_sock, client_addr, message):
    print(f"Sending registration denial to client at {client_addr[0]}:{str(client_addr[1])}... \n")
    server_sock.sendto(pickle.dumps(message), client_addr)
# END REGISTER_DENIED


## Client-Side Functions

# This method will be used to handle user inputs for client-side registration.
def registration_input_handling(rq, name, role, ip_address, udp_port, tcp_port, client_socket, server_address):
    # Create the message that will be sent to the server for registration
    registration_request = f"REGISTER {rq} {name} {role} {ip_address} {udp_port} {tcp_port}"

    # Call the REGISTER method to send the registration request to the server
    REGISTER(client_socket, server_address, registration_request)
# END registration_input_handling

# This method will be used to handle user inputs for client-side deregistration.
def deregistration_input_handling(rq, name, client_socket, server_address):
    # Create the message that will be sent to the server for deregistration
    deregistration_request = f"DEREGISTER {rq} {name}"

    # Call the DE_REGISTER method to send the deregistration request to the server
    DE_REGISTER(client_socket, server_address, deregistration_request)
# END deregistration_input_handling

# This method will be used by the client to register to the server.
def REGISTER(client_sock, server_addr, message):
    print(f"Sending registration request to the server at {server_addr[0]}:{str(server_addr[1])}... \n")
    client_sock.sendto(pickle.dumps(message), server_addr)
# END REGISTER

# This method will be used by the client to deregister from the server.
def DE_REGISTER(client_sock, server_addr, message):
    print(f"Sending deregistration request to the server at {server_addr[0]}:{str(server_addr[1])}... \n")
    client_sock.sendto(pickle.dumps(message), server_addr)
# END DE_REGISTER