import gamespy.server

import threading

if __name__ == "__main__":
    # Initialize database
    # Create servers
    servers = [
        
    ]
    for server in servers:
        threading.Thread(target=server().start).start()
