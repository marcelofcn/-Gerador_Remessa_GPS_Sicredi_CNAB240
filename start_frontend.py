import http.server
import socketserver
import webbrowser
import os
import sys
import socket

# Configuration
PORT = 8000
DIRECTORY = "frontend"

def get_local_ip():
    try:
        # Connect to an external server (doesn't actually send data) to determine the routing interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def start_server():
    # Change to the frontend directory to serve files relative to it
    if os.path.exists(DIRECTORY):
        os.chdir(DIRECTORY)
    else:
        print(f"Error: Directory '{DIRECTORY}' not found.")
        sys.exit(1)

    Handler = http.server.SimpleHTTPRequestHandler
    
    # Allow address reuse to prevent "Address already in use" errors on restart
    socketserver.TCPServer.allow_reuse_address = True

    # Bind to 0.0.0.0 to allow external connections
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        local_ip = get_local_ip()
        
        print(f"-" * 40)
        print(f"Server running at:")
        print(f"   Local:   http://localhost:{PORT}")
        print(f"   Network: http://{local_ip}:{PORT}")
        print(f"-" * 40)
        print("Press Ctrl+C to stop the server.")
        
        # Open the browser (local)
        webbrowser.open(f"http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            httpd.server_close()

if __name__ == "__main__":
    start_server()
