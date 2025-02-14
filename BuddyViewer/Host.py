import socket
import threading
from pynput import keyboard, mouse

# Function to get local IP address
def get_local_ip():
    try:
        # Create a temporary socket to get the local IP
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_sock.connect(("8.8.8.8", 80))  # Connect to a public DNS server
        local_ip = temp_sock.getsockname()[0]
        temp_sock.close()
        return local_ip
    except Exception:
        return "127.0.0.1"  # Fallback to localhost if unable to determine IP

# Function to find an open port
def find_open_port(start_port=5000, end_port=6000):
    for port in range(start_port, end_port + 1):
        try:
            # Try to bind to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except OSError:
            continue
    raise Exception("No open port found in the specified range.")

# Get local IP and find an open port
HOST = get_local_ip()
PORT = find_open_port()

# Set up socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Host IP: {HOST}")
print(f"Listening on port {PORT}...")
conn, addr = server_socket.accept()
print(f"Connected to {addr}")

# Keyboard event handler
def on_press(key):
    try:
        conn.send(f"Key pressed: {key.char}\n".encode())
    except AttributeError:
        conn.send(f"Special key pressed: {key}\n".encode())

# Mouse event handler
def on_click(x, y, button, pressed):
    if pressed:
        conn.send(f"Mouse clicked at ({x}, {y}) with {button}\n".encode())

# Start listening to keyboard and mouse
keyboard_listener = keyboard.Listener(on_press=on_press)
mouse_listener = mouse.Listener(on_click=on_click)

keyboard_listener.start()
mouse_listener.start()

# Function to handle discovery requests
def handle_discovery():
    discovery_port = 5001  # Separate port for discovery

    # Create a UDP socket for discovery
    discovery_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_sock.bind(('0.0.0.0', discovery_port))

    while True:
        data, addr = discovery_sock.recvfrom(1024)
        if data == b"ViewingBuddyDiscovery":
            # Send the Host's IP and open port
            discovery_sock.sendto(f"{HOST}:{PORT}".encode(), addr)

# Start the discovery thread
discovery_thread = threading.Thread(target=handle_discovery)
discovery_thread.daemon = True
discovery_thread.start()

# Keep the script running
keyboard_listener.join()
mouse_listener.join()