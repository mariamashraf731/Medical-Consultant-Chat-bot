import socket
import threading
import json
import ssl

TIMEOUT_MESSAGE = "!TIMEOUT"                            # TIMEOUT_MESSAGE (if sent, the server will close connection of that client)
TIMEOUT_SECONDS = 30                                    # Number of seconds to wait before disconnect the idle client


HOST = socket.gethostbyname(socket.gethostname())       # Get IP (HOST) of local connected device
PORT = 9090                                             # PORT Number that the socket will listen to
data = open("DataBase.json")           #Server Database
servicedB = json.load(data)             

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # Create a server socket &opening TCP connection
server.bind((HOST, PORT))                                         
server.listen()													# Listen for incoming connections


def start_server():
	"""
    This function starts accepting connections from different clients,
    each client with a specific address(IP & PORT) ,
    uses security on client socket to secure client msgs.

	"""
	print("Starting server connection !!!!!")
	while True:
        # Accept Client Connection
	    client, address = server.accept()
	    # Make the socket connection to the clients secure through SSLSocket
	    connection = ssl.wrap_socket(client,
                               server_side=True,
                               ca_certs="RootCA.pem",
                               certfile="RootCA.crt",
                               keyfile="RootCA.key",
                               cert_reqs=ssl.CERT_OPTIONAL,
                               ssl_version=ssl.PROTOCOL_TLSv1_2)
	    connection.settimeout(TIMEOUT_SECONDS)
	    # Start a new thread for this Client
        # Using Multiple threads to allow Multi-client connections.
        # Each thread handles one client in a separate function
	    thread = threading.Thread(target=handle_recieved_messages, args=(connection,address))
	    thread.start()
	    print(f"connection established :{address[0]}:{address[1]}")

def handle_recieved_messages(client,address): 
    """
	This function checks for recieved msgs form client ,if there is a problem
	in receiving msg the connection is closed after the timeout,
	if the msg is in the database it sends the value of this msg(key)
	to this client otherwise it asks the client to send again.

    :param 
    client: Socket Object (Client Connection)
    address: Address (IP, PORT Number) of the client
    """
    while True:
        try:
            # Receive the message header sent from client side
            # This case for the normal message
            message = client.recv(1024).decode('utf-8')
            print(message) 
            if message in servicedB.keys():
                print(servicedB[message])
                client.send(f"{servicedB[message]}".encode('utf-8'))            # Send Message back to same client
            else:
                client.send(f"Please choose a case scenario!".encode('utf-8'))   # Send Message back to same client
        except socket.timeout:
             # Handle socket.timeout exception (raised by socket.settimeout()) 
            client.send(f"!TIMEOUT".encode('utf-8'))                               # Send Message back to same client
            client.close()                                                         #closing connection
            break
                    
if __name__ == '__main__':
    start_server()
