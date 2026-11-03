# ============================================================
#  ipc_bridge.py  --  Packet Tracer <-> Python IPC Bridge
#  CN Chat -- Computer Networks Course Project
#
#  PT 8.2.2 Integration Strategy:
#  ---------------------------------------------------------
#  Packet Tracer 8.x supports "External Application" feature:
#    1. PT opens or listens on a TCP connection for external apps.
#    2. This bridge communicates on BRIDGE_PORT (3900).
#    3. Relays messages between PT and the chat server.
#
#  Flow:
#    [Packet Tracer] <--> TCP:3900 <--> [ipc_bridge.py] <--> TCP:5000 <--> [server.py]
# ============================================================

import socket
import threading
import datetime
import sys
from config import (
    HOST, PORT, BUFFER_SIZE, ENCODING,
    BRIDGE_HOST, BRIDGE_PORT,
    TAG_PT, TAG_SERVER, TAG_MSG,
    SEPARATOR, APP_TITLE
)


# -- Helpers --------------------------------------------------

def timestamp() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def log(msg: str) -> None:
    print(f"[BRIDGE {timestamp()}] {msg}")


# -- Bridge Core -----------------------------------------------

class PTBridge:
    """
    Bidirectional bridge between Packet Tracer (PT) and the Chat Server.

    PT side  : Listens on BRIDGE_PORT for a PT connection.
    Chat side: Connects to the main chat server as a special "PT_Bridge" client.
    """

    def __init__(self):
        self.pt_sock      = None   # Socket to Packet Tracer
        self.server_sock  = None   # Socket to chat server
        self.running      = threading.Event()
        self.running.set()

    # -- Connect to Chat Server --------------------------------

    def connect_to_server(self) -> bool:
        """Establish a connection to the chat server as 'PT_Bridge' client."""
        log(f"Connecting to chat server at {HOST}:{PORT} ...")
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_sock.connect((HOST, PORT))
        except ConnectionRefusedError:
            log(f"[ERROR] Chat server not reachable at {HOST}:{PORT}.")
            log("Make sure server.py is running first!")
            return False

        # Receive username prompt from server
        try:
            data = self.server_sock.recv(BUFFER_SIZE)
            log(f"Server says: {data.decode(ENCODING).strip()}")
        except OSError:
            log("[ERROR] Could not read from server.")
            return False

        # Register with a special bridge username
        username = "PT_Bridge"
        self.server_sock.sendall(username.encode(ENCODING))
        log(f"Registered as '{username}' on chat server.")

        # Receive welcome response
        try:
            welcome = self.server_sock.recv(BUFFER_SIZE)
            log(f"Server welcome: {welcome.decode(ENCODING).strip()}")
        except OSError:
            log("[ERROR] No welcome received from server.")
            return False

        return True

    # -- Listen for PT Connection ------------------------------

    def wait_for_pt(self) -> bool:
        """
        Connect to Packet Tracer IPC listener on BRIDGE_PORT (3900),
        OR start a listener on BRIDGE_PORT if PT script connects outwards.
        """
        # Mode 1: Check if Packet Tracer is already listening on BRIDGE_PORT
        log(f"Probing Packet Tracer IPC listener on {BRIDGE_HOST}:{BRIDGE_PORT} ...")
        probe_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe_sock.settimeout(1.5)
        try:
            probe_sock.connect((BRIDGE_HOST, BRIDGE_PORT))
            probe_sock.settimeout(None)
            self.pt_sock = probe_sock
            log(f"Connected to Packet Tracer on {BRIDGE_HOST}:{BRIDGE_PORT} (PT is Listener)!")
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            probe_sock.close()
            log(f"PT is not listening on {BRIDGE_PORT}. Switching to Bridge Listener mode...")

        # Mode 2: Listen on BRIDGE_PORT and wait for PT or pt_script.py to connect
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind((BRIDGE_HOST, BRIDGE_PORT))
            listener.listen(1)
        except OSError as e:
            log(f"[ERROR] Cannot bind bridge on port {BRIDGE_PORT}: {e}")
            return False

        log(f"Bridge listener started on {BRIDGE_HOST}:{BRIDGE_PORT}")
        log("Waiting for Packet Tracer / pt_script.py to connect...")

        try:
            self.pt_sock, addr = listener.accept()
            log(f"Packet Tracer connected from {addr[0]}:{addr[1]}")
        except OSError as e:
            log(f"[ERROR] Accept failed: {e}")
            return False
        finally:
            listener.close()

        return True

    # -- Relay: PT -> Server ------------------------------------

    def pt_to_server(self) -> None:
        """
        Thread: reads messages from PT and forwards them to the chat server.
        Prefixes messages with TAG_PT so clients know origin.
        """
        while self.running.is_set():
            try:
                data = self.pt_sock.recv(BUFFER_SIZE)
                if not data:
                    log("PT disconnected (PT->Server thread).")
                    self.running.clear()
                    break

                raw = data.decode(ENCODING).strip()
                if not raw:
                    continue

                log(f"  PT -> Server: {raw}")
                self.server_sock.sendall(raw.encode(ENCODING))

            except OSError:
                if self.running.is_set():
                    log("Connection error in PT->Server relay.")
                    self.running.clear()
                break

    # -- Relay: Server -> PT ------------------------------------

    def server_to_pt(self) -> None:
        """
        Thread: reads messages from chat server and forwards them back to PT.
        """
        while self.running.is_set():
            try:
                data = self.server_sock.recv(BUFFER_SIZE)
                if not data:
                    log("Chat server disconnected (Server->PT thread).")
                    self.running.clear()
                    break

                raw = data.decode(ENCODING).strip()
                if not raw:
                    continue

                log(f"  Server -> PT: {raw}")
                self.pt_sock.sendall((raw + "\n").encode(ENCODING))

            except OSError:
                if self.running.is_set():
                    log("Connection error in Server->PT relay.")
                    self.running.clear()
                break

    # -- Main Run ----------------------------------------------

    def run(self) -> None:
        """Start the bridge: connect to server, wait for PT, then relay."""
        print(f"\n{SEPARATOR}")
        print(f"  {APP_TITLE} - IPC Bridge")
        print(f"{SEPARATOR}\n")

        # Step 1: Connect to the chat server first
        if not self.connect_to_server():
            sys.exit(1)

        # Step 2: Wait for Packet Tracer to connect
        if not self.wait_for_pt():
            sys.exit(1)

        log("Bridge is ACTIVE. Relaying between PT and Chat Server.\n")

        # Step 3: Start bidirectional relay threads
        t1 = threading.Thread(target=self.pt_to_server, daemon=True, name="pt-to-server")
        t2 = threading.Thread(target=self.server_to_pt, daemon=True, name="server-to-pt")
        t1.start()
        t2.start()

        # Wait until bridge is stopped
        try:
            t1.join()
            t2.join()
        except KeyboardInterrupt:
            log("\nBridge shutting down...")
            self.running.clear()

        # Cleanup
        for s in [self.pt_sock, self.server_sock]:
            if s:
                try:
                    s.close()
                except OSError:
                    pass

        log("Bridge closed.")


# -- Entry Point -----------------------------------------------

if __name__ == "__main__":
    bridge = PTBridge()
    bridge.run()
