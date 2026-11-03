# ============================================================
#  pt_script.py  --  Packet Tracer Python Script (PT side)
#  CN Chat -- Computer Networks Course Project
#
#  HOW TO USE IN PACKET TRACER 8.2.2:
#  ---------------------------------------------------------
#  1. In PT, click a PC device -> Desktop -> Python Interpreter
#  2. Open this file or paste the code below.
#  3. The script connects to ipc_bridge.py running on the host.
#
#  PT's Python is sandboxed:
#    - socket module has LIMITED support (no threads in PT 8.x)
#    - Use non-blocking + polling loop pattern instead
#    - This script sends and receives via bridge on port 5001
# ============================================================

import socket
import time

# -- Config (syncs with config.py) -----------------------------
try:
    from config import BRIDGE_HOST, BRIDGE_PORT, BUFFER_SIZE, ENCODING
except ImportError:
    BRIDGE_HOST = "127.0.0.1"   # Host running ipc_bridge.py
    BRIDGE_PORT = 3900          # Matches Packet Tracer IPC Options port
    BUFFER_SIZE = 4096
    ENCODING    = "utf-8"

# -- PT Node Identity ------------------------------------------
PT_NODE_NAME = "PT-Router-1"  # Identify which PT node is speaking

# -- Simulated messages (for demo/presentation) ---------------
DEMO_MESSAGES = [
    f"[PT] {PT_NODE_NAME}: Packet received at Router-1, forwarding to switch.",
    f"[PT] {PT_NODE_NAME}: ARP request broadcasted on LAN segment.",
    f"[PT] {PT_NODE_NAME}: TCP SYN received from 192.168.1.10 -> 192.168.1.1:5000",
    f"[PT] {PT_NODE_NAME}: Connection established. Chat session active.",
]


def connect_to_bridge():
    """Connect to the IPC bridge and return the socket."""
    print(f"[PT Script] Connecting to IPC bridge at {BRIDGE_HOST}:{BRIDGE_PORT} ...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((BRIDGE_HOST, BRIDGE_PORT))
    print("[PT Script] Connected to bridge.")
    return s


def run():
    """
    Main PT script logic:
      1. Connect to ipc_bridge.py
      2. Send demo simulation events as chat messages
      3. Receive and display any messages from the chat server
    """
    try:
        sock = connect_to_bridge()
    except Exception as e:
        print(f"[PT Script] ERROR: Could not connect to bridge - {e}")
        return

    # Send demo messages with a small delay between each
    print("[PT Script] Sending simulation events to chat server...")
    for msg in DEMO_MESSAGES:
        try:
            sock.sendall((msg + "\n").encode(ENCODING))
            print(f"[PT Script] Sent: {msg}")
            time.sleep(1.2)   # Delay for dramatic demo effect
        except Exception as e:
            print(f"[PT Script] Send error: {e}")
            break

    # Poll for incoming messages from the chat server (non-blocking)
    sock.setblocking(False)
    print("\n[PT Script] Listening for incoming chat messages (Ctrl+C to stop)...\n")
    try:
        while True:
            try:
                data = sock.recv(BUFFER_SIZE)
                if data:
                    messages = data.decode(ENCODING).strip().split("\n")
                    for m in messages:
                        m = m.strip()
                        if m:
                            print(f"[PT Script] Received: {m}")
            except BlockingIOError:
                pass   # No data yet - normal for non-blocking
            except Exception as e:
                print(f"[PT Script] Recv error: {e}")
                break
            time.sleep(0.3)   # Poll interval

    except KeyboardInterrupt:
        print("\n[PT Script] Stopped by user.")
    finally:
        sock.close()
        print("[PT Script] Connection closed.")


# -- Run -------------------------------------------------------
if __name__ == "__main__":
    run()
