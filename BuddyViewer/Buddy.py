import socket

# Function to discover the Host's IP address and port
def discover_host():
    # Broadcast a message to find the Host
    broadcast_ip = "255.255.255.255"  # Broadcast address
    broadcast_port = 5001             # Separate port for discovery

    # Create a UDP socket for broadcasting
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Timeout after 5 seconds

    # Send a discovery message
    discovery_message = b"ViewingBuddyDiscovery"
    sock.sendto(discovery_message, (broadcast_ip, broadcast_port))

    # Wait for a response from the Host
    try:
        data, addr = sock.recvfrom(1024)
        if data.startswith(b"ViewingBuddyHost"):
            host_ip, host_port = data.decode().split(":")
            return host_ip, int(host_port)
    except socket.timeout:
        print("Host not found. Make sure the Host script is running.")
        return None, None
    finally:
        sock.close()

# Discover the Host's IP address and port
HOST, PORT = discover_host()
if not HOST or not PORT:
    exit()

# Set up socket client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print(f"Connected to Host at {HOST}:{PORT}. Waiting for events...")

# Log events to a file
with open("event_log.txt", "a") as log_file:
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        log_file.write(data)
        print(data, end='')