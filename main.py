import gamespy.server
from interface import Interface
import threading

if __name__ == "__main__":
    # Initialize database
    # Create servers
    servers = [
        
    ]
    for server in servers:
        threading.Thread(target=server().start).start()

    app = Interface()
    app.run()
