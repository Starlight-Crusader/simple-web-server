import socket
import signal
import sys
import threading
import json
import re

# Define the server's IP address and port
HOST = '127.0.0.1'
PORT = 8080

# Create a socket that uses IPv4 and TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address and port
try:
    server_socket.bind((HOST, PORT))
except:
    PORT = 8081
    server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen(5)
print(f'Server is listening on {HOST}:{PORT}')

# Function to handle client requests
def handle_request(client_socket):

    # Receive and print the client's request data
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f'Received Request:\n{request_data}')

    # Parse the request to get the HTTP method and path
    request_lines = request_data.split('\n')
    request_line = request_lines[0].strip().split()
    # method = request_line[0]
    path = request_line[1]

    # Initialize the response content and status code
    response_content = ''
    status_code = 200

    # Define a simple routing mechanism
    if path == '/':
        response_content = ''
        response_content += "<div class='sections-page'><h5>Website contents:</h5>"
        response_content += "<h5 class='section-name'><a href=http://" + str(HOST) + ':' + str(PORT) + '/home>~ Home</a></h5>'
        response_content += "<h5 class='section-name'><a href=http://" + str(HOST) + ':' + str(PORT) + '/about>~ About</a></h5>'
        response_content += "<h5 class='section-name'><a href=http://" + str(HOST) + ':' + str(PORT) + '/contacts>~ Contacts</a></h5>'
        response_content += "<h5 class='section-name'><a href=http://" + str(HOST) + ':' + str(PORT) + '/products>~ Products</a></h5>'
        response_content += '</div>'
    elif path == '/home':
        response_content = "<div class='simple-section-page'><p>Hello, I'am a web server and my developer is behind you!</p>"
    elif path == '/about':
        response_content = "<div class='simple-section-page'><p>This will be a simple web catalog...</p>"
    elif path == '/contacts':
        response_content = "<div class='simple-section-page'><p>Tel: +000 11 00-11-00</p></div>"
    elif path == '/products':
        with open('products.json') as f:
            data = json.load(f)

        response_content = "<div class='catalog-page'><h5>Products:</h5>"
        for i in range(len(data)):
            print(str(data[i]['name']))
            response_content += '<div><span>' + str(i) + '. </span><a href=http://'+ str(HOST) + ':' + str(PORT) + '/products/' + str(i) + '>' + str(data[i]['name']) + '</a></div>'
            
        response_content += '</div>'
    elif re.match('/products/+', path):
        with open('products.json') as f:
            data = json.load(f)
        
        product_id = 0
        for i in reversed(range((len(path)-1))):
            if path[i] == '/':
                product_id = int(path[i+1:])
                break

        response_content = "<div class='product-page'><h5>Product #" + str(product_id) +' details:</h5>'

        if product_id > len(data) - 1:
            response_content = '404 Not Found'
            status_code = 404
        else:
            for item in data[product_id]:
                response_content += "<b class='key'>" + item + '</b><span>: </span>'
                response_content += "<div class='value'>" + str(data[product_id][item]) + '</div>'

        response_content += '</div>'
    else:
        response_content = '404 Not Found'
        status_code = 404

    # Prepare the HTTP response
    response = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n\n{response_content}'

    # Send the HTTP response
    client_socket.send(response.encode('utf-8'))

    # Close the client socket
    client_socket.close()

# Function to handle Ctrl+C and other signals
def signal_handler(sig, frame):
    print('\nShutting down the server...')
    server_socket.close()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

while True:
    
    # Accept incoming client connections
    client_socket, client_address = server_socket.accept()
    print(f'Accepted connection from {client_address[0]}:{client_address[1]}')

    # Create a thread to handle the client's request
    client_handler = threading.Thread(target=handle_request, args=(client_socket,))
    client_handler.start()